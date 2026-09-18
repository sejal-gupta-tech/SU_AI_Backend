import httpx
from fastapi import HTTPException
from bson import ObjectId

class SocialService:
    @staticmethod
    async def publish_to_whatsapp(db, business_id: str, content_id: str, target_phone: str):
        # 1. Get the business credentials
        business = await db["businesses"].find_one({"_id": ObjectId(business_id)})
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        whatsapp_phone_id = business.get("whatsapp_phone_id")
        whatsapp_token = business.get("whatsapp_token")
        
        if not whatsapp_phone_id or not whatsapp_token:
            raise HTTPException(status_code=400, detail="WhatsApp is not connected for this business. Please configure it in settings.")
            
        # 2. Get the content
        content = await db["contents"].find_one({
            "_id": ObjectId(content_id),
            "business_id": business_id
        })
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
            
        caption = content.get("caption", "New Post!")
        hashtags = content.get("hashtags", "")
        full_text = f"{caption}\n\n{hashtags}"
        
        image_url = content.get("image_url") # If it's a post
        
        # 3. Call the WhatsApp Cloud API
        url = f"https://graph.facebook.com/v19.0/{whatsapp_phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        # If we have an image, send an image message. Otherwise text.
        if image_url and not "pollinations.ai" in image_url: # Note: WhatsApp doesn't support some dynamic URLs well
            payload = {
                "messaging_product": "whatsapp",
                "to": target_phone,
                "type": "image",
                "image": {
                    "link": image_url,
                    "caption": full_text
                }
            }
        else:
            # Fallback to simple text for mock/demo purposes
            payload = {
                "messaging_product": "whatsapp",
                "to": target_phone,
                "type": "text",
                "text": {
                    "body": full_text
                }
            }
            
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Catch Meta Graph API errors
                err_detail = e.response.json()
                print(f"WhatsApp API Error: {err_detail}")
                raise HTTPException(status_code=400, detail=f"WhatsApp API Error: {err_detail.get('error', {}).get('message', str(e))}")
            except Exception as e:
                print(f"Failed to send WhatsApp message: {e}")
                raise HTTPException(status_code=500, detail="Failed to communicate with WhatsApp API")

    @staticmethod
    async def publish_to_instagram(db, business_id: str, content_id: str):
        business = await db["businesses"].find_one({"_id": ObjectId(business_id)})
        if not business:
            raise HTTPException(status_code=404, detail="Business not found")
            
        ig_account_id = business.get("ig_account_id")
        ig_access_token = business.get("ig_access_token")
        
        if not ig_account_id or not ig_access_token:
            raise HTTPException(status_code=400, detail="Instagram is not connected for this business.")
            
        content = await db["contents"].find_one({
            "_id": ObjectId(content_id),
            "business_id": business_id
        })
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
            
        image_url = content.get("image_url")
        caption = content.get("caption", "")
        hashtags = content.get("hashtags", "")
        full_caption = f"{caption}\n\n{hashtags}"
        
        if not image_url:
            raise HTTPException(status_code=400, detail="Content must have an image_url to publish to Instagram.")
            
        async with httpx.AsyncClient() as client:
            try:
                # 1. Create Media Container
                create_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media"
                payload = {
                    "image_url": image_url,
                    "caption": full_caption,
                    "access_token": ig_access_token
                }
                res = await client.post(create_url, params=payload)
                res.raise_for_status()
                creation_id = res.json().get("id")
                
                # 2. Publish Media Container
                publish_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media_publish"
                pub_payload = {
                    "creation_id": creation_id,
                    "access_token": ig_access_token
                }
                pub_res = await client.post(publish_url, params=pub_payload)
                pub_res.raise_for_status()
                
                return {"success": True, "ig_post_id": pub_res.json().get("id")}
                
            except httpx.HTTPStatusError as e:
                err_detail = e.response.json()
                print(f"Instagram API Error: {err_detail}")
                raise HTTPException(status_code=400, detail=f"Instagram API Error: {err_detail.get('error', {}).get('message', str(e))}")
            except Exception as e:
                print(f"Failed to publish to Instagram: {e}")
                raise HTTPException(status_code=500, detail="Failed to communicate with Instagram API")
