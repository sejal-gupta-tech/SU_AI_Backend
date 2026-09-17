from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.core.database import get_database
from app.services.insight_service import get_dashboard_insights as fetch_insights

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_insights(
    current_user=Depends(get_current_user),
    db=Depends(get_database)
):
    return await fetch_insights(
        db,
        str(current_user.id)
    )