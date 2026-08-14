from abc import ABC, abstractmethod

from ai_creative_sdk.types import ImageGenerateRequest, ImageGenerateResult


class BaseImageProvider(ABC):
    @abstractmethod
    async def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        pass
