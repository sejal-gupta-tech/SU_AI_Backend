import io
import aiohttp
from PIL import Image, ImageDraw, ImageFont

class ImageComposer:
    
    @staticmethod
    async def generate_banner(
        product_image_url: str,
        headline: str,
        cta: str,
        brand_colors: dict,
    ) -> str:
        try:
            # 1. Download product image
            # If the URL is relative or localhost, we need to handle it or assume it's valid
            if product_image_url.startswith("/"):
                product_image_url = f"http://127.0.0.1:8000{product_image_url}"
                
            async with aiohttp.ClientSession() as session:
                async with session.get(product_image_url) as response:
                    if response.status == 200:
                        img_data = await response.read()
                        product_img = Image.open(io.BytesIO(img_data)).convert("RGBA")
                    else:
                        raise ValueError(f"Failed to fetch product image: {response.status}")

            # 2. Create base canvas (1080x1080 for Instagram post)
            bg_color = brand_colors.get("primary", "#ffffff")
            if not bg_color.startswith("#"):
                bg_color = "#" + bg_color
            
            canvas = Image.new("RGB", (1080, 1080), color=bg_color)
            
            # 3. Resize and paste product image
            # Make product fill around 70% of the canvas height
            target_height = int(1080 * 0.7)
            ratio = target_height / product_img.height
            target_width = int(product_img.width * ratio)
            
            product_img = product_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Center it
            x_offset = (1080 - target_width) // 2
            y_offset = (1080 - target_height) // 2
            
            # Create a blank image same size as canvas for alpha composite
            temp = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            temp.paste(product_img, (x_offset, y_offset))
            canvas = Image.alpha_composite(canvas.convert("RGBA"), temp).convert("RGB")
            
            # 4. Draw text
            draw = ImageDraw.Draw(canvas)
            
            font = ImageFont.load_default()
            
            cta_bg = brand_colors.get("secondary", "#000000")
            if not cta_bg.startswith("#"):
                cta_bg = "#" + cta_bg
                
            draw.rectangle([(100, 900), (980, 1000)], fill=cta_bg)
            
            # Very basic text overlay
            draw.text((120, 940), f"{headline} | {cta}", fill="white", font=font)
            
            # 5. Save locally and return URL
            import uuid
            import os
            
            filename = f"{uuid.uuid4().hex}.jpg"
            # Assuming uploads directory is in the root of SU_AI_Backend
            save_dir = os.path.join(os.getcwd(), "uploads")
            os.makedirs(save_dir, exist_ok=True)
            
            filepath = os.path.join(save_dir, filename)
            canvas.save(filepath, "JPEG", quality=90)
            
            return f"http://127.0.0.1:8000/uploads/{filename}"
            
        except Exception as e:
            print(f"Image composition failed: {e}")
            return product_image_url  # Fallback to original
