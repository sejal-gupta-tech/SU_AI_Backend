from bson import ObjectId
from app.core.database import get_database
from app.models.brand import BrandKit
from app.schemas.brand import BrandKitCreate

class BrandKitService:
    @staticmethod
    async def get_collection():
        db = get_database()
        return db["brand_kits"]

    @staticmethod
    async def create_brand_kit(business_id: str, brand_in: BrandKitCreate) -> BrandKit:
        collection = await BrandKitService.get_collection()
        brand_dict = brand_in.model_dump()
        brand_dict["business_id"] = business_id
        brand_kit = BrandKit(**brand_dict)
        
        doc = brand_kit.model_dump(by_alias=True)
        # Upsert logic could be added here, but simple insert for now
        await collection.insert_one(doc)
        return brand_kit

    @staticmethod
    async def get_brand_kit_by_business(business_id: str) -> BrandKit | None:
        collection = await BrandKitService.get_collection()
        doc = await collection.find_one({"business_id": business_id})
        if doc:
            return BrandKit(**doc)
        return None
