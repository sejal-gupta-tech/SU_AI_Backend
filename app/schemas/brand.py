from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ContactInfo(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class LocationInfo(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None


class BrandCreate(BaseModel):
    logo_url: Optional[str] = None

    primary_color: Optional[str] = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )

    secondary_color: Optional[str] = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )

    font: Optional[str] = None

    tone: Optional[str] = None

    brand_description: Optional[str] = None

    target_audience: Optional[str] = None

    website: Optional[HttpUrl] = None

    instagram: Optional[str] = None

    contact: Optional[ContactInfo] = None

    location: Optional[LocationInfo] = None

    social_style: Optional[str] = None


class BrandUpdate(BaseModel):
    logo_url: Optional[str] = None

    primary_color: Optional[str] = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )

    secondary_color: Optional[str] = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$"
    )

    font: Optional[str] = None

    tone: Optional[str] = None

    brand_description: Optional[str] = None

    target_audience: Optional[str] = None

    website: Optional[HttpUrl] = None

    instagram: Optional[str] = None

    contact: Optional[ContactInfo] = None

    location: Optional[LocationInfo] = None

    social_style: Optional[str] = None


class BrandResponse(BaseModel):
    id: str
    business_id: str

    logo_url: Optional[str] = None

    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None

    font: Optional[str] = None
    tone: Optional[str] = None

    brand_description: Optional[str] = None
    target_audience: Optional[str] = None

    website: Optional[str] = None
    instagram: Optional[str] = None

    contact: Optional[ContactInfo] = None
    location: Optional[LocationInfo] = None

    social_style: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
