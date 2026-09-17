import httpx


class ImageGenerator:

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    async def generate(
        self,
        prompt: str,
        product_image: str | None = None,
    ):
        payload = {
            "prompt": prompt,
        }

        if product_image:
            payload["product_image"] = product_image

        if self.api_key == "your_api_key_here" or not self.api_key:
            import urllib.parse
            import re
            
            clean_prompt = prompt
            product_match = re.search(r'Product:\s*(.*?)\n', prompt)
            style_match = re.search(r'Photography Style:\s*(.*?)\n', prompt)
            bg_match = re.search(r'Background:\s*(.*?)\n', prompt)
            
            if product_match and style_match and bg_match:
                prod = product_match.group(1).strip()
                style = style_match.group(1).strip()
                bg = bg_match.group(1).strip()
                
                # Format perfectly for Stable Diffusion
                clean_prompt = f"Professional product photography of a {prod}, {style} style, {bg} background, highly detailed, photorealistic, 8k resolution, commercial studio lighting"
                
                # Ensure no faces if model is not specified
                if "No model" in prompt:
                    clean_prompt += ", no people, no humans, product only"
            else:
                clean_prompt = prompt.replace('\n', ' ')

            safe_prompt = urllib.parse.quote(clean_prompt[:800])
            return {
                "image_url": f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
            }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                self.api_url,
                json=payload,
                headers=headers,
            )

            response.raise_for_status()

            return response.json()
