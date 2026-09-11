from typing import Dict, Any
from app.services.business_service import BusinessService
from app.services.brand_service import BrandKitService
from app.services.product_service import ProductService

class BusinessContextService:
    @staticmethod
    async def get_business_context(business_id: str) -> Dict[str, Any]:
        """
        Gathers business, brand, and product data to create a structured context.
        """
        business = await BusinessService.get_business(business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found.")

        brand_kit = await BrandKitService.get_brand_kit_by_business(business_id)
        products = await ProductService.get_products_by_business(business_id)

        context = {
            "business": {
                "name": business.name,
                "category": business.category,
                "location": business.location,
                "target_customer": business.target_customer,
                "language": business.preferred_language
            },
            "brand": {},
            "products": []
        }

        if brand_kit:
            context["brand"] = {
                "tone": brand_kit.brand_voice,
                "tagline": brand_kit.tagline,
                "target_audience": brand_kit.target_audience
            }

        for product in products:
            context["products"].append({
                "id": str(product.id),
                "name": product.name,
                "price": product.price,
                "sale_price": product.sale_price,
                "sizes": product.sizes,
                "colors": product.colors,
                "stock": product.stock,
                "category": product.category
            })

        return context
