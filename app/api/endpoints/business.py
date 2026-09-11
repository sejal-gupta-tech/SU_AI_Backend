from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.business import BusinessCreate, BusinessResponse
from app.services.business_service import BusinessService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def create_business(
    business_in: BusinessCreate,
    current_user: User = Depends(get_current_user)
):
    existing_business = await BusinessService.get_business_by_owner(str(current_user.id))
    if existing_business:
        raise HTTPException(status_code=400, detail="User already has a business")
    
    business = await BusinessService.create_business(str(current_user.id), business_in)
    return business

@router.get("/me", response_model=BusinessResponse)
async def get_my_business(current_user: User = Depends(get_current_user)):
    business = await BusinessService.get_business_by_owner(str(current_user.id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business
