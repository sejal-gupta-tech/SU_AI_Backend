from fastapi import APIRouter, Depends, HTTPException, Body
from app.core.security import get_current_user
from app.core.database import get_database
from app.services.social_service import SocialService

router = APIRouter(
    prefix="/api/v1/social",
    tags=["Social"]
)

@router.post("/publish-whatsapp/{content_id}")
async def publish_whatsapp(
    content_id: str,
    target_phone: str = Body(..., embed=True),
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    business_id = str(current_user["business_id"])
    
    result = await SocialService.publish_to_whatsapp(
        db=db,
        business_id=business_id,
        content_id=content_id,
        target_phone=target_phone
    )
    
    return {"success": True, "message": "Successfully sent to WhatsApp", "data": result}

@router.post("/publish-instagram/{content_id}")
async def publish_instagram(
    content_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    business_id = str(current_user["business_id"])
    
    result = await SocialService.publish_to_instagram(
        db=db,
        business_id=business_id,
        content_id=content_id
    )
    
    return {"success": True, "message": "Successfully published to Instagram", "data": result}

@router.post("/publish-facebook/{content_id}")
async def publish_facebook(
    content_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    business_id = str(current_user["business_id"])
    
    result = await SocialService.publish_to_facebook(
        db=db,
        business_id=business_id,
        content_id=content_id
    )
    
    return {"success": True, "message": "Successfully published to Facebook", "data": result}

@router.post("/publish-linkedin/{content_id}")
async def publish_linkedin(
    content_id: str,
    current_user = Depends(get_current_user),
    db = Depends(get_database)
):
    business_id = str(current_user["business_id"])
    
    result = await SocialService.publish_to_linkedin(
        db=db,
        business_id=business_id,
        content_id=content_id
    )
    
    return {"success": True, "message": "Successfully published to LinkedIn", "data": result}
