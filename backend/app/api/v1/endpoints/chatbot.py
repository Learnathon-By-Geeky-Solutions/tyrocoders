from fastapi import APIRouter, Depends, File, UploadFile
from typing import List, Optional
from middlewares import authenticate_token
from services.chatbot_service import ChatbotService
from schemas.chatbot import (
    ChatbotCreate,
    ChatbotUpdate,
    ChatbotQueryRequest,
)

chatbot_router = APIRouter()
chatbot_service = ChatbotService()

@chatbot_router.post("/create")
async def create_chatbot(
    chatbot_data: ChatbotCreate,
    user_id = Depends(authenticate_token)
):
    return await chatbot_service.create_chatbot(
        user_id, 
        chatbot_data
    )

@chatbot_router.get("/get-all-chatbots")
async def get_all_chatbots(
     user_id = Depends(authenticate_token)
):
    return await chatbot_service.get_all_chatbots(user_id)

@chatbot_router.get("/{chatbot_id}")
async def read_chatbot(
    chatbot_id: str,
    user_id = Depends(authenticate_token)
):
    return await chatbot_service.read_chatbot(
        user_id, 
        chatbot_id,
    )

@chatbot_router.put("/{chatbot_id}")
async def update_chatbot(
    chatbot_id: str,
    update_data: ChatbotUpdate,
    user_id = Depends(authenticate_token)
):
    return await chatbot_service.update_chatbot(
        user_id, 
        chatbot_id,
        update_data,
    )

@chatbot_router.post("/{chatbot_id}/files")
async def upload_knowledge_files(
    chatbot_id: str,
    files: List[UploadFile] = File(...),
    user_id=Depends(authenticate_token),
):
    return await chatbot_service.upload_chatbot_files(
        user_id,
        chatbot_id,
        files
    )


@chatbot_router.delete("/{chatbot_id}")
async def delete_chatbot(
    chatbot_id: str,
    user_id = Depends(authenticate_token)
):
    return await chatbot_service.delete_chatbot(
        user_id, chatbot_id
    )


@chatbot_router.get("/get-leads/{chatbot_id}")
async def get_leads_of_chatbot(
    chatbot_id: str,
    user_id = Depends(authenticate_token),
):
    return await chatbot_service.get_leads_by_chatbot_id(
        user_id, chatbot_id
    )