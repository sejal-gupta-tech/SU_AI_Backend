from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.schemas.photoshoot import PhotoshootRequest
from app.services.photoshoot_service import generate_photoshoot
from app.core.security import get_current_user
from app.core.database import get_database
from app.ai.image.generator import ImageGenerator
from app.ai.factory import AIProviderFactory

router = APIRouter(
    prefix="/api/v1/ai/photoshoot",
    tags=["AI Photoshoot"],
)

# Initialize ImageGenerator
image_generator = ImageGenerator(
    api_url="https://api.openai.com/v1/images/generations",
    api_key="your_api_key_here"
)


@router.post("")
async def create_photoshoot(
    request: PhotoshootRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_database)
):
    from app.services.credit_service import CreditService
    await CreditService.check_credits(db, current_user.id, "photoshoot")

    # Flexible product lookup logic
    product = None
    product_id = request.product_id
    business_id = ObjectId(current_user.business_id) if current_user.business_id else None

    # Try ObjectId lookup
    if ObjectId.is_valid(product_id):
        product = await db["products"].find_one({"_id": ObjectId(product_id), "business_id": business_id})

    # Try name or custom product_id lookup
    if not product:
        product = await db["products"].find_one({
            "business_id": business_id,
            "$or": [{"product_id": product_id}, {"name": product_id}]
        })

    # Fallback to first product
    if not product and business_id:
        product = await db["products"].find_one({"business_id": business_id})

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    try:
        text_generator = AIProviderFactory.get_provider()
        
        result = await generate_photoshoot(
            db=db,
            user_id=current_user.id,
            product=product,
            request=request,
            text_generator=text_generator,
            image_provider=image_generator,
        )

        await CreditService.deduct_credits(db, current_user.id, "photoshoot")

        return {
            "success": True,
            "message": "Photoshoot generated successfully",
            "data": result,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )
