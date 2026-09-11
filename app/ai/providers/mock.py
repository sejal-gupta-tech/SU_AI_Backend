from typing import Dict, Any
import asyncio
from app.ai.base import AIProvider

class MockAIProvider(AIProvider):
    """
    A mock provider for development and testing.
    Returns deterministic structured text data without calling any external API.
    """
    
    async def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        # Simulate network delay
        await asyncio.sleep(1.0)
        
        # We can inspect the prompt to return slightly different mock data if we want,
        # but returning a solid deterministic structure is enough for the frontend.
        mock_response = {
            "caption": "Experience premium quality with our latest collection. 🌟 Don't miss out on this exclusive offer! Elevate your style today.",
            "hashtags": ["#PremiumQuality", "#NewArrival", "#Fashion", "#ExclusiveOffer"],
            "cta": "Shop Now"
        }
        
        import json
        text_content = json.dumps(mock_response)
        
        return {
            "text": text_content,
            "metadata": {
                "provider": "mock",
                "model": "mock-model-v1",
                "usage": {
                    "prompt_tokens": len(prompt) // 4,
                    "completion_tokens": len(text_content) // 4,
                    "total_tokens": (len(prompt) + len(text_content)) // 4
                }
            }
        }
