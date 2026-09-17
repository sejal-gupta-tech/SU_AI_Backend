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

class PiperVoiceProvider(VoiceProvider):
    def __init__(self):
        self.piper_path = getattr(settings, "PIPER_PATH", "piper")
        self.voices_dir = getattr(settings, "PIPER_VOICES_DIR", "./piper_voices")
        self.output_dir = "uploads/audio"
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def generate_audio(self, text: str, language: str, voice: str, speed: float = 1.0) -> str:
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(self.output_dir, filename)
        
        # Select voice model based on language (this is a simplified mapping, should be configurable)
        # Default piper models have specific names, assuming `en_US-lessac-medium.onnx` as default
        voice_model_path = os.path.join(self.voices_dir, f"{voice}.onnx")
        
        if not os.path.exists(voice_model_path):
            logger.warning(f"Piper voice model {voice_model_path} not found. Attempting to use default.")
            voice_model_path = os.path.join(self.voices_dir, "en_US-lessac-medium.onnx")
            
        command = f'echo "{text}" | {self.piper_path} --model {voice_model_path} --output_file {output_path}'
        
        try:
            # We use a shell command to pipe text to piper
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Piper error: {stderr.decode()}")
                raise Exception("Voice generation failed.")
                
            # Return relative URL path
            return f"/uploads/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Error in PiperVoiceProvider: {str(e)}")
            raise e

def get_voice_provider() -> VoiceProvider:
    provider_name = getattr(settings, "VOICE_PROVIDER", "piper").lower()
    if provider_name == "piper":
        return PiperVoiceProvider()
    else:
        # Fallback or other providers
        return PiperVoiceProvider()
