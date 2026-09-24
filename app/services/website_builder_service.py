from bson import ObjectId
from datetime import datetime, timezone
import json
import uuid

from app.core.database import get_database
from app.models.website_builder import WebsiteProject, WebsiteBuilderSession
from app.schemas.website_builder import FrontendMessageResponse, FrontendSessionResponse
from app.services.business_service import BusinessService
from app.services.brand_service import get_brand_kit
from app.services.product_service import get_products
from app.ai.factory import AIProviderFactory

class WebsiteBuilderService:
    @staticmethod
    async def get_session_collection():
        db = get_database()
        return db["website_builder_sessions"]

    @staticmethod
    async def get_project_collection():
        db = get_database()
        return db["website_projects"]

    @staticmethod
    async def save_session(session: WebsiteBuilderSession):
        collection = await WebsiteBuilderService.get_session_collection()
        update_data = session.model_dump(by_alias=True, exclude={"id", "created_at"})
        update_data["updated_at"] = datetime.now(timezone.utc)
        await collection.update_one({"_id": ObjectId(session.id)}, {"$set": update_data})

    @staticmethod
    async def create_session(user_id: str) -> WebsiteBuilderSession:
        collection = await WebsiteBuilderService.get_session_collection()
        existing_doc = await collection.find_one({"user_id": user_id, "status": "active"})
        if existing_doc:
            return WebsiteBuilderSession(**existing_doc)

        session = WebsiteBuilderSession(
            user_id=user_id,
            messages=[
                {
                    "id": str(uuid.uuid4()),
                    "role": "ai",
                    "content": "Hi! I can build your business website. Let's create it together. Which language do you prefer?",
                    "type": "text"
                }
            ]
        )
        doc = session.model_dump(by_alias=True, exclude={"id"})
        result = await collection.insert_one(doc)
        session.id = str(result.inserted_id)
        await WebsiteBuilderService.load_existing_user_data(user_id, session)
        return session

    @staticmethod
    async def get_session(session_id: str, user_id: str) -> WebsiteBuilderSession | None:
        collection = await WebsiteBuilderService.get_session_collection()
        if not ObjectId.is_valid(session_id):
            return None
        doc = await collection.find_one({"_id": ObjectId(session_id), "user_id": user_id})
        if doc:
            return WebsiteBuilderSession(**doc)
        return None

    @staticmethod
    async def load_existing_user_data(user_id: str, session: WebsiteBuilderSession):
        business = await BusinessService.get_business_by_owner(user_id)
        if business:
            session.collected_data["Business Name"] = business.business_name
            session.collected_data["Business Category"] = business.business_category
            session.collected_data["business_id"] = str(business.id)
            
            db = get_database()
            brand = await get_brand_kit(db, str(business.id))
            if brand:
                if isinstance(brand, dict):
                    brand.pop("id", None)
                    brand.pop("_id", None)
                    session.collected_data["Brand Guidelines"] = brand
                else:
                    session.collected_data["Brand Guidelines"] = brand.model_dump(by_alias=True, exclude={"id"})
                
            products = await get_products(db, str(business.id))
            if products:
                prod_list = []
                for p in products:
                    if isinstance(p, dict):
                        p.pop("id", None)
                        p.pop("_id", None)
                        prod_list.append(p)
                    else:
                        prod_list.append(p.model_dump(by_alias=True, exclude={"id"}))
                session.collected_data["Products"] = prod_list
            
        await WebsiteBuilderService.save_session(session)

    @staticmethod
    async def process_chat(session_id: str, user_id: str, message: str, language: str = None):
        session = await WebsiteBuilderService.get_session(session_id, user_id)
        if not session:
            raise Exception("Session not found")
            
        session.messages.append({
            "id": str(uuid.uuid4()),
            "role": "user",
            "content": message
        })
        
        lower_msg = message.lower()
        if any(x in lower_msg for x in ["you decide", "recommend", "i don't know", "anything is fine"]):
            return await WebsiteBuilderService.generate_recommendations(session)
            
        if "build my website" in lower_msg:
            return await WebsiteBuilderService.generate_website(session)
            
        ai = AIProviderFactory.get_provider()
        extract_prompt = f"Extract structured fields from user message: '{message}'. Current collected data: {json.dumps(session.collected_data, default=str)}. Do NOT invent data. Return JSON with extracted fields."
        extracted = await ai.generate_json(extract_prompt, system_prompt="Extract business details (name, category, location, phone, products) from user messages.")
        if extracted and not extracted.get("error"):
            session.collected_data.update(extracted)
            
        chat_prompt = f"User said: '{message}'. We have this data: {json.dumps(session.collected_data, default=str)}. Respond in {session.language or 'English'}. If we have Name and Category, summarize and ask if they want to 'Recommend' a template or 'Build My Website'. Or ask for missing info."
        chat_result = await ai.generate_text(chat_prompt, system_prompt="You are a helpful AI website builder assistant. Keep it short and conversational.")
        reply_msg = chat_result.get("text", "Got it. Tell me more.")
        
        actions = []
        if "Business Name" in session.collected_data and "Business Category" in session.collected_data:
             actions = [{"label": "Recommend Templates", "action": "recommend"}, {"label": "Build My Website", "action": "generate"}]
             
        msg_obj = {
            "id": str(uuid.uuid4()),
            "role": "ai",
            "content": reply_msg,
            "type": "confirmation" if actions else "text",
        }
        if actions:
            msg_obj["options"] = actions
            
        session.messages.append(msg_obj)
        await WebsiteBuilderService.save_session(session)
        
        return type('obj', (object,), {'message': reply_msg, 'quick_actions': actions, 'session': session})

    @staticmethod
    async def generate_recommendations(session: WebsiteBuilderSession):
        ai = AIProviderFactory.get_provider()
        prompt = f"Generate exactly THREE website design recommendations for a business with data: {session.collected_data}. Return JSON with 'recommendations' array containing: id, name, description, reason, palette, style."
        result = await ai.generate_json(prompt, system_prompt="You are an expert web designer AI.")
        
        recs = result.get("recommendations", [])
        if len(recs) != 3:
            recs = [
                {"id": "rec1", "name": "Premium Luxury", "description": "High end look", "reason": "Fits your brand", "palette": "Black/Gold", "style": "Luxury"},
                {"id": "rec2", "name": "Modern Minimal", "description": "Clean look", "reason": "Contemporary style", "palette": "Blue/White", "style": "Minimal"},
                {"id": "rec3", "name": "Vibrant Casual", "description": "Energetic", "reason": "Attracts youth", "palette": "Orange/Yellow", "style": "Bold"}
            ]
        
        session.recommendations = recs
        session.current_step = 5
        reply_msg = "Here are 3 recommendations for you. Please select one."
        
        msg_obj = {
            "id": str(uuid.uuid4()),
            "role": "ai",
            "content": reply_msg,
            "type": "recommendation",
            "options": recs
        }
        session.messages.append(msg_obj)
        await WebsiteBuilderService.save_session(session)
        return type('obj', (object,), {'message': reply_msg, 'quick_actions': [], 'session': session})

    @staticmethod
    async def select_template(session_id: str, user_id: str, template_id: str) -> WebsiteBuilderSession:
        session = await WebsiteBuilderService.get_session(session_id, user_id)
        if not session:
            raise Exception("Session not found")
            
        session.selected_template = template_id
        session.current_step = 7
        session.messages.append({
            "id": str(uuid.uuid4()),
            "role": "ai",
            "content": f"You selected {template_id}. Ready to generate?",
            "type": "summary",
            "data": {
                "business": session.collected_data.get("Business Name", "Your Business"),
                "theme": template_id,
                "language": session.language
            },
            "options": [{"label": "Build My Website", "action": "generate"}]
        })
        await WebsiteBuilderService.save_session(session)
        return session
        
    @staticmethod
    async def generate_website(session: WebsiteBuilderSession):
        session.messages.append({
            "id": str(uuid.uuid4()),
            "role": "ai",
            "content": "Generating your website...",
            "type": "generation_status",
            "data": { "progress": ["Business Information", "Brand Style", "Website Structure"] }
        })
        await WebsiteBuilderService.save_session(session)
        
        ai = AIProviderFactory.get_provider()
        prompt = f"Generate a structured website JSON representation based on this data: {session.collected_data}. Include pages (Home, About, Products, Services, Contact) and sections. Use {session.language}."
        result = await ai.generate_json(prompt, system_prompt="You are an expert website generator.")
        
        if not result or result.get("error"):
             result = {
                 "pages": {
                     "home": {"hero": f"Welcome to {session.collected_data.get('Business Name', 'Your Brand')}", "features": []},
                     "about": {"content": "About us section..."}
                 }
             }
        
        raw_pages = result.get("pages", [])
        if not raw_pages:
             raw_pages = []
        elif not isinstance(raw_pages, list):
             raw_pages = [raw_pages]
             
        project = WebsiteProject(
            user_id=session.user_id,
            business_id=session.collected_data.get("business_id"),
            session_id=str(session.id),
            template_id=session.selected_template or "default",
            language=session.language or "English",
            pages=raw_pages,
            theme=result.get("theme", {}),
            status="published",
            website_data=result
        )
        
        collection = await WebsiteBuilderService.get_project_collection()
        doc = project.model_dump(by_alias=True, exclude={"id"})
        res = await collection.insert_one(doc)
        project.id = str(res.inserted_id)
        
        session.website_project_id = project.id
        session.current_step = 8
        session.messages.append({
            "id": str(uuid.uuid4()),
            "role": "ai",
            "content": "Website generated! You can now preview it on the right and ask for revisions.",
            "type": "text"
        })
        await WebsiteBuilderService.save_session(session)
        return type('obj', (object,), {'message': "Generated", 'quick_actions': [], 'session': session})
        
    @staticmethod
    async def get_website(site_id: str, user_id: str) -> WebsiteProject | None:
        collection = await WebsiteBuilderService.get_project_collection()
        if not ObjectId.is_valid(site_id):
            return None
        doc = await collection.find_one({"_id": ObjectId(site_id), "user_id": user_id})
        if doc:
            return WebsiteProject(**doc)
        return None

    @staticmethod
    async def revise_website(site_id: str, user_id: str, message: str) -> WebsiteProject:
        project = await WebsiteBuilderService.get_website(site_id, user_id)
        if not project:
            raise Exception("Project not found")
            
        ai = AIProviderFactory.get_provider()
        prompt = f"Revise this website JSON based on user request: '{message}'. Current website: {json.dumps(project.website_data)}. Return updated website JSON."
        result = await ai.generate_json(prompt, system_prompt="You are an expert website reviser.")
        
        if result and not result.get("error"):
            project.website_data = result
            project.pages = result.get("pages", project.pages) if isinstance(result.get("pages"), list) else [result.get("pages")]
            project.theme = result.get("theme", project.theme)
            project.version += 1
            
        collection = await WebsiteBuilderService.get_project_collection()
        update_data = project.model_dump(by_alias=True, exclude={"id", "created_at"})
        update_data["updated_at"] = datetime.now(timezone.utc)
        await collection.update_one({"_id": ObjectId(project.id)}, {"$set": update_data})
        
        return project
