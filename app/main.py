from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.api_router import api_router
from app.api.endpoints.brand import router as brand_router
from app.api.endpoints.products import router as products_router
from app.api.endpoints import content, insights, messages, reviews, social
from app.api.endpoints.photoshoot import router as photoshoot_router
from app.api.endpoints.ad import router as ad_router
from app.api.endpoints.reel import router as reel_router
from app.api.endpoints.calendar import router as calendar_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    connect_to_mongo()
    yield
    # Shutdown
    close_mongo_connection()

app = FastAPI(
    title="SevenUnique AI API",
    description="Backend API for SevenUnique AI Marketing Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=".*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(content.router)
app.include_router(social.router)

app.include_router(
    insights.router,
    prefix="/api/v1/insights",
    tags=["Insights"]
)

app.include_router(
    messages.router,
    prefix="/api/v1/messages",
    tags=["Messages"]
)

app.include_router(
    reviews.router,
    prefix="/api/v1/reviews",
    tags=["Reviews"]
)

app.include_router(photoshoot_router)
app.include_router(ad_router)
app.include_router(reel_router)
app.include_router(calendar_router)

@app.get("/")
async def root():
    return {"message": "Welcome to SevenUnique AI API"}
