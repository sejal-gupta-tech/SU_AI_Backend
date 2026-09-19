import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from bson import ObjectId

async def main():
    # Connect to MongoDB using the actual connection string from settings
    print(f"Connecting to: {settings.MONGO_URI[:30]}...")
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DATABASE_NAME]
    
    # Fetch campaigns
    cursor = db.campaigns.find().limit(5)
    campaigns = await cursor.to_list(length=5)
    
    if not campaigns:
        print("NO_CAMPAIGNS_FOUND")
    else:
        for c in campaigns:
            print(f"Campaign ID: {c['_id']} | Name: {c.get('name', 'Unnamed')}")

if __name__ == '__main__':
    asyncio.run(main())