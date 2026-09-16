from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException
from app.schemas.review import ReviewCreate, ReviewUpdate

def serialize_review(rev):
    return {
        "id": str(rev["_id"]),
        "business_id": str(rev["business_id"]),
        "customer_name": rev.get("customer_name"),
        "rating": rev.get("rating"),
        "review_text": rev.get("review_text"),
        "status": rev.get("status"),
        "reply": rev.get("reply"),
        "created_at": rev.get("created_at"),
        "updated_at": rev.get("updated_at"),
    }

async def create_review(db, business_id: str, data: ReviewCreate):
    collection = db["reviews"]
    rev_data = data.model_dump(exclude_none=True)
    now = datetime.now(timezone.utc)
    
    rev_data["business_id"] = ObjectId(business_id)
    rev_data["created_at"] = now
    rev_data["updated_at"] = now
    
    result = await collection.insert_one(rev_data)
    rev = await collection.find_one({"_id": result.inserted_id})
    return serialize_review(rev)

async def get_reviews(db, business_id: str):
    collection = db["reviews"]
    cursor = collection.find({"business_id": ObjectId(business_id)})
    
    reviews = []
    async for rev in cursor:
        reviews.append(serialize_review(rev))
        
    return reviews

async def get_review(db, business_id: str, review_id: str):
    if not ObjectId.is_valid(review_id):
        raise HTTPException(status_code=400, detail="Invalid review ID")
        
    rev = await db["reviews"].find_one({
        "_id": ObjectId(review_id),
        "business_id": ObjectId(business_id)
    })
    
    if not rev:
        raise HTTPException(status_code=404, detail="Review not found")
        
    return serialize_review(rev)

async def update_review(db, business_id: str, review_id: str, data: ReviewUpdate):
    if not ObjectId.is_valid(review_id):
        raise HTTPException(status_code=400, detail="Invalid review ID")
        
    update_data = data.model_dump(exclude_none=True)
    
    existing = await db["reviews"].find_one({
        "_id": ObjectId(review_id),
        "business_id": ObjectId(business_id)
    })
    
    if not existing:
        raise HTTPException(status_code=404, detail="Review not found")
        
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db["reviews"].update_one(
        {"_id": ObjectId(review_id), "business_id": ObjectId(business_id)},
        {"$set": update_data}
    )
    
    updated = await db["reviews"].find_one({
        "_id": ObjectId(review_id),
        "business_id": ObjectId(business_id)
    })
    
    return serialize_review(updated)

async def delete_review(db, business_id: str, review_id: str):
    if not ObjectId.is_valid(review_id):
        raise HTTPException(status_code=400, detail="Invalid review ID")
        
    result = await db["reviews"].delete_one({
        "_id": ObjectId(review_id),
        "business_id": ObjectId(business_id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
        
    return {"success": True, "message": "Review deleted successfully"}
