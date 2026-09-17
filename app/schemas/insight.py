from pydantic import BaseModel
from typing import Optional

class DashboardStats(BaseModel):
    total_posts: int = 0
    total_campaigns: int = 0
    total_products: int = 0
    total_reviews: int = 0
    total_messages: int = 0

class EngagementStats(BaseModel):
    likes: int = 0
    comments: int = 0
    shares: int = 0
    reach: int = 0

class DashboardInsights(BaseModel):
    stats: DashboardStats
    engagement: EngagementStats
