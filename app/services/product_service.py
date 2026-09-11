from bson import ObjectId
from app.core.database import get_database
from app.models.product import Product
from app.schemas.product import ProductCreate

class ProductService:
    @staticmethod
    async def get_collection():
        db = get_database()
        return db["products"]

    @staticmethod
    async def create_product(business_id: str, product_in: ProductCreate) -> Product:
        collection = await ProductService.get_collection()
        product_dict = product_in.model_dump()
        product_dict["business_id"] = business_id
        product = Product(**product_dict)
        
        doc = product.model_dump(by_alias=True)
        await collection.insert_one(doc)
        return product

    @staticmethod
    async def get_products_by_business(business_id: str) -> list[Product]:
        collection = await ProductService.get_collection()
        cursor = collection.find({"business_id": business_id})
        products = []
        async for doc in cursor:
            products.append(Product(**doc))
        return products

    @staticmethod
    async def get_product(product_id: str) -> Product | None:
        collection = await ProductService.get_collection()
        if not ObjectId.is_valid(product_id):
            return None
        doc = await collection.find_one({"_id": product_id})
        if doc:
            return Product(**doc)
        return None
