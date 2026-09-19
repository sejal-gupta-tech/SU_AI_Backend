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
    whatsapp_phone_id: Optional[str] = None
    whatsapp_token: Optional[str] = None
    ig_access_token: Optional[str] = None
    ig_account_id: Optional[str] = None
    fb_access_token: Optional[str] = None
    fb_page_id: Optional[str] = None
    linkedin_author_id: Optional[str] = None
    linkedin_access_token: Optional[str] = None

from app.models.base import PyObjectId

class BusinessResponse(BusinessCreate):
    id: PyObjectId
    owner_id: str

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    instagram: Optional[str] = None
    target_customer: Optional[str] = None
    preferred_language: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    description: Optional[str] = None
    whatsapp_phone_id: Optional[str] = None
    whatsapp_token: Optional[str] = None
    ig_access_token: Optional[str] = None
    ig_account_id: Optional[str] = None
    fb_access_token: Optional[str] = None
    fb_page_id: Optional[str] = None
    linkedin_author_id: Optional[str] = None
    linkedin_access_token: Optional[str] = None
