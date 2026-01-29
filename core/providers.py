from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import base64
from io import BytesIO
from PIL import Image

@dataclass
class GenResult:
    images: List[Image.Image]
    raw: Dict[str, Any]

class ImageProvider:
    name: str = "base"
    def generate(self, api_key: str, model: str, prompt: str, size: str="1024x1024", n: int=1, transparent: bool=False) -> GenResult:
        raise NotImplementedError

class OpenAIProvider(ImageProvider):
    name = "OpenAI"
    def generate(self, api_key: str, model: str, prompt: str, size: str="1024x1024", n: int=1, transparent: bool=False) -> GenResult:
        # Docs: https://platform.openai.com/docs/api-reference/images
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        kwargs = {"model": model, "prompt": prompt, "n": n, "size": size}
        # GPT image models support background=transparent + output_format
        if transparent:
            kwargs["background"] = "transparent"
            kwargs["output_format"] = "png"
        resp = client.images.generate(**kwargs)
        imgs = []
        raw = resp.model_dump() if hasattr(resp, "model_dump") else dict(resp)
        for item in resp.data:
            b64 = getattr(item, "b64_json", None) or item.get("b64_json")
            img_bytes = base64.b64decode(b64)
            imgs.append(Image.open(BytesIO(img_bytes)).convert("RGBA"))
        return GenResult(images=imgs, raw=raw)

class GeminiImagenProvider(ImageProvider):
    name = "Gemini (Imagen)"
    def generate(self, api_key: str, model: str, prompt: str, size: str="1K", n: int=1, transparent: bool=False) -> GenResult:
        # Docs: https://ai.google.dev/gemini-api/docs/imagen
        # Uses google-genai SDK (python-genai). The Imagen API currently supports specific params.
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        # size for Imagen is via image_size ('1K' or '2K') and aspect_ratio; we map to defaults
        config = types.GenerateImagesConfig(
            number_of_images=int(n),
            image_size=size,  # '1K' or '2K'
        )
        resp = client.models.generate_images(model=model, prompt=prompt, config=config)
        imgs = []
        # response.generated_images -> generated_image.image.image_bytes (base64)
        for gi in resp.generated_images:
            # The SDK returns bytes base64-encoded string in some contexts; handle both
            b = gi.image.image_bytes
            if isinstance(b, str):
                img_bytes = base64.b64decode(b)
            else:
                img_bytes = b
            imgs.append(Image.open(BytesIO(img_bytes)).convert("RGBA"))
        raw = resp.model_dump() if hasattr(resp, "model_dump") else {"generated_images": len(resp.generated_images)}
        return GenResult(images=imgs, raw=raw)

PROVIDERS = {
    "OpenAI": OpenAIProvider(),
    "Gemini": GeminiImagenProvider(),
}
