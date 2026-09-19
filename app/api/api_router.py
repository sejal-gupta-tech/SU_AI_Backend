from fastapi import APIRouter
from app.api.endpoints import business, brand, products, ai, auth, campaigns, admin, analytics

api_router = APIRouter()
api_router.include_router(business.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(brand.router, prefix="/brands", tags=["brands"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(campaigns.router)
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
