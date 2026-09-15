from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1)
    goal: Optional[str] = None
    targetAudience: Optional[str] = None
    platforms: list[str] = Field(default_factory=list)
    budget: Optional[str] = None
    duration: Optional[str] = None
    productId: Optional[str] = None
    objective: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    goal: Optional[str] = None
    targetAudience: Optional[str] = None
    platforms: Optional[list[str]] = None
    budget: Optional[str] = None
    duration: Optional[str] = None
    productId: Optional[str] = None
    objective: Optional[str] = None


class CampaignResponse(CampaignCreate):
    id: str
    userId: str
    businessId: str

    strategy: Optional[Any] = None
    contentStrategy: Optional[Any] = None
    suggestedPosts: Optional[list[str]] = None
    suggestedReels: Optional[list[str]] = None
    adCopy: Optional[str] = None
    callToAction: Optional[str] = None
    postingSchedule: Optional[str] = None

    createdAt: datetime
    updatedAt: datetime
