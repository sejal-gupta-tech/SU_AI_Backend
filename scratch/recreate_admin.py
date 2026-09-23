import asyncio
from app.core.database import connect_to_mongo, get_database, close_mongo_connection
from app.core.security import get_password_hash

async def main():
    connect_to_mongo()
    db = get_database()
    
    admin_email = "admin@example.com"
    existing = await db["users"].find_one({"email": admin_email})
    if not existing:
        await db["users"].insert_one({
            "name": "Admin",
            "email": admin_email,
            "hashed_password": get_password_hash("Admin@123"),
            "role": "admin",
            "email_verified": True
        })
        print("Admin user recreated.")
    
    # Also recreate the user they might be testing with
    kratika_email = "kratikasharma2003@gmail.com"
    if not await db["users"].find_one({"email": kratika_email}):
        await db["users"].insert_one({
            "name": "Kratika Sharma",
            "email": kratika_email,
            "hashed_password": get_password_hash("Admin@123"),
            "role": "user",
            "email_verified": True
        })
        print("Kratika user recreated.")
        
    close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
