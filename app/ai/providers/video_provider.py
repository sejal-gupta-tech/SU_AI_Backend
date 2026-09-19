import logging
import asyncio
import uuid
import os
from abc import ABC, abstractmethod
from app.core.config import settings

logger = logging.getLogger(__name__)

class VideoProvider(ABC):
    @abstractmethod
    async def generate_video(self, image_url: str, prompt: str, duration: int) -> str:
        """Starts video generation and returns a job ID."""
        pass

    @abstractmethod
    async def get_status(self, job_id: str) -> dict:
        """Returns status of the video generation."""
        pass

    @abstractmethod
    async def get_result(self, job_id: str) -> str:
        """Returns the final video URL."""
        pass


class MockVideoProvider(VideoProvider):
    """
    Mock video provider for development/testing.
    Returns a placeholder video URL without requiring a real video API key.
    Replace with a real provider (Runway ML, Luma, Replicate, etc.) when you have credentials.
    """
    async def generate_video(self, image_url: str, prompt: str, duration: int) -> str:
        logger.info(f"MockVideoProvider: Simulating video generation for prompt={prompt[:50]}...")
        await asyncio.sleep(1)  # Simulate API call delay
        return str(uuid.uuid4())  # Return a fake job ID

    async def get_status(self, job_id: str) -> dict:
        return {"status": "completed", "progress": 100}

    async def get_result(self, job_id: str) -> str:
        # Return a publicly accessible sample video for demo/testing
        return "https://www.w3schools.com/html/mov_bbb.mp4"


class ExternalVideoProvider(VideoProvider):
    """
    Placeholder for an actual external Video API (like Runway ML, Luma, Replicate, etc.).
    Requires VIDEO_API_KEY to be set in .env
    Falls back to MockVideoProvider if the key is missing.
    """
    def __init__(self):
        self.api_key = getattr(settings, "VIDEO_API_KEY", None)
        if not self.api_key:
            logger.warning("VIDEO_API_KEY is not configured. Using MockVideoProvider as fallback.")
            self._mock = MockVideoProvider()
        else:
            self._mock = None

    async def generate_video(self, image_url: str, prompt: str, duration: int) -> str:
        if self._mock:
            return await self._mock.generate_video(image_url, prompt, duration)

        # Real implementation would go here:
        # response = await client.post("https://api.videoprovider.com/generate", json={...})
        # return response.json()["id"]
        return str(uuid.uuid4())

    async def get_status(self, job_id: str) -> dict:
        if self._mock:
            return await self._mock.get_status(job_id)
        # response = await client.get(f"https://api.videoprovider.com/status/{job_id}")
        # return response.json()
        return {"status": "completed", "progress": 100}

    async def get_result(self, job_id: str) -> str:
        if self._mock:
            return await self._mock.get_result(job_id)
        # response = await client.get(f"https://api.videoprovider.com/result/{job_id}")
        # return response.json()["video_url"]
        return "https://www.w3schools.com/html/mov_bbb.mp4"


def get_video_provider() -> VideoProvider:
    provider_name = getattr(settings, "VIDEO_PROVIDER", "mock").lower()
    if provider_name == "mock":
        return MockVideoProvider()
    return ExternalVideoProvider()
