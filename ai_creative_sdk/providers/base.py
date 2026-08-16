from abc import ABC, abstractmethod

from ai_creative_sdk.types import ImageGenerateRequest, ImageGenerateResult


class BaseImageProvider(ABC):

    @abstractmethod
    async def generate(self, request: ImageGenerateRequest) -> ImageGenerateResult:
        """
        文生图
        """
        raise NotImplementedError

    # @abstractmethod
    # async def edit(self, ImageEditRequest) -> ImageGenerateResult:
    #     """
    #     图片编辑。
    #     """
    #     raise NotImplementedError