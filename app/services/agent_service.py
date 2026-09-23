import json
import logging
import re
from typing import Dict, Any, Optional

from app.ai.factory import AIProviderFactory
from app.services.business_service import BusinessService
from app.services.brand_service import get_brand_kit
from app.ai.services.post_generation import PostGenerationService
from app.services.reel_service import ReelService

logger = logging.getLogger(__name__)

class AgentService:
    """
    UNI AI Agent Service: Parses natural language inputs (Hindi/Hinglish)
    and routes them to the appropriate underlying AI generation tool.
    """

    async def parse_and_execute(self, db, user_id: str, command: str) -> Dict[str, Any]:
        """
        1. Parse the command using LLM to extract intent
        2. Fetch business context
        3. Execute the right tool
        4. Return the standard result format
        """
        # Fetch business context
        business = await BusinessService.get_business_by_owner(user_id)
        if not business:
            return {"success": False, "message": "Business profile not found. Please set it up first."}
            
        business_id = str(business.id)
        brand = await get_brand_kit(db, business_id) or {}
        language = getattr(business, "preferred_language", "Hinglish") or "Hinglish"
        
        # 1. Parse Intent
        intent_data = await self._parse_intent(command)
        
        if not intent_data or intent_data.get("action") == "unknown":
            return {
                "success": False,
                "action": "chat",
                "message": "I didn't quite get that. Try asking me to make a post, reel, or festival campaign!",
                "data": intent_data.get("reply", "")
            }

        action = intent_data["action"]
        topic = intent_data.get("topic", "")
        tone = intent_data.get("tone", "conversational")
        platform = intent_data.get("platform", "instagram")

        # Combine topic and tone into an instruction
        instruction = f"Topic: {topic}. Tone: {tone}. Note: Generate the content natively in {language} (if Hinglish/Hindi is requested, prioritize it)."

        business_dict = business.model_dump()
        business_dict["_id"] = str(business.id)

        try:
            if action == "create_post":
                # Mock a product context or search if needed
                product = {"name": "General", "description": topic}
                post_svc = PostGenerationService()
                result = await post_svc.generate_post(
                    business=business_dict,
                    brand=brand,
                    product=product,
                    platform=platform,
                    objective="engagement",
                    language=language,
                    additional_instruction=instruction
                )
                return {
                    "success": True,
                    "action": "create_post",
                    "data": result
                }

            elif action == "create_reel":
                from app.services.reel_script_service import ReelScriptService
                script_svc = ReelScriptService()
                product = {"name": "General", "description": topic}
                script = await script_svc.generate_script(
                    product=product,
                    brand=brand,
                    objective="engagement",
                    platform=platform,
                    language=language,
                    duration=30,
                    tone=tone,
                    additional_instruction=instruction
                )
                script_dict = script.model_dump()
                return {
                    "success": True,
                    "action": "create_reel",
                    "data": {
                        "title": script_dict.get("title", ""),
                        "hook": script_dict.get("hook", ""),
                        "cta": script_dict.get("cta", ""),
                        "caption": script_dict.get("caption", ""),
                        "hashtags": script_dict.get("hashtags", []),
                        "scenes": script_dict.get("scenes", []),
                        "voiceover": " ".join(
                            s.get("voiceover", "") for s in script_dict.get("scenes", [])
                        ),
                        "script": "\n\n".join(
                            f"Scene {s.get('scene_number','')}: {s.get('visual','')} | {s.get('voiceover','')}"
                            for s in script_dict.get("scenes", [])
                        ),
                    }
                }
                
            elif action == "generate_festival_campaign":
                from app.services.festival_service import get_upcoming_festivals, generate_festival_campaign
                upcoming = get_upcoming_festivals(days_ahead=60)
                # Find matching festival or just pick the next one
                target_fest = next((f for f in upcoming if f["name"].lower() in topic.lower()), None)
                if not target_fest and upcoming:
                    target_fest = upcoming[0]
                    
                if target_fest:
                    campaign = await generate_festival_campaign(db, business_id, target_fest)
                    if campaign:
                        return {
                            "success": True,
                            "action": "generate_festival_campaign",
                            "data": campaign
                        }
                        
                return {
                    "success": False,
                    "action": "generate_festival_campaign",
                    "message": f"Could not find or generate a campaign for {topic}."
                }

            else:
                return {
                    "success": False,
                    "action": action,
                    "message": "Action not supported yet."
                }

        except Exception as e:
            logger.error(f"Error executing agent action {action}: {str(e)}")
            return {
                "success": False,
                "action": action,
                "message": f"Execution failed: {str(e)}"
            }

    async def _parse_intent(self, command: str) -> Optional[Dict[str, Any]]:
        system_prompt = """
You are an intelligent Intent Parser for a marketing AI tool.
The user will provide a command in Hindi, Hinglish, or English.
Analyze the command and output ONLY a JSON object with the following schema:

{
  "action": "create_post" | "create_reel" | "create_ad" | "generate_festival_campaign" | "unknown",
  "topic": "extracted topic or subject matter",
  "tone": "extracted tone (e.g. professional, funny, zabardast/energetic)",
  "platform": "instagram" | "facebook" | "linkedin",
  "reply": "If unknown, a short polite reply in Hinglish asking for clarification"
}

Example: "Bhai mere kapde ke business ke liye ek zabardast reel bana"
Output: {"action": "create_reel", "topic": "kapde ka business", "tone": "zabardast", "platform": "instagram"}
        """
        
        provider = AIProviderFactory.get_provider()
        try:
            res = await provider.generate_text(
                prompt=command,
                system_prompt=system_prompt.strip(),
                max_tokens=500
            )
            raw = res.get("text", "{}").strip()
            
            # Clean up Qwen/Markdown wrappers
            raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()
            if "```" in raw:
                parts = raw.split("```")
                for part in parts:
                    cleaned = part.strip()
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:].strip()
                    if cleaned.startswith("{"):
                        raw = cleaned
                        break
                        
            first_brace = raw.find("{")
            last_brace = raw.rfind("}")
            if first_brace != -1 and last_brace != -1:
                raw = raw[first_brace:last_brace + 1]
                
            return json.loads(raw)
        except Exception as e:
            logger.error(f"Failed to parse intent: {e}")
            return None
