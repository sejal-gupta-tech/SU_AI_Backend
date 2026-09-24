import asyncio
from app.core.database import connect_to_mongo, close_mongo_connection
from app.services.website_builder_service import WebsiteBuilderService
from bson import ObjectId

async def main():
    connect_to_mongo()
    test_user_id = str(ObjectId())
    try:
        session = await WebsiteBuilderService.create_session(test_user_id)
        session.language = "Hinglish"
        await WebsiteBuilderService.save_session(session)
        print("Session created:", session.id)
        
        resp = await WebsiteBuilderService.process_chat(session.id, test_user_id, "Sharma clothing store")
        print("Chat processed:", resp.message)
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        close_mongo_connection()

if __name__ == '__main__':
    asyncio.run(main())
