import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from datetime import datetime, timezone
from bson import ObjectId
from app.core.database import get_database

async def seed_reviews():
    db = get_database()
    
    # Need to get a business_id to attach the reviews to
    business = await db["businesses"].find_one()
    if not business:
        print("No business found to attach reviews to.")
        return
        
    business_id = business["_id"]
    
    # Check if we already seeded
    existing = await db["reviews"].find_one({"business_id": business_id, "customer_name": "Sanjay Verma"})
    if existing:
        print("Reviews already seeded.")
        return

    now = datetime.now(timezone.utc)
    
    reviews = [
        {
            "business_id": business_id,
            "customer_name": "Sanjay Verma",
            "rating": 5,
            "review_text": "Amazing quality! The material is very soft and it fits perfectly. Highly recommend this store.",
            "status": "New",
            "created_at": now,
            "updated_at": now
        },
        {
            "business_id": business_id,
            "customer_name": "Neha Gupta",
            "rating": 2,
            "review_text": "Delivery was late by 3 days and the packaging was slightly damaged.",
            "status": "New",
            "created_at": now,
            "updated_at": now
        }
    ]
    
    await db["reviews"].insert_many(reviews)
    print("Successfully seeded 2 reviews!")

if __name__ == "__main__":
    from app.core.database import connect_to_mongo, close_mongo_connection
    connect_to_mongo()
    asyncio.run(seed_reviews())
    close_mongo_connection()
