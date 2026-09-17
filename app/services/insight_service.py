async def get_dashboard_insights(db, user_id: str):

    total_posts = await db["content"].count_documents({
        "user_id": user_id
    })

    total_campaigns = await db["campaigns"].count_documents({
        "user_id": user_id
    })

    total_products = await db["products"].count_documents({
        "user_id": user_id
    })

    return {
        "stats": {
            "total_posts": total_posts,
            "total_campaigns": total_campaigns,
            "total_products": total_products,
        }
    }
