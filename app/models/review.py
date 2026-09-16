from typing import Optional
from app.models.base import MongoBaseModel

class Review(MongoBaseModel):
    user_id: Optional[str] = None
    business_id: Optional[str] = None
    customer_name: str
    rating: int
    review_text: str
    status: str = "New"
    reply: Optional[str] = None
