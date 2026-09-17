import json

def get_reel_script_prompt(
    product: dict,
    brand: dict,
    objective: str,
    platform: str,
    duration: int,
    language: str,
    tone: str,
    offer: str = None,
    additional_instruction: str = None
) -> str:
    prompt = f"""
You are an expert AI Video Producer and Copywriter creating a highly engaging Reel script.

# CONTEXT
Product: {json.dumps(product, default=str)}
Brand: {json.dumps(brand, default=str)}
Objective: {objective}
Platform: {platform}
Duration: {duration} seconds
Language: {language}
Tone: {tone}
"""
    if offer:
        prompt += f"Offer: {offer}\n"
    if additional_instruction:
        prompt += f"Additional Instructions: {additional_instruction}\n"

    prompt += """
# INSTRUCTIONS
1. Create a dynamic and engaging script for a short-form vertical video (Reel).
2. The output MUST be valid JSON matching the exact schema below.
3. The total duration of all scenes must closely match the requested duration.
4. Voiceover text should sound natural in the specified language and tone.
5. Provide compelling on_screen_text that highlights key value props.
6. The final CTA should encourage action related to the objective.

# OUTPUT JSON SCHEMA
{
  "title": "string (Catchy internal title)",
  "objective": "string",
  "hook": "string (The opening hook to grab attention in first 3 seconds)",
  "duration_seconds": integer,
  "language": "string",
  "tone": "string",
  "scenes": [
    {
      "scene_number": integer,
      "duration_seconds": integer (Length of this specific scene),
      "visual": "string (Description of what is shown on screen)",
      "voiceover": "string (What the voiceover says during this scene)",
      "on_screen_text": "string (Text overlay for this scene, keep it short)",
      "transition": "string (e.g., fade, slide, none)"
    }
  ],
  "cta": "string (Short Call To Action text)",
  "caption": "string (The social media caption text)",
  "hashtags": ["string", "string"]
}

Output ONLY valid JSON. Do not include markdown formatting like ```json or any conversational text.
"""
    return prompt
