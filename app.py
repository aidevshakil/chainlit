import os
import sitecustomize  # Apply Python 3.14 AnyIO/Sniffio compatibility patches
from dotenv import load_dotenv
import chainlit as cl
from services.flux import FluxService

load_dotenv()

# Preset prompt dictionary for clean action routing
PRESETS = {
    "preset_cyberpunk": "A futuristic cyberpunk city skyline with neon lights at night, ultra-detailed, 8k resolution octane render",
    "preset_robot": "A high-tech friendly AI robot helper with glowing cyan eyes, sleek metallic finish, 3D render",
    "preset_sunset": "A serene watercolor landscape painting of majestic snowy mountains during golden hour sunset",
    "preset_nebula": "An epic cosmic nebula with shimmering stars and distant glowing planets in deep space",
}


@cl.on_chat_start
async def start():
    """Initialize session state, AI service connection, and welcome interface."""
    cl.user_session.set("aspect_ratio", "1:1")
    try:
        service = FluxService()
        cl.user_session.set("service", service)
        status = "🟢 **Connected to black-forest-labs/FLUX.1-schnell**"
    except ValueError as err:
        cl.user_session.set("service", None)
        status = f"⚠️ **HF_TOKEN Missing**: {err}"

    actions = [
        cl.Action(name="preset_cyberpunk", payload={"value": "cyberpunk"}, label="🌆 Cyberpunk City"),
        cl.Action(name="preset_robot", payload={"value": "robot"}, label="🤖 3D AI Robot"),
        cl.Action(name="preset_sunset", payload={"value": "sunset"}, label="🎨 Sunset Watercolor"),
        cl.Action(name="preset_nebula", payload={"value": "nebula"}, label="🌌 Cosmic Nebula"),
        cl.Action(name="toggle_aspect", payload={"value": "toggle"}, label="📐 Aspect Ratio (1:1 / 16:9)"),
    ]
    await cl.Message(
        content=f"### ⚡ FLUX.1-schnell AI Studio Initialized\n\n> {status}\n\nSelect a preset below, type your prompt directly, or use `/image <prompt>` to generate state-of-the-art AI artwork!",
        actions=actions
    ).send()


@cl.action_callback("preset_cyberpunk")
@cl.action_callback("preset_robot")
@cl.action_callback("preset_sunset")
@cl.action_callback("preset_nebula")
async def handle_preset(action: cl.Action):
    """Handle click events for preset image prompts."""
    prompt = PRESETS.get(action.name)
    if prompt:
        await generate_image_ui(prompt)


@cl.action_callback("toggle_aspect")
async def toggle_aspect(action: cl.Action):
    """Toggle aspect ratio setting in user session."""
    current = cl.user_session.get("aspect_ratio", "1:1")
    new_ratio = "16:9" if current == "1:1" else "1:1"
    cl.user_session.set("aspect_ratio", new_ratio)
    await cl.Message(
        content=f"📐 **Canvas Aspect Ratio updated to** `{new_ratio}`"
    ).send()


async def generate_image_ui(prompt: str):
    """UI helper to handle step tracking and inline image display."""
    service: FluxService = cl.user_session.get("service")
    if not service:
        return await cl.Message(content="⚠️ Please configure `HF_TOKEN` in your `.env` file.").send()

    aspect_ratio = cl.user_session.get("aspect_ratio", "1:1")
    async with cl.Step(name="FLUX.1-schnell Studio", type="tool") as step:
        step.input = f"Prompt: '{prompt}' | Aspect: {aspect_ratio}"
        try:
            image_bytes = await service.generate_image(prompt, aspect_ratio)
            img = cl.Image(content=image_bytes, name="flux_artwork.jpg", display="inline")
            step.output = "✨ Image rendered successfully via FLUX.1-schnell."

            await cl.Message(
                content=f"🎨 **FLUX.1 Generated Artwork** • `{aspect_ratio}`\n\n*\"{prompt}\"*",
                elements=[img]
            ).send()
        except Exception as e:
            step.output = f"Error: {e}"
            await cl.Message(content=f"❌ **Image Generation Failed:** {e}").send()


@cl.on_message
async def on_message(msg: cl.Message):
    """Route user text prompts to FLUX.1-schnell image generation."""
    service: FluxService = cl.user_session.get("service")
    if not service:
        return await cl.Message(content="⚠️ Please configure `HF_TOKEN` in your `.env` file.").send()

    text = msg.content.strip()
    prompt = text.split(" ", 1)[1] if " " in text and text.lower().startswith(("/image", "/draw")) else text
    await generate_image_ui(prompt)
