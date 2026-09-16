from app.schemas.settings import UserSettingsUpdate

async def get_user_settings(db, user_id: str):
    collection = db["settings"]
    settings = await collection.find_one({"user_id": user_id})
    if not settings:
        return {
            "user_id": user_id,
            "theme": "light",
            "email_notifications": True,
            "language": "en"
        }
    return {
        "user_id": user_id,
        "theme": settings.get("theme", "light"),
        "email_notifications": settings.get("email_notifications", True),
        "language": settings.get("language", "en")
    }

async def update_user_settings(db, user_id: str, data: UserSettingsUpdate):
    collection = db["settings"]
    update_data = data.model_dump(exclude_none=True)
    
    if not update_data:
        return await get_user_settings(db, user_id)
        
    await collection.update_one(
        {"user_id": user_id},
        {"$set": update_data},
        upsert=True
    )
    
    return await get_user_settings(db, user_id)
