from fastapi import APIRouter
from app.api.endpoints import business, ai

api_router = APIRouter()
api_router.include_router(business.router, prefix="/businesses", tags=["businesses"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
