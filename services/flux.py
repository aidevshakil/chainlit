import os
import io
import asyncio
from typing import Tuple
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from huggingface_hub.errors import HfHubHTTPError


class FluxService:
    """Service wrapper for Hugging Face FLUX.1-schnell text-to-image model."""

    def __init__(self, api_key: str = None):
        load_dotenv()
        key = api_key or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
        if not key or key in ["your_huggingface_api_key_here", "your_hf_token_here"]:
            raise ValueError("HF_TOKEN is not configured in .env file.")
        self.key = key
        self.model = "black-forest-labs/FLUX.1-schnell"

    def _get_dimensions(self, aspect_ratio: str) -> Tuple[int, int]:
        """Convert aspect ratio string to width & height in pixels."""
        if aspect_ratio == "16:9":
            return (1024, 576)
        elif aspect_ratio == "9:16":
            return (576, 1024)
        elif aspect_ratio == "4:3":
            return (1024, 768)
        else:  # default "1:1"
            return (1024, 1024)

    async def generate_image(self, prompt: str, aspect_ratio: str = "1:1") -> bytes:
        """Asynchronously generates an image using black-forest-labs/FLUX.1-schnell via Hugging Face Inference API."""
        width, height = self._get_dimensions(aspect_ratio)

        def _call():
            # Use Hugging Face auto-routing client with provider fallback support
            try:
                client = InferenceClient(token=self.key)
                image = client.text_to_image(
                    prompt=prompt,
                    model=self.model,
                    width=width,
                    height=height,
                )
            except Exception:
                client = InferenceClient(model=self.model, token=self.key, provider="together")
                image = client.text_to_image(
                    prompt=prompt,
                    width=width,
                    height=height,
                )

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=95)
            return buffer.getvalue()

        try:
            return await asyncio.to_thread(_call)
        except HfHubHTTPError as err:
            err_str = str(err)
            if "403" in err_str or "permissions" in err_str.lower():
                raise PermissionError(
                    "🔑 **Hugging Face Token Permission Error (403 Forbidden)**:\n\n"
                    "Your Hugging Face token lacks the **Inference Provider** permission.\n\n"
                    "**How to fix:**\n"
                    "1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)\n"
                    "2. Click **Create new token** → **Fine-grained** (or **Write**)\n"
                    "3. Under **User permissions** -> **Inference**, check ✅ **Make calls to Inference Providers**\n"
                    "4. Copy the new token into your `.env` file (`HF_TOKEN=hf_...`)"
                ) from err
            raise err
