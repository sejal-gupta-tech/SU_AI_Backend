import asyncio
from app.ai.factory import AIProviderFactory
from app.core.config import settings

async def main():
    settings.AI_PROVIDER = "groq"
    provider = AIProviderFactory.get_provider()
    
    print(f"Provider class: {provider.__class__.__name__}")
    
    response = await provider.generate_text(prompt="Write a short social media caption for a coffee shop.")
    print(response["text"])

if __name__ == '__main__':
    asyncio.run(main())