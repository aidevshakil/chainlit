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
        """Asynchronously streams response text with automatic model fallback."""
        models = ["gemini-2.0-flash", "gemini-flash-latest"]
        last_error = None
        
        for model_name in models:
            try:
                def _call(m=model_name):
                    return self.client.models.generate_content_stream(
                        model=m,
                        contents=prompt,
                    )
                response_stream = await asyncio.to_thread(_call)
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                last_error = e
                if "429" in str(e) or "404" in str(e):
                    continue
                raise e

        if last_error:
            if "429" in str(last_error):
                yield "⏳ **Rate Limit Reached**: Free tier API quota was hit. Please wait ~10 seconds and send your message again."
            else:
                raise last_error

    async def generate_image(self, prompt: str, aspect_ratio: str = "1:1") -> bytes:
        """Asynchronously generates an image via Imagen 3."""
        image_models = ["imagen-3.0-generate-002", "imagen-3.0-fast-generate-001"]
        last_err = None
        
        for m in image_models:
            try:
                def _call(mod=m):
                    return self.client.models.generate_images(
                        model=mod,
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
            except Exception as e:
                last_err = e
                if "404" in str(e) or "429" in str(e):
                    continue
                raise e
        
        if last_err:
            if "404" in str(last_err):
                raise RuntimeError(
                    "Imagen 3 requires a paid API plan or Vertex AI project on Google Cloud. "
                    "Free-tier API keys on Google AI Studio only support Gemini chat & code models. "
                    "To generate images, enable billing on your Google AI Studio API key at https://aistudio.google.com!"
                )
            elif "429" in str(last_err):
                raise RuntimeError("⏳ Rate limit reached for image generation. Please wait a few seconds and try again.")
            else:
                raise last_err
        raise RuntimeError("No image returned from Imagen 3.")
