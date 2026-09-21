from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.database import get_database
from app.services.credit_service import CreditService
from app.schemas.credit import SubscriptionResponse

router = APIRouter(
    prefix="/api/v1/subscription",
    tags=["Subscription"]
)

@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    sub = await CreditService.get_or_create_subscription(db, current_user.id)
    sub["id"] = str(sub.pop("_id"))
    return sub
