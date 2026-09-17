import asyncio
import logging
import traceback
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.schemas.reel import GenerateReelRequest, ReelJobStatus
from app.services.reel_script_service import ReelScriptService
from app.ai.providers.voice_provider import get_voice_provider
from app.ai.providers.video_provider import get_video_provider
from app.ai.video.composer import VideoComposer

logger = logging.getLogger(__name__)

class ReelService:
    def __init__(self, db):
        self.db = db
        self.script_service = ReelScriptService()
        self.voice_provider = get_voice_provider()
        self.video_provider = get_video_provider()
        self.composer = VideoComposer()

    async def create_reel_job(self, user_id: str, business_id: str, request: GenerateReelRequest, product: dict, brand: dict) -> str:
        """Creates a background job for Reel generation."""
        job_doc = {
            "user_id": ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id,
            "business_id": ObjectId(business_id) if ObjectId.is_valid(business_id) else business_id,
            "product_id": request.product_id,
            "objective": request.objective,
            "platform": request.platform,
            "language": request.language,
            "duration": request.duration,
            "status": "queued",
            "progress": 0,
            "stage": "Waiting to start",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.db["reel_jobs"].insert_one(job_doc)
        job_id = str(result.inserted_id)
        
        # In a production environment, this should be sent to a Celery/Redis queue.
        # Here we use asyncio.create_task for the background job.
        asyncio.create_task(self._process_reel_generation(job_id, product, brand, request))
        
        return job_id

    async def get_job_status(self, job_id: str) -> ReelJobStatus:
        if not ObjectId.is_valid(job_id):
            return None
            
        job = await self.db["reel_jobs"].find_one({"_id": ObjectId(job_id)})
        if not job:
            return None
            
        return ReelJobStatus(
            job_id=str(job["_id"]),
            status=job.get("status", "unknown"),
            progress=job.get("progress", 0),
            stage=job.get("stage", ""),
            video_url=job.get("video_url"),
            thumbnail_url=job.get("thumbnail_url"),
            script=job.get("script"),
            caption=job.get("caption"),
            hashtags=job.get("hashtags")
        )

    async def _update_job(self, job_id: str, updates: dict):
        updates["updated_at"] = datetime.utcnow()
        await self.db["reel_jobs"].update_one(
            {"_id": ObjectId(job_id)},
            {"$set": updates}
        )

    async def _process_reel_generation(self, job_id: str, product: dict, brand: dict, request: GenerateReelRequest):
        try:
            # 1. Generate Script
            await self._update_job(job_id, {"status": "processing", "progress": 10, "stage": "Generating script"})
            script = await self.script_service.generate_script(
                product=product,
                brand=brand,
                objective=request.objective,
                platform=request.platform,
                duration=request.duration,
                language=request.language,
                tone=request.tone,
                offer=request.offer,
                additional_instruction=request.additional_instruction
            )
            await self._update_job(job_id, {"script": script.model_dump(), "caption": script.caption, "hashtags": script.hashtags})
            
            # Extract combined voiceover text
            full_voiceover = " ".join([scene.voiceover for scene in script.scenes if scene.voiceover])
            
            # 2. Generate Voice
            await self._update_job(job_id, {"progress": 30, "stage": "Generating voiceover"})
            audio_url = await self.voice_provider.generate_audio(
                text=full_voiceover,
                language=script.language,
                voice="en_US-lessac-medium" # Should be mapped properly
            )
            
            # 3. Generate Video
            await self._update_job(job_id, {"progress": 50, "stage": "Generating video scenes"})
            
            image_url = product.get("image_url") or (product.get("images")[0] if product.get("images") else None)
            if not image_url:
                # We need a fallback or to use a static image if possible
                pass
            
            video_job_id = await self.video_provider.generate_video(
                image_url=image_url,
                prompt=script.scenes[0].visual if script.scenes else "Product showcase",
                duration=script.duration_seconds
            )
            
            # Wait for video (mocked)
            await asyncio.sleep(2)
            video_url = await self.video_provider.get_result(video_job_id)
            
            # 4. Compose Final Video
            await self._update_job(job_id, {"progress": 80, "stage": "Composing final reel"})
            final_video_url = await self.composer.compose_reel(
                video_segments=[video_url] if image_url else [], # Typically we'd use the generated video
                audio_url=audio_url,
                brand_colors={"primary": brand.get("primary_color", "#000000")}
            )
            
            # 5. Completed
            await self._update_job(job_id, {
                "status": "completed",
                "progress": 100,
                "stage": "Completed",
                "video_url": final_video_url,
                "thumbnail_url": image_url
            })
            
            # Optionally copy to 'contents' collection
            
        except Exception as e:
            err_msg = str(e).strip()
            if not err_msg:
                err_msg = repr(e)
            # Truncate extremely long error messages (like Pydantic Validation errors)
            if len(err_msg) > 200:
                err_msg = err_msg[:200] + "..."
                
            logger.error(f"Reel generation failed for job {job_id}: {traceback.format_exc()}")
            await self._update_job(job_id, {
                "status": "failed",
                "progress": 0,
                "stage": f"Failed: {err_msg}"
            })
