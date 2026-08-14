from typing import List, Optional

from pydantic import BaseModel


class ImageGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    width: int = 1024
    height: int = 1024
    batch_size: int = 1
    seed: Optional[int] = None


class ImageGenerateResult(BaseModel):
    success: bool
    images: List[str] = []
    prompt_id: Optional[str] = None
    metadata: dict = {}
