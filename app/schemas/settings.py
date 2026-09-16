from typing import Optional
from pydantic import BaseModel

class UserSettingsUpdate(BaseModel):
    theme: Optional[str] = None
    email_notifications: Optional[bool] = None
    language: Optional[str] = None

class UserSettingsResponse(BaseModel):
    user_id: str
    theme: str
    email_notifications: bool
    language: str
