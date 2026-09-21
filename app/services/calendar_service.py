import json
import logging
from datetime import datetime, timezone
from app.ai.factory import AIProviderFactory

logger = logging.getLogger(__name__)

async def generate_calendar_plan(
    db,
    user_id: str,
    product: dict,
    prompt: str,
    text_generator
) -> list:
    product_name = product.get("name", "Product")
    product_desc = product.get("description", "")
    
    system_prompt = f"""
You are an expert Social Media Manager. Create a 30-day social media calendar based on the user's request.
User Request: {prompt}
Product Name: {product_name}
Product Description: {product_desc}

IMPORTANT INSTRUCTION FOR VISUAL DIRECTION & CONTENT TYPE:
1. Ensure that the `visual_direction` is highly dynamic and specifically mentions DIFFERENT colors, styles, and settings for the product (especially if it's clothing) on different days. Do not use the same color or setting repeatedly.
2. The `content_type` MUST ALWAYS be "Product Post". Do NOT create Reels or any other content types.
3. Every single day must have entirely unique and dynamic captions and hashtags. 

You must respond ONLY with a valid JSON array of 30 objects, without any markdown formatting, no code blocks, no backticks.
Each object must have exactly these keys:
- "day_number": (integer from 1 to 30)
- "content_type": (string, exactly "Product Post")
- "caption": (string, highly engaging social media caption with emojis)
- "hashtags": (string, space-separated hashtags)
- "visual_direction": (string, detailed visual description of the creative, EXPLICITLY mentioning a unique color and setting for the product)

Example format:
[
  {{
    "day_number": 1,
    "content_type": "Product Post",
    "caption": "Meet your new favorite everyday essential! ✨ Upgrade your style with our premium collection.",
    "hashtags": "#StyleUpgrade #PremiumQuality #FashionDaily",
    "visual_direction": "High-quality lifestyle shot of a vibrant red {product_name} on a clean white background."
  }}
]
"""
    try:
        response = await text_generator.generate_text(prompt=system_prompt, max_tokens=4000)
        text_content = response.get("text", "")
        
        # Clean the response to ensure it's valid JSON
        if text_content.startswith("`json"):
            text_content = text_content[7:]
        if text_content.startswith("`"):
            text_content = text_content[3:]
        if text_content.endswith("`"):
            text_content = text_content[:-3]
            
        plan_data = json.loads(text_content.strip())
        
        # Save to DB for history
        document = {
            "user_id": user_id,
            "product_id": str(product.get("_id")),
            "type": "social_media_calendar",
            "prompt": prompt,
            "days": plan_data,
            "status": "generated",
            "created_at": datetime.now(timezone.utc),
        }
        await db.calendars.insert_one(document)
        
        return plan_data
        
    except Exception as e:
        logger.error(f"Failed to generate calendar: {e}")
        # Fallback dummy data if LLM parsing fails
        dummy_plan = []
        colors = ["red", "blue", "green", "black", "white", "yellow", "purple", "pink", "orange", "teal", "navy", "maroon", "olive", "coral", "grey"]
        for i in range(1, 31):
            color = colors[i % len(colors)]
            dummy_plan.append({
                "day_number": i,
                "content_type": "Product Post",
                "caption": f"Day {i} caption for {product_name}! ✨ Buy now.",
                "hashtags": f"#Day{i} #{product_name.replace(' ', '')} #{color}{product_name.replace(' ', '')}",
                "visual_direction": f"Beautiful lifestyle showcase of a {color} {product_name}."
            })
        return dummy_plan
