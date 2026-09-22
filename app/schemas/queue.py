from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.base import PyObjectId

class QueueItemCreate(BaseModel):
    content_id: str
    scheduled_for: datetime
    platform: str = "instagram"
    status: str = "pending"  # pending, published, failed
    error_message: Optional[str] = None
    
class QueueItemResponse(QueueItemCreate):
    id: PyObjectId
    business_id: str
    user_id: str
    created_at: datetime
