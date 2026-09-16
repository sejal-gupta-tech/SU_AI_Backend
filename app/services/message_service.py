from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException

from app.schemas.message import MessageCreate, MessageUpdate

def serialize_message(msg):
    return {
        "id": str(msg["_id"]),
        "business_id": str(msg["business_id"]),
        "customer_name": msg.get("customer_name"),
        "message": msg.get("message"),
        "platform": msg.get("platform"),
        "status": msg.get("status"),
        "reply": msg.get("reply"),
        "created_at": msg.get("created_at"),
        "updated_at": msg.get("updated_at"),
    }

async def create_message(db, business_id: str, data: MessageCreate):
    collection = db["messages"]
    msg_data = data.model_dump(exclude_none=True)
    now = datetime.now(timezone.utc)
    
    msg_data["business_id"] = ObjectId(business_id)
    msg_data["created_at"] = now
    msg_data["updated_at"] = now
    
    result = await collection.insert_one(msg_data)
    msg = await collection.find_one({"_id": result.inserted_id})
    return serialize_message(msg)

async def get_messages(db, business_id: str):
    collection = db["messages"]
    cursor = collection.find({"business_id": ObjectId(business_id)})
    
    messages = []
    async for msg in cursor:
        messages.append(serialize_message(msg))
        
    return messages

async def get_message(db, business_id: str, message_id: str):
    if not ObjectId.is_valid(message_id):
        raise HTTPException(status_code=400, detail="Invalid message ID")
        
    msg = await db["messages"].find_one({
        "_id": ObjectId(message_id),
        "business_id": ObjectId(business_id)
    })
    
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    return serialize_message(msg)

async def update_message(db, business_id: str, message_id: str, data: MessageUpdate):
    if not ObjectId.is_valid(message_id):
        raise HTTPException(status_code=400, detail="Invalid message ID")
        
    update_data = data.model_dump(exclude_none=True)
    
    existing = await db["messages"].find_one({
        "_id": ObjectId(message_id),
        "business_id": ObjectId(business_id)
    })
    
    if not existing:
        raise HTTPException(status_code=404, detail="Message not found")
        
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db["messages"].update_one(
        {"_id": ObjectId(message_id), "business_id": ObjectId(business_id)},
        {"$set": update_data}
    )
    
    updated = await db["messages"].find_one({
        "_id": ObjectId(message_id),
        "business_id": ObjectId(business_id)
    })
    
    return serialize_message(updated)

async def delete_message(db, business_id: str, message_id: str):
    if not ObjectId.is_valid(message_id):
        raise HTTPException(status_code=400, detail="Invalid message ID")
        
    result = await db["messages"].delete_one({
        "_id": ObjectId(message_id),
        "business_id": ObjectId(business_id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
        
    return {"success": True, "message": "Message deleted successfully"}
