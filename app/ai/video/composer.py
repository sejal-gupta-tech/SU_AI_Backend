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
        Composes the final Reel using FFmpeg.
        Combines the video segments, adds the voiceover, applies brand colors for text,
        and returns the path to the final MP4.
        """
        filename = f"{uuid.uuid4()}.mp4"
        output_path = os.path.join(self.output_dir, filename)
        
        # This is a simplified representation of what FFmpeg would do.
        # In a full implementation, you would construct a complex filtergraph
        # to concatenate video_segments, overlay captions, add the logo, and mix audio.
        
        try:
            if not video_segments:
                raise ValueError("No video segments provided for composition.")
                
            input_video = video_segments[0]  # Simplifying for the example
            
            # Basic FFmpeg command: mix one video with one audio
            command = f'{self.ffmpeg_path} -i "{input_video}" -i "{audio_url}" -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest "{output_path}"'
            
            # Fallback if the video segment is an image (creating a video from image)
            if input_video.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Create a loop of the image with the audio duration
                command = f'{self.ffmpeg_path} -loop 1 -i "{input_video}" -i "{audio_url}" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest "{output_path}"'
            
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                raise Exception("Video composition failed.")
                
            return f"/uploads/reels/{filename}"
            
        except Exception as e:
            logger.error(f"Error in VideoComposer: {str(e)}")
            raise e
