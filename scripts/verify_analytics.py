import asyncio
import httpx
from app.core.security import create_access_token
from app.core.database import connect_to_mongo, get_database
from bson import ObjectId


async def main():
    connect_to_mongo()
    db = get_database()
    user = await db["users"].find_one({})
    if not user:
        print("No users in DB — use a real JWT from login")
        return

    user_id = str(user["_id"])
    email = user.get("email", "unknown")
    print(f"Using real user: {user_id} | {email}")

    token = create_access_token(subject=user_id)
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        for rng in ["7d", "30d", "90d"]:
            r = await client.get(
                "/api/v1/analytics/overview",
                params={"range": rng},
                headers=headers,
            )
            d = r.json()
            data = d.get("data", {})
            print(f"\n--- range={rng}  HTTP {r.status_code} ---")
            print(f"  success:  {d.get('success')}")
            print(f"  content:  {data.get('content')}")
            print(f"  ai_usage: {data.get('ai_usage')}")
            print(f"  business: {data.get('business')}")
            print(f"  external: {data.get('external')}")
            ms = data.get("marketing_score", {})
            print(f"  score:    {ms.get('score')} | breakdown: {ms.get('breakdown')}")
            rec = data.get("recommendation", {})
            print(f"  rec_type: {rec.get('type')} | text: {rec.get('text', '')[:60]}...")
            buckets = data.get("activity", [])
            print(f"  activity buckets: {len(buckets)} (first: {buckets[0] if buckets else 'none'})")

        # Invalid range -> 400
        r400 = await client.get(
            "/api/v1/analytics/overview",
            params={"range": "15d"},
            headers=headers,
        )
        print(f"\n--- range=15d (invalid)  HTTP {r400.status_code}  detail: {r400.json().get('detail')} ---")

        # Unauthenticated -> 401
        r401 = await client.get("/api/v1/analytics/overview", params={"range": "7d"})
        print(f"--- no auth  HTTP {r401.status_code} ---")


asyncio.run(main())
