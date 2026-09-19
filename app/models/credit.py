from datetime import datetime
from typing import Optional
from app.models.base import MongoBaseModel

class Subscription(MongoBaseModel):
    user_id: str
    plan: str = "FREE"
    credits_total: int = 5
    credits_remaining: int = 5
    status: str = "active"

class CreditTransaction(MongoBaseModel):
    user_id: str
    action: str
    credits: int
    balance_after: int
