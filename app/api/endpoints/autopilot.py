from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.security import get_current_user
from app.core.database import get_database
from typing import Dict, List, Any, Optional
from bson import ObjectId

router = APIRouter(
    prefix="/autopilot",
    tags=["Autopilot"]
)

async def _resolve_business_id(current_user, db) -> Optional[str]:
    """
    Return the business_id for the current user.
    If the token already has one, use it.
    Otherwise, look it up from the DB (covers dev mock users and newly registered users).
    """
    business_id = current_user.get("business_id")
    if business_id:
        return str(business_id)
    
    # Fallback: look up business by owner_id
    user_id = str(current_user.get("id") or current_user.id)
    business = await db["businesses"].find_one({"owner_id": user_id})
    return str(business["_id"]) if business else None


@router.get("/queue")
async def get_autopilot_queue(
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get upcoming and past scheduled posts for this user."""
    business_id = await _resolve_business_id(current_user, db)
    if not business_id:
        return {"success": True, "data": [], "message": "No business found. Please create a business first."}
        
    cursor = db["post_queue"].find({"business_id": business_id}).sort("scheduled_for", 1)
    queue = []
    async for item in cursor:
        item["id"] = str(item.pop("_id"))
        # Serialize datetimes for JSON
        if "scheduled_for" in item and hasattr(item["scheduled_for"], "isoformat"):
            item["scheduled_for"] = item["scheduled_for"].isoformat()
        if "created_at" in item and hasattr(item["created_at"], "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
        queue.append(item)
        
    return {"success": True, "data": queue}


@router.get("/settings")
async def get_autopilot_settings(
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Get current autopilot settings (enabled flag + schedule) for the business."""
    business_id = await _resolve_business_id(current_user, db)
    if not business_id:
        return {"success": True, "data": {"auto_publish_enabled": False, "autopilot_schedule": {}}}

    business = await db["businesses"].find_one({"_id": ObjectId(business_id)})
    if not business:
        return {"success": True, "data": {"auto_publish_enabled": False, "autopilot_schedule": {}}}

    return {
        "success": True,
        "data": {
            "auto_publish_enabled": business.get("auto_publish_enabled", False),
            "autopilot_schedule": business.get("autopilot_schedule", {})
        }
    }


@router.post("/toggle")
async def toggle_autopilot(
    enabled: bool = Body(..., embed=True),
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Turn Instagram Autopilot ON or OFF."""
    business_id = await _resolve_business_id(current_user, db)
    if not business_id:
        return {"success": False, "message": "No business found. Please create a business profile first."}
        
    await db["businesses"].update_one(
        {"_id": ObjectId(business_id)},
        {"$set": {"auto_publish_enabled": enabled}},
        upsert=False
    )
    
    return {"success": True, "message": f"Autopilot is now {'ON 🚀' if enabled else 'OFF'}"}


@router.put("/schedule")
async def update_autopilot_schedule(
    schedule: Dict[str, List[str]] = Body(..., embed=True),
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Update weekly schedule. e.g. {'Monday': ['11:00'], 'Wednesday': ['19:00']}"""
    business_id = await _resolve_business_id(current_user, db)
    if not business_id:
        return {"success": False, "message": "No business found. Please create a business profile first."}
        
    await db["businesses"].update_one(
        {"_id": ObjectId(business_id)},
        {"$set": {"autopilot_schedule": schedule}}
    )
    
    return {"success": True, "message": "Schedule updated successfully"}


@router.delete("/queue/{item_id}")
async def cancel_scheduled_post(
    item_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    """Cancel a pending post in the queue."""
    if not ObjectId.is_valid(item_id):
        return {"success": False, "message": "Invalid item ID"}
        
    business_id = await _resolve_business_id(current_user, db)
    if not business_id:
        return {"success": False, "message": "No business found"}

    result = await db["post_queue"].delete_one({
        "_id": ObjectId(item_id),
        "business_id": str(business_id),
        "status": "pending"
    })
    
    if result.deleted_count == 0:
        return {"success": False, "message": "Queue item not found or already processed"}
        
    return {"success": True, "message": "Scheduled post cancelled"}

