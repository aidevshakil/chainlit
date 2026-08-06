import os
import asyncio
from google import genai
from google.genai import types

class GeminiService:
    """Optimized & scalable service wrapper for Google Gemini API."""

    def __init__(self, api_key: str = None):
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key or key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY is not configured.")
        self.client = genai.Client(api_key=key)

    async def stream_chat(self, prompt: str):
        """Asynchronously streams response text from Gemini 2.5 Flash."""
        def _call():
            return self.client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=prompt,
            )
        
        response_stream = await asyncio.to_thread(_call)
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text

    async def generate_image(self, prompt: str, aspect_ratio: str = "1:1") -> bytes:
        """Asynchronously generates an image via Imagen 3."""
        def _call():
            return self.client.models.generate_images(
                model="imagen-3.0-generate-002",
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio=aspect_ratio,
                )
            )

        result = await asyncio.to_thread(_call)
        if result and result.generated_images:
            return result.generated_images[0].image.image_bytes
        raise RuntimeError("No image returned from Imagen 3.")
