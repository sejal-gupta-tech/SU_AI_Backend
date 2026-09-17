from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from app.models.base import PyObjectId

class MessageCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    platform: str
    status: str = "New"

class MessageUpdate(BaseModel):
    status: Optional[str] = None
    reply: Optional[str] = None

class MessageResponse(BaseModel):
    id: PyObjectId
    business_id: str
    customer_name: str
    message: str
    platform: str
    status: str
    reply: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
