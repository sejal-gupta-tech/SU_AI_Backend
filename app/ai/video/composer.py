import os
import uuid
import logging
import asyncio
import httpx
from typing import List, Dict, Any
from app.core.config import settings
try:
    import imageio_ffmpeg
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False

logger = logging.getLogger(__name__)

class VideoComposer:
    def __init__(self):
        self.output_dir = "uploads/reels"
        self.temp_dir = "uploads/temp"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        self.bgm_path = "assets/music/bgm.ogg"

    def _format_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds - int(seconds)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    def _generate_srt(self, script: Any, output_path: str):
        scenes = script.scenes if hasattr(script, "scenes") else script.get("scenes", [])
        with open(output_path, "w", encoding="utf-8") as f:
            current_time = 0
            for i, scene in enumerate(scenes):
                duration = scene.duration_seconds if hasattr(scene, "duration_seconds") else scene.get("duration_seconds", 5)
                text = scene.on_screen_text if hasattr(scene, "on_screen_text") else scene.get("on_screen_text", "")
                if not text:
                    text = scene.voiceover if hasattr(scene, "voiceover") else scene.get("voiceover", "")
                
                # word wrap logic roughly
                words = text.split()
                wrapped = []
                line = ""
                for w in words:
                    if len(line) + len(w) > 30:
                        wrapped.append(line)
                        line = w + " "
                    else:
                        line += w + " "
                wrapped.append(line)
                text = "\n".join([ln.strip() for ln in wrapped if ln.strip()])
                
                start_str = self._format_time(current_time)
                end_str = self._format_time(current_time + duration)
                
                f.write(f"{i+1}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{text}\n\n")
                
                current_time += duration

    async def _download_file(self, url: str, path: str):
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            res.raise_for_status()
            with open(path, "wb") as f:
                f.write(res.content)

    async def compose_reel(
        self,
        video_segments: List[str],
        audio_url: str,
        brand_colors: Dict[str, str],
        captions: str = None,
        logo_url: str = None,
        script: Any = None
    ) -> str:
        if not HAS_FFMPEG:
            logger.error("imageio-ffmpeg is not installed.")
            raise Exception("FFmpeg not available for composition")

        if not video_segments or not video_segments[0]:
            raise Exception("No visual assets provided for composition")

        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        job_id = str(uuid.uuid4())
        
        # Resolve files
        primary_image = video_segments[0]
        local_img = os.path.join(self.temp_dir, f"{job_id}_img.jpg")
        if primary_image.startswith("http"):
            await self._download_file(primary_image, local_img)
        else:
            # If it's a relative path like /uploads/..., use it directly
            local_img = primary_image.lstrip("/")
            
        local_audio = audio_url.lstrip("/") if audio_url else None
        
        srt_path = os.path.join(self.temp_dir, f"{job_id}.srt")
        if script:
            self._generate_srt(script, srt_path)
            # FFmpeg requires forward slashes and escaped colons for subtitles filter path on Windows
            srt_filter_path = srt_path.replace("\\", "/").replace(":", "\\:")
        else:
            srt_filter_path = None
            
        out_filename = f"{job_id}.mp4"
        output_path = os.path.join(self.output_dir, out_filename)
        
        total_duration = script.duration_seconds if hasattr(script, "duration_seconds") else script.get("duration_seconds", 15)

        # Build FFmpeg command
        # 1. Loop image
        cmd = [ffmpeg_exe, "-y", "-loop", "1", "-t", str(total_duration), "-i", local_img]
        
        # 2. Voiceover audio
        if local_audio and os.path.exists(local_audio):
            cmd.extend(["-i", local_audio])
        else:
            # Silent audio if no voiceover
            cmd.extend(["-f", "lavfi", "-t", str(total_duration), "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"])
            
        # 3. Background music
        has_bgm = os.path.exists(self.bgm_path)
        if has_bgm:
            cmd.extend(["-stream_loop", "-1", "-i", self.bgm_path])
            
        # 4. Filter complex
        # Video: scale to 9:16 (720x1280) and add subtitles
        vf = "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:-1:-1:color=black"
        if srt_filter_path:
            vf += f",subtitles='{srt_filter_path}':force_style='Fontsize=24,PrimaryColour=&H00FFFFFF,BorderStyle=3,Outline=2,Shadow=0'"
            
        # Audio: mix voice (1) and bgm (2)
        if has_bgm:
            af = "[1:a]volume=1.0[voice];[2:a]volume=0.1[bgm];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=2[a]"
        else:
            af = "[1:a]volume=1.0[a]"
            
        cmd.extend([
            "-filter_complex", f"[0:v]{vf}[v];{af}",
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ])
        
        logger.info(f"Running FFmpeg: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"FFmpeg error: {stderr.decode()}")
            raise Exception("FFmpeg video composition failed")
            
        return f"/{self.output_dir}/{out_filename}"
