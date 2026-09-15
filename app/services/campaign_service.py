from datetime import datetime, timezone
from bson import ObjectId

class CampaignService:
    def __init__(self, db):
        self.db = db

    async def create_campaign(
        self,
        user_id: str,
        business_id: str,
        payload: dict,
    ):
        document = payload.copy()
        document["userId"] = user_id
        document["businessId"] = business_id
        
        # Populate AI generated mocks or placeholders for results
        # A real implementation would call an AI service here
        document["strategy"] = f"AI strategy for {payload.get('goal', 'growth')}"
        document["contentStrategy"] = f"Content strategy focusing on {payload.get('targetAudience', 'your audience')}"
        document["suggestedPosts"] = ["Introductory Post", "Feature Highlight", "Testimonial"]
        document["suggestedReels"] = ["Behind the scenes", "Quick tip"]
        document["adCopy"] = "Discover our exclusive offers!"
        document["callToAction"] = "Learn More"
        document["postingSchedule"] = "Mondays, Wednesdays, Fridays"

        document["createdAt"] = datetime.now(timezone.utc)
        document["updatedAt"] = datetime.now(timezone.utc)

        result = await self.db.campaigns.insert_one(document)
        document["id"] = str(result.inserted_id)
        
        # Ensure we return `id` and remove `_id` so Pydantic model can parse it cleanly
        if "_id" in document:
            del document["_id"]

        return document

    async def get_campaigns(self, business_id: str):
        cursor = self.db.campaigns.find({"businessId": business_id}).sort("createdAt", -1)
        campaigns = []
        async for item in cursor:
            item["id"] = str(item.pop("_id"))
            campaigns.append(item)
        return campaigns

    async def get_campaign_by_id(self, campaign_id: str, business_id: str):
        if not ObjectId.is_valid(campaign_id):
            return None
            
        doc = await self.db.campaigns.find_one({
            "_id": ObjectId(campaign_id),
            "businessId": business_id
        })
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    async def update_campaign(self, campaign_id: str, business_id: str, updates: dict):
        if not ObjectId.is_valid(campaign_id):
            return None

        updates["updatedAt"] = datetime.now(timezone.utc)
        
        result = await self.db.campaigns.update_one(
            {"_id": ObjectId(campaign_id), "businessId": business_id},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            return None
            
        return await self.get_campaign_by_id(campaign_id, business_id)

    async def delete_campaign(self, campaign_id: str, business_id: str) -> bool:
        if not ObjectId.is_valid(campaign_id):
            return False
            
        result = await self.db.campaigns.delete_one({
            "_id": ObjectId(campaign_id),
            "businessId": business_id
        })
        return result.deleted_count > 0
