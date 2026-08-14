from ai_creative_sdk.providers.base import BaseImageProvider
from ai_creative_sdk.types import ImageGenerateRequest


class CommercialImageSkill:
    def __init__(self, provider: BaseImageProvider):
        self.provider = provider

    async def generate(self, prompt: str):
        request = ImageGenerateRequest(prompt=prompt)
        result = await self.provider.generate(request)
        return result

