from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import ProductService
from app.services.business_service import BusinessService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_user)
):
    business = await BusinessService.get_business_by_owner(str(current_user.id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    product = await ProductService.create_product(str(business.id), product_in)
    return product

@router.get("/", response_model=List[ProductResponse])
async def get_my_products(current_user: User = Depends(get_current_user)):
    business = await BusinessService.get_business_by_owner(str(current_user.id))
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
        
    products = await ProductService.get_products_by_business(str(business.id))
    return products
