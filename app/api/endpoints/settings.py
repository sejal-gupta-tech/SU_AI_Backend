from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.database import get_database
from app.schemas.settings import UserSettingsUpdate
from app.services.settings_service import get_user_settings, update_user_settings

router = APIRouter()

@router.get("")
async def get_settings(
    current_user=Depends(get_current_user),
    db=Depends(get_database)
):
    user_id = str(current_user.get("id") or current_user.get("_id"))
    settings = await get_user_settings(db, user_id)
    return {"success": True, "data": settings}

@router.put("")
async def update_settings(
    data: UserSettingsUpdate,
    current_user=Depends(get_current_user),
    db=Depends(get_database)
):
    user_id = str(current_user.get("id") or current_user.get("_id"))
    settings = await update_user_settings(db, user_id, data)
    return {"success": True, "message": "Settings updated", "data": settings}
