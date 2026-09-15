from fastapi import APIRouter
from app.api.endpoints import business, brand, products, ai, auth, campaigns

api_router = APIRouter()
api_router.include_router(business.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(campaigns.router)
