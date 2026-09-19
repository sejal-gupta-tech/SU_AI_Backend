from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.schemas.calendar import CalendarRequest, CalendarResponse
from app.services.calendar_service import generate_calendar_plan
from app.core.security import get_current_user
from app.core.database import get_database
from app.ai.factory import AIProviderFactory

router = APIRouter(
    prefix="/api/v1/ai/calendar",
    tags=["AI Calendar"],
)

@router.post("/", response_model=CalendarResponse)
async def create_calendar(
    request: CalendarRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_database)
):
    product_id = ObjectId(request.product_id) if ObjectId.is_valid(request.product_id) else request.product_id
    
    product = await db.products.find_one({
        "_id": product_id,
        "business_id": ObjectId(current_user.business_id) if current_user.business_id else None,
    })

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    try:
        text_generator = AIProviderFactory.get_provider()
        
        result = await generate_calendar_plan(
            db=db,
            user_id=current_user.id,
            product=product,
            prompt=request.prompt,
            text_generator=text_generator,
        )

        return {
            "success": True,
            "message": "Calendar generated successfully",
            "data": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
