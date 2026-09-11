from typing import Dict, Any
import json

class PromptBuilder:
    @staticmethod
    def build_caption_prompt(
        context: Dict[str, Any],
        product_id: str,
        objective: str,
        tone: str,
        language: str,
        offer: str,
        cta: str
    ) -> str:
        """
        Builds a strict LLM prompt using the business context and generation parameters.
        """
        # Find the specific product
        target_product = next((p for p in context.get("products", []) if p["id"] == product_id), None)
        
        product_info = "Product information not available."
        if target_product:
            product_info = json.dumps(target_product, indent=2)

        business_info = json.dumps(context.get("business", {}), indent=2)
        brand_info = json.dumps(context.get("brand", {}), indent=2)

        system_prompt = (
            "You are an expert AI Marketing Agent for SevenUnique AI. "
            "Use only the supplied business and product information for factual details. "
            "Never invent prices, discounts, sizes, colors, stock quantities, contact details or policies. "
            "If information is unavailable, do not invent it."
        )

        user_prompt = f"""
Please generate a social media caption based on the following context.

BUSINESS INFO:
{business_info}

BRAND INFO:
{brand_info}

TARGET PRODUCT:
{product_info}

GENERATION PARAMETERS:
- Objective: {objective}
- Tone: {tone}
- Language: {language}
- Offer/Discount: {offer}
- Call to Action (CTA): {cta}

Return the output strictly in the following JSON format:
{{
    "caption": "The generated caption text here",
    "hashtags": ["#tag1", "#tag2"],
    "cta": "The call to action text"
}}
"""
        return system_prompt, user_prompt
