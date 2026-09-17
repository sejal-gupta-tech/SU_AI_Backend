from app.ai.prompts.photoshoot import build_photoshoot_prompt

async def generate_photoshoot(
    db,
    user_id: str,
    product: dict,
    request,
    text_generator,
    image_provider,
):
    base_prompt = build_photoshoot_prompt(
        product_name=product.get("name", "Product"),
        style=request.style,
        background=request.background,
        model=request.model,
        pose=request.pose,
        additional_instruction=request.additional_instruction,
    )

    llm_prompt = f"""
You are an expert AI photography prompt engineer. Based on the following requirements, write a highly descriptive, comma-separated image generation prompt for Stable Diffusion.
Focus strictly on visual details, lighting, camera angles, and composition. The main subject MUST be the product itself.

Requirements:
{base_prompt}

IMPORTANT RULES:
- If the requirements specify "No model", you MUST explicitly add negative prompts like "no humans, no people, product only, empty scene" to your output.
- The product MUST be the absolute center of attention.
- Do not describe a person using the product unless a specific model is requested.

Return ONLY the comma-separated prompt text, no intro, no quotes, no extra text.
"""
    try:
        prompt_response = await text_generator.generate_text(prompt=llm_prompt)
        prompt = prompt_response.get("text", base_prompt)
    except Exception as e:
        print(f"Text generation failed: {e}")
        # Fallback to a realistic prompt directly since LLM failed
        product_desc = product.get('name', 'Product')
        prompt = f"Professional product photography of a {product_desc}, {request.style} style, {request.background} background, highly detailed, photorealistic, 8k resolution, commercial studio lighting"
        if request.model and request.model.lower() != "no model":
            prompt += f", featuring {request.model}"
        else:
            prompt += ", no people, no humans, product only"
            
        if request.additional_instruction:
            prompt += f", {request.additional_instruction}"
            
        if product.get("image"):
            prompt += f" based on image reference: {product.get('image')}"

    result = await image_provider.generate(
        prompt=prompt,
        product_image=product.get("image"),
    )

    document = {
        "user_id": user_id,
        "product_id": request.product_id,
        "type": "photoshoot",
        "style": request.style,
        "background": request.background,
        "model": request.model,
        "pose": request.pose,
        "prompt": prompt,
        "generated_image": result["image_url"],
        "status": "generated",
    }

    inserted = await db.photoshoots.insert_one(document)

    # Also save to Content Library
    await db.contents.insert_one({
        "user_id": user_id,
        "type": "photoshoot",
        "source_id": str(inserted.inserted_id),
        "product_id": request.product_id,
        "title": f"{product.get('name', 'Product')} Photoshoot",
        "media_url": result["image_url"],
        "status": "generated",
    })

    return {
        "id": str(inserted.inserted_id),
        "image_url": result["image_url"],
        "prompt": prompt,
        "style": request.style,
        "status": "generated",
    }
