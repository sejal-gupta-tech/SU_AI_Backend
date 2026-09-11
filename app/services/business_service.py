from bson import ObjectId
from app.core.database import get_database
from app.models.business import Business
from app.schemas.business import BusinessCreate

class BusinessService:
    @staticmethod
    async def get_collection():
        db = get_database()
        return db["businesses"]

    @staticmethod
    async def create_business(owner_id: str, business_in: BusinessCreate) -> Business:
        collection = await BusinessService.get_collection()
        business_dict = business_in.model_dump()
        business_dict["owner_id"] = owner_id
        business = Business(**business_dict)
        
        doc = business.model_dump(by_alias=True)
        await collection.insert_one(doc)
        return business

    @staticmethod
    async def get_business(business_id: str) -> Business | None:
        collection = await BusinessService.get_collection()
        if not ObjectId.is_valid(business_id):
            return None
        doc = await collection.find_one({"_id": business_id})
        if doc:
            return Business(**doc)
        return None

    @staticmethod
    async def get_business_by_owner(owner_id: str) -> Business | None:
        collection = await BusinessService.get_collection()
        doc = await collection.find_one({"owner_id": owner_id})
        if doc:
            return Business(**doc)
        return None
