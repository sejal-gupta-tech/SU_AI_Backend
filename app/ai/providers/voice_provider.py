import os
import uuid
import logging
import asyncio
from abc import ABC, abstractmethod
from app.core.config import settings

logger = logging.getLogger(__name__)

class VoiceProvider(ABC):
    @abstractmethod
    async def generate_audio(self, text: str, language: str, voice: str, speed: float = 1.0) -> str:
        pass


class MockVoiceProvider(VoiceProvider):
    """
    A mock voice provider that simulates TTS generation.
    Returns a placeholder audio URL without requiring any local tools.
    Replace this with a real API-based TTS provider (ElevenLabs, Google TTS, Azure TTS, etc.)
    when you have the credentials.
    """
    async def generate_audio(self, text: str, language: str, voice: str, speed: float = 1.0) -> str:
        logger.info(f"MockVoiceProvider: Simulating TTS for language={language}, voice={voice}")
        # Simulate a small delay like a real API call
        await asyncio.sleep(0.5)
        # Return a placeholder audio URL
        fake_filename = f"{uuid.uuid4()}.mp3"
        return f"/uploads/audio/{fake_filename}"


class PiperVoiceProvider(VoiceProvider):
    """
    Piper TTS provider - requires piper binary and voice models installed locally.
    NOTE: This does NOT work on Windows due to asyncio subprocess limitations.
    Use MockVoiceProvider or an API-based provider instead.
    """
    def __init__(self):
        self.piper_path = getattr(settings, "PIPER_PATH", "piper")
        self.voices_dir = getattr(settings, "PIPER_VOICES_DIR", "./piper_voices")
        self.output_dir = "uploads/audio"
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_audio(self, text: str, language: str, voice: str, speed: float = 1.0) -> str:
        filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(self.output_dir, filename)

        voice_model_path = os.path.join(self.voices_dir, f"{voice}.onnx")
        if not os.path.exists(voice_model_path):
            logger.warning(f"Piper voice model {voice_model_path} not found. Falling back to mock.")
            # Fall back to mock instead of crashing
            mock = MockVoiceProvider()
            return await mock.generate_audio(text, language, voice, speed)

        command = f'echo "{text}" | {self.piper_path} --model {voice_model_path} --output_file {output_path}'

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"Piper error: {stderr.decode()}")
                raise Exception("Voice generation failed.")

            return f"/uploads/audio/{filename}"

        except NotImplementedError:
            logger.warning("asyncio subprocess not supported on this platform. Using MockVoiceProvider.")
            mock = MockVoiceProvider()
            return await mock.generate_audio(text, language, voice, speed)
        except Exception as e:
            logger.error(f"Error in PiperVoiceProvider: {str(e)}")
            raise e


def get_voice_provider() -> VoiceProvider:
    provider_name = getattr(settings, "VOICE_PROVIDER", "mock").lower()
    if provider_name == "piper":
        return PiperVoiceProvider()
    else:
        # Default to mock for easy development/testing
        return MockVoiceProvider()
