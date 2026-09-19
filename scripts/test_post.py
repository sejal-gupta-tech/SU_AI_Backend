import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import asyncio, traceback
from app.core.database import connect_to_mongo
from app.services.business_service import BusinessService
from app.services.brand_service import get_brand_kit
from app.services.product_service import get_products
from app.ai.services.post_generation import PostGenerationService
from app.core.database import get_database
async def run():
    connect_to_mongo()
    db = get_database()
    business = await BusinessService.get_business_by_owner('6aa8cab4fa33b37250e68d91')
    print('Business:', business)
    brand = await get_brand_kit(db, str(business.id))
    print('Brand:', brand)
    products = await get_products(db, str(business.id))
    product = products[0] if products else {}
    print('Product:', product)
    svc = PostGenerationService()
    result = await svc.generate_post(business=business.model_dump(), brand=brand, product=product, platform='instagram', objective='product_promotion', language='English')
    print('Result:', result)
try:
    asyncio.run(run())
except Exception:
    traceback.print_exc()
