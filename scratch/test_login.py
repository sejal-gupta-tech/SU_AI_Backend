import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import connect_to_mongo, close_mongo_connection

async def main():
    connect_to_mongo()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", json={
            "email": "kratikasharma2003@gmail.com",
            "password": "Admin@123"
        })
        print(response.status_code)
        print(response.json())
    close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(main())
