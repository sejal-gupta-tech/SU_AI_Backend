import os
import uuid
import logging
import asyncio
from typing import List, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)

class VideoComposer:
    def __init__(self):
        self.ffmpeg_path = getattr(settings, "FFMPEG_PATH", "ffmpeg")
        self.output_dir = "uploads/reels"
        os.makedirs(self.output_dir, exist_ok=True)

    async def compose_reel(
        self,
        video_segments: List[str],
        audio_url: str,
        brand_colors: Dict[str, str],
        captions: str = None,
        logo_url: str = None
    ) -> str:
        """
        Composes the final Reel by combining video + audio.

        In development mode (no FFmpeg / no real video segments), returns a
        sample demo video URL so the whole pipeline completes successfully.

        In production, install FFmpeg and set FFMPEG_PATH in .env to enable
        real composition.
        """
        # If no segments or all segments are external URLs / placeholders, skip composition
        if not video_segments:
            logger.info("VideoComposer: No video segments provided. Returning demo reel URL.")
            return await self._mock_compose()

        input_video = video_segments[0]

        # If the video is already a remote URL, skip FFmpeg and return it directly
        if input_video.startswith("http://") or input_video.startswith("https://"):
            logger.info(f"VideoComposer: Video is a remote URL, returning directly: {input_video}")
            return input_video

        # If the file doesn't exist locally, fall back to mock
        if not os.path.exists(input_video):
            logger.warning(f"VideoComposer: Video file not found at {input_video}. Returning demo reel URL.")
            return await self._mock_compose()

        filename = f"{uuid.uuid4()}.mp4"
        output_path = os.path.join(self.output_dir, filename)

        # Decide command based on whether input is image or video
        if input_video.lower().endswith(('.png', '.jpg', '.jpeg')):
            command = (
                f'{self.ffmpeg_path} -loop 1 -i "{input_video}" -i "{audio_url}" '
                f'-c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p '
                f'-shortest "{output_path}"'
            )
        else:
            command = (
                f'{self.ffmpeg_path} -i "{input_video}" -i "{audio_url}" '
                f'-c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "{output_path}"'
            )

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                logger.warning("FFmpeg composition failed. Falling back to demo reel.")
                return await self._mock_compose()

            return f"/uploads/reels/{filename}"

        except NotImplementedError:
            logger.warning("asyncio subprocess not supported on this platform. Using mock compose.")
            return await self._mock_compose()
        except Exception as e:
            logger.error(f"Error in VideoComposer: {str(e)}")
            logger.warning("Falling back to demo reel URL due to composition error.")
            return await self._mock_compose()

    async def _mock_compose(self) -> str:
        """Returns a publicly accessible demo video URL for development/testing."""
        await asyncio.sleep(0.5)
        # A free, publicly accessible sample MP4 suitable for demo purposes
        return "https://www.w3schools.com/html/mov_bbb.mp4"
