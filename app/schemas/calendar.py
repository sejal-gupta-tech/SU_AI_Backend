from pydantic import BaseModel
from typing import List, Optional

class CalendarRequest(BaseModel):
    product_id: str
    prompt: str

class DayPlan(BaseModel):
    day_number: int
    content_type: str
    caption: str
    hashtags: str
    visual_direction: str
    generated_image_url: Optional[str] = None

class CalendarResponse(BaseModel):
    success: bool
    message: str
    data: List[DayPlan]
