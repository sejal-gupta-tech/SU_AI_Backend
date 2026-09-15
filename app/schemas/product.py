from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=200
    )

    description: Optional[str] = None

    price: float = Field(
        ...,
        ge=0
    )

    sale_price: Optional[float] = Field(
        default=None,
        ge=0
    )

    sizes: List[str] = Field(
        default_factory=list
    )

    colors: List[str] = Field(
        default_factory=list
    )

    stock: int = Field(
        default=0,
        ge=0
    )

    image_url: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )

    description: Optional[str] = None

    price: Optional[float] = Field(
        default=None,
        ge=0
    )

    sale_price: Optional[float] = Field(
        default=None,
        ge=0
    )

    sizes: Optional[List[str]] = None

    colors: Optional[List[str]] = None

    stock: Optional[int] = Field(
        default=None,
        ge=0
    )

    image_url: Optional[str] = None


from app.models.base import PyObjectId

class ProductResponse(BaseModel):
    id: PyObjectId
    business_id: str

    name: str
    description: Optional[str] = None

    price: float
    sale_price: Optional[float] = None

    sizes: List[str] = []
    colors: List[str] = []

    stock: int

    image_url: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
