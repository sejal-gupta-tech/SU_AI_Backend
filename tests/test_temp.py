import pytest
from app.services.website_builder_service import WebsiteBuilderService
from bson import ObjectId

@pytest.fixture(autouse=True)
async def setup_db():
    from app.core.database import connect_to_mongo, close_mongo_connection
    connect_to_mongo()
    yield
    close_mongo_connection()

@pytest.mark.asyncio
async def test_debug_chat():
    test_user_id = str(ObjectId())
    session = await WebsiteBuilderService.create_session(test_user_id)
    session.language = "Hinglish"
    await WebsiteBuilderService.save_session(session)
    print("Session created:", session.id)
    
    resp = await WebsiteBuilderService.process_chat(session.id, test_user_id, "Sharma clothing store")
    print("Chat processed:", resp.message)
