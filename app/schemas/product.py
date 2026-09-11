from pydantic import BaseModel
from typing import List, Optional

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    sale_price: Optional[float] = None
    sizes: List[str] = []
    colors: List[str] = []
    stock: int = 0
    category: str
    sku: str
    images: List[str] = []

class ProductResponse(ProductCreate):
    id: str
    business_id: str
