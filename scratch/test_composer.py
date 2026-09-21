import asyncio
import os
from app.ai.video.composer import VideoComposer

async def test():
    composer = VideoComposer()
    img_url = "https://image.pollinations.ai/prompt/test?width=1024&height=1024&nologo=true"
    audio_url = "" # silent
    try:
        out = await composer.compose_reel(
            video_segments=[img_url],
            audio_url=audio_url,
            brand_colors={},
            script={} 
        )
        print("Success:", out)
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(test())
