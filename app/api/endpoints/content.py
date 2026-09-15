from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from app.core.security import get_current_user
from app.schemas.content import GeneratePostRequest
from app.ai.services.post_generation import PostGenerationService
from app.services.business_service import BusinessService
from app.services.brand_service import get_brand_kit
from app.services.product_service import get_products, serialize_product
from app.core.database import get_database


router = APIRouter(
    prefix="/api/v1/content",
    tags=["Content"]
)


@router.post("/generate-post")
async def generate_post(
    request: GeneratePostRequest,
    current_user=Depends(get_current_user),
):

    # ---------------------------------
    # 1. Get user's business
    # ---------------------------------

    business = await BusinessService.get_business_by_owner(str(current_user.id))

    if not business:
        raise HTTPException(
            status_code=404,
            detail="Business not found"
        )

    # ---------------------------------
    # 2. Get brand kit
    # ---------------------------------

    db = get_database()
    brand = await get_brand_kit(
        db,
        str(business.id)
    )

    # ---------------------------------
    # 3. Get product (flexible ID lookup)
    # ---------------------------------

    product = {}
    product_id = request.product_id

    # Try MongoDB ObjectId lookup first
    if ObjectId.is_valid(product_id):
        doc = await db["products"].find_one({
            "_id": ObjectId(product_id),
            "business_id": ObjectId(str(business.id))
        })
        if doc:
            product = serialize_product(doc)

    # If not found by ObjectId, try matching by custom product_id field or name
    if not product:
        doc = await db["products"].find_one({
            "business_id": ObjectId(str(business.id)),
            "$or": [
                {"product_id": product_id},
                {"name": product_id}
            ]
        })
        if doc:
            product = serialize_product(doc)

    # If still not found, use first product of the business as fallback
    if not product:
        all_products = await get_products(db, str(business.id))
        if all_products:
            product = all_products[0]

    # ---------------------------------
    # 4. Generate AI Post
    # ---------------------------------

    service = PostGenerationService()

    generated = await service.generate_post(
        business=business.model_dump(mode="json"),
        brand=brand,
        product=product,
        platform=request.platform,
        objective=request.objective,
        language=request.language,
        additional_instruction=request.additional_instruction,
    )

    # ---------------------------------
    # 5. Add metadata
    # ---------------------------------

    generated["product_id"] = request.product_id
    generated["platform"] = request.platform
    generated["objective"] = request.objective

    return {
        "success": True,
        "data": generated
    }