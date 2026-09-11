from typing import List, Optional
from app.models.base import MongoBaseModel

class Product(MongoBaseModel):
    business_id: str
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
