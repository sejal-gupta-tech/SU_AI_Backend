import asyncio, sys
sys.path.insert(0, ".")

SEJAL_ID = "6ab36f42e493e913a05d89d5"
OLD_MOCK_ID = "60a7b45c342d3c148c2e6d5a"
SET_OP = {"$set": {"user_id": SEJAL_ID}}

async def migrate():
    from motor.motor_asyncio import AsyncIOMotorClient
    from app.core.config import settings
    client = AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.DATABASE_NAME]
    for col in ["fashion_products", "fashion_generations", "virtual_tryons"]:
        result = await db[col].update_many({"user_id": OLD_MOCK_ID}, SET_OP)
        print(col + ": migrated", result.modified_count, "docs")
    print("Done - all fashion data now belongs to sejal gupta")
    client.close()

asyncio.run(migrate())