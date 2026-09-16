from datetime import datetime, timezone
from typing import Optional


class PhotoshootModel:

    @staticmethod
    def create_document(
        user_id: str,
        product_id: str,
        style: str,
        background: str,
        model: Optional[str],
        pose: Optional[str],
        generated_image: str,
    ):
        return {
            "user_id": user_id,
            "product_id": product_id,
            "type": "photoshoot",
            "style": style,
            "background": background,
            "model": model,
            "pose": pose,
            "generated_image": generated_image,
            "status": "generated",
            "created_at": datetime.now(timezone.utc),
        }
