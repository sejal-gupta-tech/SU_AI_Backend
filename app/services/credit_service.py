from datetime import datetime, timezone
from fastapi import HTTPException, status
from pymongo.collection import ReturnDocument
from bson import ObjectId

class CreditService:
    # Centralized plan configurations
    PLANS = {
        "FREE": 5,
        "STARTER": 50,
        "GROWTH": 150,
        "PRO": 400,
        "BUSINESS": 1000,
    }

    # Centralized cost configuration
    COSTS = {
        "post_generation": 1,
        "image_generation": 1,
        "photoshoot": 2,
        "reel_generation": 3,
    }

    @staticmethod
    async def get_or_create_subscription(db, user_id: str):
        collection = db["subscriptions"]
        
        # Ensure only one active subscription per user via unique index
        # We handle this implicitly here by always doing an upsert logic if not found
        existing = await collection.find_one({"user_id": user_id})
        
        if existing:
            return existing
            
        now = datetime.now(timezone.utc)
        default_plan = "FREE"
        credits = CreditService.PLANS[default_plan]
        
        # Idempotent creation
        new_sub = {
            "user_id": user_id,
            "plan": default_plan,
            "credits_total": credits,
            "credits_remaining": credits,
            "status": "active",
            "created_at": now,
            "updated_at": now
        }
        
        try:
            # Upsert using find_one_and_update to guarantee uniqueness if multiple concurrent calls happen
            result = await collection.find_one_and_update(
                {"user_id": user_id},
                {"$setOnInsert": new_sub},
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            return result
        except Exception:
            # Fallback
            return await collection.find_one({"user_id": user_id})

    @staticmethod
    async def check_credits(db, user_id: str, action: str):
        """Check if user has enough credits without deducting. Raises 402 if not."""
        # Ensure they have a subscription
        sub = await CreditService.get_or_create_subscription(db, user_id)
        
        cost = CreditService.COSTS.get(action, 1)
        
        if sub.get("credits_remaining", 0) < cost:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits for {action}. Required: {cost}, Remaining: {sub.get('credits_remaining', 0)}"
            )
        return True
        
    @staticmethod
    async def deduct_credits(db, user_id: str, action: str) -> dict:
        """Atomically deducts credits for an action and logs the transaction. Raises 402 if insufficient."""
        cost = CreditService.COSTS.get(action, 1)
        
        if cost == 0:
            return {"success": True}
            
        # Ensure subscription exists
        await CreditService.get_or_create_subscription(db, user_id)
        
        # Atomic deduction using $gte to prevent negative balance
        sub_collection = db["subscriptions"]
        updated_sub = await sub_collection.find_one_and_update(
            {
                "user_id": user_id,
                "credits_remaining": {"$gte": cost}
            },
            {
                "$inc": {"credits_remaining": -cost},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            return_document=ReturnDocument.AFTER
        )
        
        if not updated_sub:
            # Find the actual balance to return in error
            current = await sub_collection.find_one({"user_id": user_id})
            remaining = current.get("credits_remaining", 0) if current else 0
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Insufficient credits for {action}. Required: {cost}, Remaining: {remaining}"
            )
            
        # Record transaction
        tx_collection = db["credit_transactions"]
        tx = {
            "user_id": user_id,
            "action": action,
            "credits": -cost,
            "balance_after": updated_sub["credits_remaining"],
            "created_at": datetime.now(timezone.utc)
        }
        await tx_collection.insert_one(tx)
        
        return updated_sub

    @staticmethod
    async def refund_credits(db, user_id: str, action: str, job_id: str = None) -> dict:
        """Refunds credits (e.g. if an async job fails right away). Idempotent if job_id provided."""
        cost = CreditService.COSTS.get(action, 1)
        
        if cost == 0:
            return {"success": True}
            
        tx_collection = db["credit_transactions"]
        
        # Ensure idempotency
        if job_id:
            existing_refund = await tx_collection.find_one({
                "user_id": user_id,
                "action": f"{action}_refund",
                "job_id": job_id
            })
            if existing_refund:
                return {"success": True, "message": "Already refunded"}
            
        sub_collection = db["subscriptions"]
        updated_sub = await sub_collection.find_one_and_update(
            {"user_id": user_id},
            {
                "$inc": {"credits_remaining": cost},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            return_document=ReturnDocument.AFTER
        )
        
        if updated_sub:
            tx = {
                "user_id": user_id,
                "action": f"{action}_refund",
                "credits": cost,
                "balance_after": updated_sub["credits_remaining"],
                "created_at": datetime.now(timezone.utc)
            }
            if job_id:
                tx["job_id"] = job_id
                
            await tx_collection.insert_one(tx)
            
        return updated_sub

    @staticmethod
    async def get_history(db, user_id: str):
        cursor = db["credit_transactions"].find({"user_id": user_id}).sort("created_at", -1)
        history = []
        async for tx in cursor:
            tx["id"] = str(tx["_id"])
            history.append(tx)
        return history
