from fastapi import APIRouter, Depends
from typing import List, Any
from app.core.security import require_admin, CurrentUser
from app.core.database import get_database
from app.schemas.admin import AdminDashboardOverview, DashboardStats, AIUsageStats
from app.services.admin_dashboard_service import AdminDashboardService

router = APIRouter()

@router.get("/dashboard/overview", response_model=AdminDashboardOverview)
async def get_dashboard_overview(current_user: CurrentUser = Depends(require_admin)):
    total_users = await AdminDashboardService.get_total_users()
    total_businesses = await AdminDashboardService.get_total_businesses()
    recent_users = await AdminDashboardService.get_recent_users()
    recent_businesses = await AdminDashboardService.get_recent_businesses()
    ai_usage = await AdminDashboardService.get_ai_usage()
    
    return AdminDashboardOverview(
        stats=DashboardStats(
            total_users=total_users,
            total_businesses=total_businesses,
            active_subscriptions=None,
            credits_used=None
        ),
        ai_usage=AIUsageStats(**ai_usage),
        recent_registrations=recent_users,
        recent_businesses=recent_businesses
    )

@router.get("/users")
async def get_all_users(current_user: CurrentUser = Depends(require_admin)) -> Any:
    db = get_database()
    users_cursor = db["users"].find({}, {"hashed_password": 0})
    users = await users_cursor.to_list(length=100)
    # Convert ObjectId to string for JSON serialization
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users

@router.get("/businesses")
async def get_all_businesses(current_user: CurrentUser = Depends(require_admin)) -> Any:
    db = get_database()
    businesses_cursor = db["businesses"].find({})
    businesses = await businesses_cursor.to_list(length=100)
    for business in businesses:
        business["id"] = str(business["_id"])
        del business["_id"]
    return businesses
