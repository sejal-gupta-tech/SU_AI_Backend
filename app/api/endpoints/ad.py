from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.schemas.ad import AdRequest
from app.services.ad_service import generate_ad
from app.core.security import get_current_user
from app.core.database import get_database

from app.ai.factory import AIProviderFactory
from app.ai.image.generator import ImageGenerator
from app.core.config import settings

router = APIRouter(
    prefix="/api/v1/ai/ads",
    tags=["AI Ads"],
)

image_generator = ImageGenerator(
    api_url=getattr(settings, "IMAGE_API_URL", "https://api.openai.com/v1/images/generations"),
    api_key=getattr(settings, "IMAGE_API_KEY", "your_api_key_here")
)

@router.post("/")
async def create_ad(
    request: AdRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_database)
):
    product = None

    if request.product_id:
        product_id = ObjectId(request.product_id) if ObjectId.is_valid(request.product_id) else request.product_id
        product = await db.products.find_one({
            "_id": product_id,
            "business_id": ObjectId(current_user.business_id) if current_user.business_id else None,
        })

    if not product and not request.content_id:
        raise HTTPException(
            status_code=400,
            detail="product_id or content_id is required",
        )

    text_generator = AIProviderFactory.get_provider()

    try:
        result = await generate_ad(
            db=db,
            user_id=current_user.id,
            product=product or {},
            request=request,
            text_generator=text_generator,
            image_generator=image_generator,
        )

        return {
            "success": True,
            "message": "Ad generated successfully",
            "data": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
