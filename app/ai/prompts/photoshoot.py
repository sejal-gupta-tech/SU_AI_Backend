def build_photoshoot_prompt(
    product_name: str,
    style: str,
    background: str,
    model: str | None = None,
    pose: str | None = None,
    additional_instruction: str | None = None,
):
    prompt = f"""
Create a professional commercial product photoshoot.

Product:
{product_name}

Photography Style:
{style}

Background:
{background}

Model:
{model or "No model"}

Pose:
{pose or "Natural product-focused composition"}

Requirements:
- Keep the product visually accurate.
- Do not change the product identity.
- Keep packaging, logo and important product details recognizable.
- Create professional commercial photography.
- Use realistic lighting.
- Use high quality composition.
- Make the image suitable for social media marketing.
- Avoid distorted text and logos.
"""

    if additional_instruction:
        prompt += f"""

Additional instructions:
{additional_instruction}
"""

    return prompt.strip()
