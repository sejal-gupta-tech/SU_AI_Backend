from pydantic import BaseModel
from typing import Optional

class BusinessCreate(BaseModel):
    name: str
    category: str
    location: str
    website: Optional[str] = None
    instagram: Optional[str] = None
    target_customer: Optional[str] = None
    preferred_language: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    description: Optional[str] = None

class BusinessResponse(BusinessCreate):
    id: str
    owner_id: str
