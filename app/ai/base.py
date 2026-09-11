from abc import ABC, abstractmethod
from typing import Dict, Any

class AIProvider(ABC):
    """
    Abstract base class for all AI providers.
    Ensures that the rest of the application remains independent of the specific AI provider.
    """
    
    @abstractmethod
    async def generate_text(self, prompt: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """
        Generates text based on the given prompt.
        
        Args:
            prompt: The main user prompt.
            system_prompt: Optional system instructions.
            **kwargs: Additional provider-specific arguments (temperature, max_tokens, etc).
            
        Returns:
            A dictionary containing the generated text and any metadata (like usage).
        """
        pass
    
    # Future methods to be implemented:
    # @abstractmethod
    # async def generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]: pass
    #
    # @abstractmethod
    # async def generate_video(self, prompt: str, **kwargs) -> Dict[str, Any]: pass
