from typing import List, Optional

from pydantic import BaseModel


class ImageGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    batch_size: int = 1
    seed: Optional[int] = None


class ImageEditRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    images: List[str] = []
    width: int = 1024
    height: int = 1024
    batch_size: int = 1
    seed: Optional[int] = None


class ImageGenerateResult(BaseModel):
    success: bool
    duration: float = None
    images: List[str] = []
    prompt_id: Optional[str] = None
    metadata: dict = {}


class MediaTypeContent(BaseModel):
    data: Optional[str] = None
    mimeType: Optional[str] = None
    type: str
    text: Optional[str] = None


class MediaTypeContentResult(BaseModel):
    content: List[MediaTypeContent]
    structured_content: ImageGenerateResult
