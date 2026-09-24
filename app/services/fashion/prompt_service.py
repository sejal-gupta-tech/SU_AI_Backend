"""
Fashion AI Prompt Service
Converts structured photoshoot config into professional fashion photography prompts.
The frontend never constructs the final AI prompt directly.
"""
from typing import Optional


# Configuration-driven style/pose/background descriptors
_POSE_DESCRIPTIONS = {
    "standing": "standing upright in a confident pose, weight evenly distributed",
    "walking": "mid-stride walking pose, natural movement, dynamic energy",
    "sitting": "seated in a relaxed, natural sitting position",
    "hands_in_pockets": "standing with both hands casually in pockets, relaxed posture",
    "crossed_arms": "standing with arms crossed confidently, strong presence",
    "looking_left": "standing, head and gaze turned naturally to the left",
    "looking_right": "standing, head and gaze turned naturally to the right",
    "custom": None,  # Will use custom_pose_description
}

_BACKGROUND_DESCRIPTIONS = {
    "studio": "clean professional photography studio, seamless white/grey background, soft diffused lighting",
    "street": "urban street environment, city sidewalk, modern architecture in background",
    "cafe": "stylish modern cafe interior, warm ambient lighting, coffee shop atmosphere",
    "office": "contemporary office space, professional environment, clean modern interior",
    "home": "cozy modern home interior, natural living space, warm lighting",
    "beach": "sandy beach, ocean in background, natural sunlight, warm golden tones",
    "luxury_store": "high-end luxury boutique interior, elegant displays, premium atmosphere",
    "gym": "modern fitness center, professional gym equipment in background",
    "outdoor": "outdoor natural setting, open sky, fresh natural environment",
    "custom": None,  # Will use custom_background_description
}

_SHOT_DESCRIPTIONS = {
    "full_body": "full-body shot showing the complete outfit from head to toe",
    "upper_body": "upper-body shot from waist up, showing the garment clearly",
    "close_up": "close-up shot focusing on the garment details, fabric texture, and design elements",
}

_VIEW_DESCRIPTIONS = {
    "front": "front-facing camera angle, model facing directly towards the camera",
    "back": "back view angle, model turned with back towards camera, showing rear of garment",
    "side": "side profile angle, model turned 90 degrees, side profile visible",
}

_MODEL_STYLE_DESCRIPTIONS = {
    # Male styles
    "casual": "casually styled, relaxed everyday look",
    "streetwear": "streetwear styled, urban fashion aesthetic, edgy and contemporary",
    "luxury": "luxury fashion styled, high-end sophisticated look, premium aesthetic",
    "fitness": "fitness/athletic styled, sporty energetic look",
    # Female styles
    "fashion": "high fashion editorial styled, sophisticated and elegant",
}


def build_fashion_photoshoot_prompt(
    *,
    product_name: str,
    category: str,
    color: str,
    gender: str,
    model_type: str,
    model_style: str,
    pose: str,
    background: str,
    location: Optional[str],
    shot_type: str,
    view: str,
    custom_pose_description: Optional[str] = None,
    custom_background_description: Optional[str] = None,
) -> str:
    """
    Builds a professional fashion photography prompt from structured parameters.
    All AI prompt construction happens here - never on the frontend.
    """

    # Resolve descriptions
    pose_desc = _POSE_DESCRIPTIONS.get(pose, pose)
    if pose == "custom" and custom_pose_description:
        pose_desc = custom_pose_description

    bg_desc = _BACKGROUND_DESCRIPTIONS.get(background, background)
    if background == "custom" and custom_background_description:
        bg_desc = custom_background_description

    shot_desc = _SHOT_DESCRIPTIONS.get(shot_type, shot_type)
    view_desc = _VIEW_DESCRIPTIONS.get(view, view)
    style_desc = _MODEL_STYLE_DESCRIPTIONS.get(model_style, model_style)

    # Location context
    location_context = f" in {location}" if location else ""

    # Model description
    model_gender_map = {"male": "male model", "female": "female model"}
    model_desc = model_gender_map.get(model_type, "fashion model")

    prompt = f"""Photorealistic professional fashion photography, {shot_desc}, {view_desc}.

Subject: A {model_desc}, {style_desc}, {pose_desc}.

Garment: The model is wearing a {color} {product_name} ({category}). 
CRITICAL GARMENT REQUIREMENTS:
- Preserve the EXACT color: {color}
- Preserve ALL design details, logos, prints, patterns exactly as they appear
- Show realistic fabric folds, draping and texture
- Correct garment placement on the body
- Accurate neckline, sleeve length, and fit
- Realistic shadows and fabric highlights
- Do NOT alter or modify the clothing design in any way

Setting: {bg_desc}{location_context}.

Technical Requirements:
- Photorealistic commercial fashion photography quality
- Natural body proportions and skin tones
- Realistic studio-quality lighting
- Sharp focus on the garment
- 4K resolution, hyperrealistic
- Professional commercial photography
- Natural pose, realistic shadows
- Correct human anatomy"""

    # Add negative guidance as annotation
    prompt += """

Style: Editorial fashion magazine quality, photorealistic, commercial product photography, ultra-detailed."""

    return prompt.strip()


def build_fashion_negative_prompt() -> str:
    """Returns a standard negative prompt for fashion photoshoot generation."""
    return (
        "cartoon, anime, illustration, painting, drawing, sketch, CGI, render, "
        "3D, unrealistic, distorted face, deformed body, extra limbs, missing limbs, "
        "blurry, out of focus, low quality, artifacts, watermark, text, logo on image, "
        "changed clothing design, different color clothing, modified garment, "
        "wrong garment, different outfit, nsfw, nude"
    )


def build_tryon_prompt(
    *,
    product_name: str,
    category: str,
    color: str,
) -> str:
    """Builds a virtual try-on instruction prompt for the AI provider."""
    return (
        f"Virtual try-on: Dress the person in the provided garment image. "
        f"The garment is a {color} {product_name} ({category}). "
        f"Preserve the person's face, skin tone, body shape, and identity exactly. "
        f"Preserve the garment's exact color ({color}), design, logo, pattern, "
        f"fabric texture, sleeve length, neckline, and fit. "
        f"Show realistic fabric folds and natural body proportions. "
        f"Photorealistic result, natural lighting, commercial fashion quality."
    )
