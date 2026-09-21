from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime

class AIUsageStats(BaseModel):
    posts_generated: Optional[int] = None
    reels_generated: Optional[int] = None
    images_generated: Optional[int] = None
    photoshoots_generated: Optional[int] = None
    total_generations: Optional[int] = None

class DashboardStats(BaseModel):
    total_users: int
    total_businesses: int
    active_subscriptions: Optional[int] = None
    credits_used: Optional[int] = None

class RecentRegistration(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: Optional[datetime] = None

class RecentBusiness(BaseModel):
    id: str
    name: str
    owner_id: str
    category: str
    location: str
    created_at: Optional[datetime] = None

class AdminDashboardOverview(BaseModel):
    stats: DashboardStats
    ai_usage: AIUsageStats
    recent_registrations: List[RecentRegistration]
    recent_businesses: List[RecentBusiness]
