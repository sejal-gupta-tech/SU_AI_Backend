from typing import Optional
from app.models.base import MongoBaseModel

class Message(MongoBaseModel):
    user_id: Optional[str] = None
    business_id: Optional[str] = None
    customer_name: str
    message: str
    platform: str
    status: str = "New"
    reply: Optional[str] = None
