import os
import sniffio
import anyio._backends._asyncio as _asyncio

# Python 3.14 compatibility patch for AnyIO / Starlette / Sniffio / EngineIO
_orig_sniffio = sniffio.current_async_library
def _patched_sniffio():
    try:
        return _orig_sniffio()
    except Exception:
        return "asyncio"
sniffio.current_async_library = _patched_sniffio

try:
    import asyncio.timeouts
    _orig_timeout_enter = asyncio.timeouts.Timeout.__aenter__
    async def _patched_timeout_enter(self):
        try:
            return await _orig_timeout_enter(self)
        except RuntimeError as e:
            if "Timeout should be used inside a task" in str(e):
                self._state = asyncio.timeouts._State.ENTERED
                return self
            raise
    asyncio.timeouts.Timeout.__aenter__ = _patched_timeout_enter

    _orig_timeout_exit = asyncio.timeouts.Timeout.__aexit__
    async def _patched_timeout_exit(self, exc_type, exc_val, exc_tb):
        try:
            return await _orig_timeout_exit(self, exc_type, exc_val, exc_tb)
        except (AssertionError, RuntimeError):
            self._state = asyncio.timeouts._State.EXITED
            return False
    asyncio.timeouts.Timeout.__aexit__ = _patched_timeout_exit
except Exception:
    pass

try:
    import anyio._backends._asyncio as _asyncio

    _orig_find_root_task = _asyncio.find_root_task
    def _patched_find_root_task():
        task = _orig_find_root_task()
        if task is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            class _DummyRootTask:
                _loop = loop
                def add_done_callback(self, *args, **kwargs): pass
                def remove_done_callback(self, *args, **kwargs): pass
            return _DummyRootTask()
        return task
    _asyncio.find_root_task = _patched_find_root_task

    _orig_worker_thread_init = _asyncio.WorkerThread.__init__
    def _patched_worker_thread_init(self, root_task, workers, idle_workers):
        if root_task is None:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            class _DummyRootTask:
                _loop = loop
                def add_done_callback(self, *args, **kwargs): pass
                def remove_done_callback(self, *args, **kwargs): pass
            root_task = _DummyRootTask()
        return _orig_worker_thread_init(self, root_task, workers, idle_workers)
    _asyncio.WorkerThread.__init__ = _patched_worker_thread_init

    _orig_get = _asyncio._task_states.get
    def _patched_get(key, default=None):
        if key is None:
            return default
        try:
            return _orig_get(key, default)
        except TypeError:
            return default
    _asyncio._task_states.get = _patched_get

    _orig_contains = _asyncio._task_states.__contains__
    def _patched_contains(key):
        if key is None:
            return False
        try:
            return _orig_contains(key)
        except TypeError:
            return False
    _asyncio._task_states.__contains__ = _patched_contains

    _orig_cancel_scope_enter = _asyncio.CancelScope.__enter__
    def _patched_cancel_scope_enter(self):
        try:
            return _orig_cancel_scope_enter(self)
        except (TypeError, AssertionError):
            self._host_task = None
            self._active = True
            return self
    _asyncio.CancelScope.__enter__ = _patched_cancel_scope_enter

    _orig_cancel_scope_exit = _asyncio.CancelScope.__exit__
    def _patched_cancel_scope_exit(self, exc_type, exc_val, exc_tb):
        try:
            return _orig_cancel_scope_exit(self, exc_type, exc_val, exc_tb)
        except (RuntimeError, TypeError, AttributeError, AssertionError):
            return False
    _asyncio.CancelScope.__exit__ = _patched_cancel_scope_exit

    _orig_acquire_nowait = _asyncio.CapacityLimiter.acquire_on_behalf_of_nowait
    def _patched_acquire_nowait(self, borrower):
        try:
            return _orig_acquire_nowait(self, borrower)
        except Exception:
            return
    _asyncio.CapacityLimiter.acquire_on_behalf_of_nowait = _patched_acquire_nowait

    _orig_release = _asyncio.CapacityLimiter.release_on_behalf_of
    def _patched_release(self, borrower):
        try:
            return _orig_release(self, borrower)
        except Exception:
            return
    _asyncio.CapacityLimiter.release_on_behalf_of = _patched_release

except Exception:
    pass

from dotenv import load_dotenv
import chainlit as cl
from services.gemini import GeminiService

load_dotenv()

# Preset prompt dictionary for clean action routing
PRESETS = {
    "preset_cyberpunk": "A futuristic cyberpunk city skyline with neon lights at night",
    "preset_robot": "A high-tech friendly AI robot helper rendering in 3D octane style",
    "preset_sunset": "A serene watercolor landscape painting of mountains during sunset",
}


@cl.on_chat_start
async def start():
    """Initialize session state, AI service connection, and welcome interface."""
    cl.user_session.set("aspect_ratio", "1:1")
    try:
        service = GeminiService()
        cl.user_session.set("service", service)
        status = "✅ **Gemini API Connected**"
    except ValueError as err:
        cl.user_session.set("service", None)
        status = f"⚠️ **Configuration Warning**: {err}"

    actions = [
        cl.Action(name="preset_cyberpunk", payload={"value": "cyberpunk"}, label="🌆 Cyberpunk"),
        cl.Action(name="preset_robot", payload={"value": "robot"}, label="🤖 AI Robot"),
        cl.Action(name="preset_sunset", payload={"value": "sunset"}, label="🎨 Sunset"),
        cl.Action(name="toggle_aspect", payload={"value": "toggle"}, label="📐 Toggle Aspect (1:1 / 16:9)"),
    ]
    await cl.Message(
        content=f"# 🚀 Gemini AI Assistant & Image Generator\n\n{status}\n\nChat naturally or type `/image <prompt>` to generate artwork!",
        actions=actions
    ).send()


@cl.action_callback("preset_cyberpunk")
@cl.action_callback("preset_robot")
@cl.action_callback("preset_sunset")
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
    await cl.Message(content=f"📐 **Aspect Ratio set to `{new_ratio}`** for future images.").send()


async def generate_image_ui(prompt: str):
    """UI helper to handle step tracking and inline image display."""
    service: GeminiService = cl.user_session.get("service")
    if not service:
        return await cl.Message(content="⚠️ Please configure `GEMINI_API_KEY` in `.env`.").send()

    aspect_ratio = cl.user_session.get("aspect_ratio", "1:1")
    async with cl.Step(name="Imagen 3 Engine", type="tool") as step:
        step.input = f"Prompt: '{prompt}' ({aspect_ratio})"
        try:
            image_bytes = await service.generate_image(prompt, aspect_ratio)
            img = cl.Image(content=image_bytes, name="generated.jpg", display="inline")
            step.output = "Image generated successfully."
            await cl.Message(content=f"✨ **Generated:** *\"{prompt}\"*", elements=[img]).send()
        except Exception as e:
            step.output = f"Error: {e}"
            await cl.Message(content=f"❌ **Image Generation Failed:** {e}").send()


@cl.on_message
async def on_message(msg: cl.Message):
    """Route user messages between text streaming and image generation."""
    service: GeminiService = cl.user_session.get("service")
    if not service:
        return await cl.Message(content="⚠️ Please configure `GEMINI_API_KEY` in `.env`.").send()

    text = msg.content.strip()
    
    # Route to image generation if command or keywords detected
    is_image = text.lower().startswith(("/image", "/draw")) or any(k in text.lower() for k in ["generate image", "draw "])
    if is_image:
        prompt = text.split(" ", 1)[1] if " " in text and text.lower().startswith(("/image", "/draw")) else text
        return await generate_image_ui(prompt)

    # Stream text response for normal chat
    response = cl.Message(content="")
    await response.send()
    try:
        async for chunk in service.stream_chat(text):
            await response.stream_token(chunk)
        await response.update()
    except Exception as e:
        await cl.Message(content=f"❌ **Chat Error:** {e}").send()
