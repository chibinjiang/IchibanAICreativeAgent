from __future__ import annotations

import base64
import time
from pathlib import Path
from uuid import uuid4

from openai import AsyncOpenAI

from ai_creative_sdk.log_config import logger
from ai_creative_sdk.providers.base import BaseImageProvider
from ai_creative_sdk.types import ImageGenerateRequest, ImageGenerateResult


class OpenAIImageProvider(BaseImageProvider):

    OUTPUT_DIR = "assets/outputs/gpt_images"

    def __init__(self, base_url: str, api_key: str, model: str = "gpt-image-2"):
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )
        self.model = model

    async def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        output_dir = Path(self.OUTPUT_DIR)
        output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
        start_time = time.time()
        logger.info(f"Request for GPT: {request}")
        response = await self.client.images.generate(
            model=self.model,
            prompt=request.prompt,
            size=f'{request.width}x{request.height}' if request.width and request.height else 'auto',
            quality="auto",
            n=request.batch_size,
        )
        paths = []
        logger.info(f"Return From GPT: {response}")
        for image in response.data:
            path = output_dir / f"{uuid4().hex}.{response.output_format}"
            path.write_bytes(base64.b64decode(image.b64_json))
            paths.append(path)
        duration = time.time() - start_time
        return ImageGenerateResult(
            success=True,
            images=paths,
            duration=duration,
            prompt_id=response._request_id,
            metadata=response.usage,
        )