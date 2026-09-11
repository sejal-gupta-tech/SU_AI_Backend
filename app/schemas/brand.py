from pydantic import BaseModel
from typing import Optional

class BrandKitCreate(BaseModel):
    brand_name: str
    logo_url: Optional[str] = None
    tagline: Optional[str] = None
    primary_color: str
    secondary_color: str
    accent_color: str
    heading_font: str
    body_font: str
    brand_voice: str
    target_audience: Optional[str] = None
    language: Optional[str] = None

class BrandKitResponse(BrandKitCreate):
    id: str
    business_id: str
