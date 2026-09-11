from typing import Optional
from app.models.base import MongoBaseModel

class Business(MongoBaseModel):
    owner_id: str
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
