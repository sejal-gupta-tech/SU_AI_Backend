from pydantic import BaseModel
from typing import Optional, Literal

class PhotoshootRequest(BaseModel):
    product_id: str

    style: Literal[
        "studio",
        "lifestyle",
        "model",
        "festival",
        "marketplace"
    ] = "studio"

    background: Optional[str] = "clean"

    model: Optional[str] = None

    pose: Optional[str] = None

    language: str = "English"

    additional_instruction: Optional[str] = None

class PhotoshootResponse(BaseModel):
    success: bool
    message: str
    data: dict
