from fastapi import APIRouter, Depends, Path
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
        update_data
    )

@chatbot_router.delete("/{chatbot_id}")
async def delete_chatbot(
    chatbot_id: str,
    user_id = Depends(authenticate_token)
):
    return await chatbot_service.delete_chatbot(
        user_id, chatbot_id
    )


@chatbot_router.post("/{chatbot_id}/query")
async def query_chatbot(
    chatbot_id: str,
    query: ChatbotQueryRequest,
    user_id = Depends(authenticate_token)
):
    return await chatbot_service.query_chatbot(
        user_id, 
        chatbot_id, 
        query.query
    )