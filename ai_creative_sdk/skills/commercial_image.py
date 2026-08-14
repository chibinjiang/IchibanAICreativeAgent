from ai_creative_sdk.providers.base import BaseImageProvider
from ai_creative_sdk.types import ImageGenerateRequest


class CommercialImageSkill:
    def __init__(self, provider: BaseImageProvider):
        self.provider = provider

    async def generate(
        self,
        prompt: str,
        negative_prompt: str = '',
        width: int = 1024,
        height: int = 1024,
        batch_size: int = 1,
        seed: int | None = None,
    ):
        request = ImageGenerateRequest(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            batch_size=batch_size,
            seed=seed,
        )
        result = await self.provider.generate(request)
        return result

