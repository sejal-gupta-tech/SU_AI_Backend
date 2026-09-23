import asyncio
from app.core.database import connect_to_mongo, get_database

async def main():
    connect_to_mongo()
    db = get_database()
    users = await db['users'].find().to_list(length=5)
    for u in users:
        print(u)

if __name__ == "__main__":
    asyncio.run(main())
