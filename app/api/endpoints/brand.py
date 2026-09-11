from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.brand import BrandKitCreate, BrandKitResponse
from app.services.brand_service import BrandKitService
from app.services.business_service import BusinessService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=BrandKitResponse, status_code=status.HTTP_201_CREATED)
async def create_brand_kit(
    brand_in: BrandKitCreate,
    current_user: User = Depends(get_current_user)
):
    business = await BusinessService.get_business_by_owner(str(current_user.id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    brand_kit = await BrandKitService.create_brand_kit(str(business.id), brand_in)
    return brand_kit

@router.get("/", response_model=BrandKitResponse)
async def get_my_brand_kit(current_user: User = Depends(get_current_user)):
    business = await BusinessService.get_business_by_owner(str(current_user.id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    brand_kit = await BrandKitService.get_brand_kit_by_business(str(business.id))
    if not brand_kit:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return brand_kit
