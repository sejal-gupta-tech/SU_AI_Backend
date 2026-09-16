def build_ad_prompt(
    product: dict,
    platform: str,
    objective: str,
    language: str,
    target_audience: str | None,
    cta: str | None,
    additional_instruction: str | None,
):

    return f"""
Create a high-converting digital advertisement.

PRODUCT
Name: {product.get("name", "")}
Description: {product.get("description", "")}
Price: {product.get("selling_price", "")}

PLATFORM
{platform}

OBJECTIVE
{objective}

LANGUAGE
{language}

TARGET AUDIENCE
{target_audience or "General relevant audience"}

CTA
{cta or "Shop Now"}

Additional instructions:
{additional_instruction or "None"}

Return JSON with:

{{
  "headline": "...",
  "primary_text": "...",
  "description": "...",
  "cta": "...",
  "hashtags": ["...", "...", "..."]
}}

Rules:
- Keep product claims accurate.
- Do not invent discounts.
- Do not invent product features.
- Keep language natural.
- Adapt copy to the selected platform.
"""
