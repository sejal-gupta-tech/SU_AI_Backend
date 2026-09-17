import json

from app.ai.prompts.post import build_post_prompt
from app.ai.factory import AIProviderFactory


class PostGenerationService:

    async def generate_post(
        self,
        business: dict,
        brand: dict,
        product: dict,
        platform: str,
        objective: str,
        language: str,
        additional_instruction: str | None = None,
    ):
        # Ensure brand is always a dict (get_brand_kit can return None)
        if brand is None:
            brand = {}

        prompt = build_post_prompt(
            business=business,
            brand=brand,
            product=product,
            platform=platform,
            objective=objective,
            language=language,
            additional_instruction=additional_instruction,
        )

        provider = AIProviderFactory.get_provider()
        response = await provider.generate_text(prompt=prompt)
        raw_text = response.get("text", "") if isinstance(response, dict) else str(response)

        # Strip markdown code blocks if present
        if "```json" in raw_text:
            raw_text = raw_text.split("```json")[-1].split("```")[0].strip()
        elif "```" in raw_text:
            raw_text = raw_text.split("```")[1].strip()

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            parsed = {
                "headline": "",
                "caption": raw_text,
                "call_to_action": "",
                "hashtags": [],
                "creative_direction": "",
            }

        # Generate graphic
        from app.utils.image_composer import ImageComposer
        image_url = product.get("image_url", "")
        if image_url:
            brand_colors = brand.get("colors", {}) if isinstance(brand, dict) else {}
            banner_url = await ImageComposer.generate_banner(
                product_image_url=image_url,
                headline=parsed.get("headline", "New Product!"),
                cta=parsed.get("call_to_action", "Shop Now"),
                brand_colors=brand_colors
            )
            parsed["media_url"] = banner_url

        return parsed