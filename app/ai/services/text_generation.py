import json
from pydantic import ValidationError
from app.ai.factory import AIProviderFactory
from app.ai.services.prompt_builder import PromptBuilder
from app.schemas.ai import CaptionResponse
from app.utils.errors import AIGenerationError

class TextGenerationService:
    @staticmethod
    async def generate_caption(
        context: dict,
        product_id: str,
        objective: str,
        tone: str,
        language: str,
        offer: str,
        cta: str
    ) -> CaptionResponse:
        system_prompt, user_prompt = PromptBuilder.build_caption_prompt(
            context=context,
            product_id=product_id,
            objective=objective,
            tone=tone,
            language=language,
            offer=offer,
            cta=cta
        )
        
        provider = AIProviderFactory.get_provider()
        
        try:
            response = await provider.generate_text(prompt=user_prompt, system_prompt=system_prompt)
            raw_text = response.get("text", "")
            
            # Extract JSON from potential markdown blocks if provider returned that
            if raw_text.startswith("```json"):
                raw_text = raw_text.strip("```json").strip("```").strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text.strip("```").strip()
                
            parsed_data = json.loads(raw_text)
            
            # Validate output using Pydantic
            validated_output = CaptionResponse(**parsed_data)
            return validated_output, response.get("metadata", {})
            
        except json.JSONDecodeError as e:
            raise AIGenerationError("Failed to parse AI output into structured format.") from e
        except ValidationError as e:
            raise AIGenerationError(f"AI output failed validation: {str(e)}") from e
        except Exception as e:
            raise AIGenerationError(f"AI generation failed: {str(e)}") from e
