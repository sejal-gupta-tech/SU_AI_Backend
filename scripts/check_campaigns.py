import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

async def main():
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    client = AsyncIOMotorClient(uri)
    db = client["sevenunique_ai_db"]
    
    cursor = db.campaigns.find().sort("createdAt", -1).limit(5)
    campaigns = await cursor.to_list(length=5)
    
    for c in campaigns:
        print(f"ID: {c['_id']}, Name: {c.get('name')}, BusinessID: {c.get('businessId')}")

if __name__ == '__main__':
    asyncio.run(main())