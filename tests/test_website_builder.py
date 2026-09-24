import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.website_builder_service import WebsiteBuilderService
from bson import ObjectId

@pytest.fixture(autouse=True)
async def setup_db():
    from app.core.database import connect_to_mongo, close_mongo_connection
    connect_to_mongo()
    yield
    close_mongo_connection()

test_user_id = str(ObjectId())

async def override_get_current_user():
    from app.models.user import User
    return User(
        id=test_user_id,
        name="Test User",
        email="test@example.com",
        hashed_password="hashed_password",
        role="user",
        email_verified=True
    )

from app.core.security import get_current_user
app.dependency_overrides[get_current_user] = override_get_current_user

@pytest.mark.asyncio
async def test_session_creation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/website-builder/session", json={"language": "English"})
        assert res.status_code == 201
        data = res.json()
        assert "sessionId" in data
        assert data["language"] == "English"
        assert len(data["messages"]) > 0

@pytest.mark.asyncio
async def test_chat_english():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.post("/api/v1/website-builder/session", json={"language": "English"})
        session_id = res1.json()["sessionId"]

        res2 = await ac.post(f"/api/v1/website-builder/session/{session_id}/message", json={
            "message": "My business is a coffee shop in London.",
        })
        assert res2.status_code == 200
        data = res2.json()
        assert "messages" in data

@pytest.mark.asyncio
async def test_recommendations_and_generate():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.post("/api/v1/website-builder/session", json={"language": "English"})
        session_id = res1.json()["sessionId"]

        # 1. Ask for recommendations
        res2 = await ac.post(f"/api/v1/website-builder/session/{session_id}/message", json={
            "message": "recommend"
        })
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["type"] == "recommendation"
        
        # 2. Select Template
        res3 = await ac.post(f"/api/v1/website-builder/session/{session_id}/message", json={
            "message": "Selected Template",
            "data": {"action": "select_template", "templateId": "rec1", "templateName": "Premium Luxury"}
        })
        assert res3.status_code == 200
        
        # 3. Generate
        res4 = await ac.post(f"/api/v1/website-builder/session/{session_id}/message", json={
            "message": "Build My Website",
            "data": {"action": "generate"}
        })
        assert res4.status_code == 200
        data4 = res4.json()
        assert data4["siteId"] is not None
        assert data4["generatedSiteData"] is not None

@pytest.mark.asyncio
async def test_revise_website():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res1 = await ac.post("/api/v1/website-builder/session", json={"language": "English"})
        session_id = res1.json()["sessionId"]

        # Generate directly
        res2 = await ac.post(f"/api/v1/website-builder/session/{session_id}/message", json={
            "message": "build my website",
            "data": {"action": "generate"}
        })
        site_id = res2.json()["siteId"]
        
        # Revise
        res3 = await ac.post(f"/api/v1/website-builder/site/{site_id}/revise", json={
            "instructions": "Make it more premium"
        })
        assert res3.status_code == 200
        assert "generatedSiteData" in res3.json()
