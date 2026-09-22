import json
import logging
from bson import ObjectId
from app.ai.factory import AIProviderFactory
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

async def get_dashboard_insights(db, user_id: str):
    # 1. Fetch real analytics data
    try:
        analytics_svc = AnalyticsService(db)
        business_record = await db["businesses"].find_one({"owner_id": user_id})
        business_id = str(business_record["_id"]) if business_record else None
        
        # Get 30d stats
        overview = await analytics_svc.get_overview(user_id, business_id, "30d")
        
        content = overview.get("content", {})
        ai_usage = overview.get("ai_usage", {})
        business = overview.get("business", {})
        score = overview.get("marketing_score", {}).get("score", 0)
        
        total_posts = content.get("posts", 0)
        total_reels = content.get("reels", 0)
        total_products = business.get("products", 0)
        credits_used = ai_usage.get("credits_used", 0)
        
        # Also count campaigns
        total_campaigns = await db["campaigns"].count_documents({"user_id": user_id})
        
        stats = {
            "total_posts": total_posts,
            "total_campaigns": total_campaigns,
            "total_products": total_products,
            "total_reels": total_reels,
            "credits_used": credits_used,
            "marketing_score": score
        }
        
    except Exception as e:
        logger.error(f"Error fetching stats for insights: {e}")
        stats = {
            "total_posts": 0, "total_campaigns": 0, "total_products": 0,
            "total_reels": 0, "credits_used": 0, "marketing_score": 0
        }

    # 2. Use AI to generate real insights
    ai_provider = AIProviderFactory.get_provider()
    
    prompt = f"""
    Analyze the following 30-day performance data for a small business:
    - Social Posts created: {stats['total_posts']}
    - Reels created: {stats['total_reels']}
    - Marketing Campaigns: {stats['total_campaigns']}
    - Products in Catalog: {stats['total_products']}
    - AI Credits Used: {stats['credits_used']}
    - Overall Marketing Health Score: {stats['marketing_score']}/100

    Generate 3 actionable, short insights for the user. Keep them very concise.
    Format the response as a JSON array of strings ONLY. No markdown, no extra text.
    Example: ["Insight 1 here", "Insight 2 here", "Insight 3 here"]
    """
    
    try:
        res = await ai_provider.generate_text(prompt=prompt, system_prompt="You are a data analyst for small businesses. Output only raw JSON array of strings.")
        text = res.get("text", "[]").strip()
        # Clean up if AI adds markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
            
        ai_insights = json.loads(text.strip())
        if not isinstance(ai_insights, list):
            ai_insights = ["Start generating more content to boost your score!"]
    except Exception as e:
        logger.error(f"Failed to generate AI insights: {e}")
        ai_insights = [
            "Consistent posting on social media increases engagement.",
            "Try generating AI Reels for higher reach.",
            "Add more products to your catalog to unlock new post ideas."
        ]
        
    return {
        "stats": stats,
        "ai_insights": ai_insights
    }
