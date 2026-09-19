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

async def generate_ai_reply(db, business_id: str, review_id: str):
    from app.ai.factory import AIProviderFactory
    
    # 1. Fetch the review
    rev = await get_review(db, business_id, review_id)
    rating = rev.get("rating", 5)
    review_text = rev.get("review_text", "")
    customer_name = rev.get("customer_name", "Customer")
    
    # 2. Setup Prompt
    system_prompt = "You are a customer support AI for a business. Respond directly to the customer's review."
    prompt = f"""
Customer Name: {customer_name}
Rating: {rating}/5 Stars
Review: {review_text}

IMPORTANT RULES FOR REPLY:
- If Rating is 4 or 5 stars, reply ONLY with something similar to: "Thank you so much for your valuable feedback! ❤ We look forward to serving you again."
- If Rating is 1, 2, or 3 stars, reply ONLY with something similar to: "We're sorry you had this experience. Please DM us your order details so our team can resolve this."
Keep the tone polite. Do not include quotes around your reply.
"""
    
    # 3. Generate Reply
    try:
        text_generator = AIProviderFactory.get_provider()
        response = await text_generator.generate_text(prompt=prompt, system_prompt=system_prompt)
        reply = response.get("text", "").strip()
        
        # Clean up quotes if AI adds them
        if reply.startswith('"') and reply.endswith('"'):
            reply = reply[1:-1]
            
        return reply
    except Exception as e:
        print(f"Failed to generate review reply: {e}")
        # Fallback if AI fails
        if rating >= 4:
            return "Thank you so much for your valuable feedback! ❤ We look forward to serving you again."
        else:
            return "We're sorry you had this experience. Please DM us your order details so our team can resolve this."
