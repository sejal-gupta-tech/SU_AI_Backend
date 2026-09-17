from pydantic import BaseModel
from typing import Optional, Literal

class AdRequest(BaseModel):
    product_id: Optional[str] = None
    content_id: Optional[str] = None
    platform: Literal[
        "instagram",
        "facebook",
        "google",
        "whatsapp",
    ]
    objective: Literal[
        "product_promotion",
        "sales",
        "awareness",
        "engagement",
        "lead_generation",
    ]
    language: str = "English"
    target_audience: Optional[str] = None
    additional_instruction: Optional[str] = None
    cta: Optional[str] = "Shop Now"

class AdResponse(BaseModel):
    success: bool
    message: str
    data: dict
