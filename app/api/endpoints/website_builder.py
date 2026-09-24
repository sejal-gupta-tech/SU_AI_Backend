from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Any, Dict
from app.schemas.website_builder import (
    CreateSessionRequest,
    SendMessageRequest,
    ReviseSiteRequest,
    FrontendSessionResponse,
    FrontendMessageResponse,
    WebsiteBuilderSessionResponse
)
from app.services.website_builder_service import WebsiteBuilderService
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("/session", response_model=FrontendSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: CreateSessionRequest, current_user: User = Depends(get_current_user)):
    session = await WebsiteBuilderService.create_session(str(current_user.id))
    session.language = request.language
    # Optionally re-save session with language, but the service handles it.
    
    return FrontendSessionResponse(
        sessionId=str(session.id),
        siteId=str(session.website_project_id) if session.website_project_id else None,
        language=session.language,
        messages=session.messages
    )

@router.get("/session/{session_id}", response_model=FrontendSessionResponse)
async def get_session(session_id: str, current_user: User = Depends(get_current_user)):
    session = await WebsiteBuilderService.get_session(session_id, str(current_user.id))
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    site = None
    if session.website_project_id:
        site = await WebsiteBuilderService.get_website(str(session.website_project_id), str(current_user.id))
        
    return FrontendSessionResponse(
        sessionId=str(session.id),
        siteId=str(session.website_project_id) if session.website_project_id else None,
        language=session.language,
        messages=session.messages,
        generatedSiteData=site.pages if site else None
    )

@router.post("/session/{session_id}/message", response_model=FrontendMessageResponse)
async def session_message(session_id: str, request: SendMessageRequest, current_user: User = Depends(get_current_user)):
    try:
        data_obj = request.data or {}
        action = data_obj.get("action") if isinstance(data_obj, dict) else None
        
        if action == "select_template":
            session = await WebsiteBuilderService.select_template(
                session_id,
                str(current_user.id),
                data_obj.get("templateId")
            )
            return FrontendMessageResponse(
                messages=session.messages,
                siteId=str(session.website_project_id) if session.website_project_id else None
            )
            
        elif action == "generate":
            session = await WebsiteBuilderService.get_session(session_id, str(current_user.id))
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            await WebsiteBuilderService.generate_website(session)
            
            # Reload session
            session = await WebsiteBuilderService.get_session(session_id, str(current_user.id))
            site = None
            if session.website_project_id:
                site = await WebsiteBuilderService.get_website(str(session.website_project_id), str(current_user.id))
                
            return FrontendMessageResponse(
                messages=session.messages,
                siteId=str(session.website_project_id) if session.website_project_id else None,
                generatedSiteData=site.pages if site else None
            )
            
        else:
            # Regular chat
            resp = await WebsiteBuilderService.process_chat(
                session_id,
                str(current_user.id),
                request.message,
                None # Language already in session
            )
            session = resp.session
            
            last_msg = session.messages[-1] if session.messages else {}
            msg_type = last_msg.get("type", "text")
            
            msg_data = {
                "message": resp.message,
                "type": msg_type,
                "messages": session.messages
            }
                
            return FrontendMessageResponse(**msg_data)
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/site/{site_id}/revise")
async def revise_website(site_id: str, request: ReviseSiteRequest, current_user: User = Depends(get_current_user)):
    try:
        site = await WebsiteBuilderService.revise_website(site_id, str(current_user.id), request.instructions)
        return {"generatedSiteData": site.pages}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
