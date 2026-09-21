from typing import Dict, Any
import logging
from groq import AsyncGroq
from app.ai.base import AIProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class GroqProvider(AIProvider):
    """
    Groq LLM integration.
    """
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing from configuration.")
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        
    async def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Enforce JSON output for prompts that expect it
            # since the MockAIProvider returned a JSON string in "text"
            # It's better to tell the model to output JSON if "json" is in kwargs or if we just want JSON.
            
            # The prompt builder in app.ai.prompts.post might already have instructed it to output JSON.
            # Using response_format={"type": "json_object"} if the model supports it.
            
            completion_kwargs = {
                "messages": messages,
                "model": self.model,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1024)
            }
            
            if "response_format" in kwargs:
                completion_kwargs["response_format"] = kwargs["response_format"]
            
            response = await self.client.chat.completions.create(**completion_kwargs)
            
            content = response.choices[0].message.content
            
            return {
                "text": content,
                "metadata": {
                    "provider": "groq",
                    "model": self.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
            }
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            raise RuntimeError(f"AI generation failed: {str(e)}")
