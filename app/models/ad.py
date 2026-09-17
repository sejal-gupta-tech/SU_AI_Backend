from datetime import datetime, timezone


class AdModel:

    @staticmethod
    def create_document(
        user_id: str,
        request,
        result: dict,
    ):

        return {
            "user_id": user_id,
            "product_id": request.product_id,
            "content_id": request.content_id,
            "platform": request.platform,
            "objective": request.objective,
            "language": request.language,
            "target_audience": request.target_audience,
            "additional_instruction": request.additional_instruction,
            "cta": request.cta,
            "headline": result.get("headline"),
            "primary_text": result.get("primary_text"),
            "description": result.get("description"),
            "hashtags": result.get("hashtags", []),
            "creative_url": result.get("creative_url"),
            "status": "generated",
            "created_at": datetime.now(timezone.utc),
        }
