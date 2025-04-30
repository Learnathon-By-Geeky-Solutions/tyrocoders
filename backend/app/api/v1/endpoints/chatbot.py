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
    """
    Create a new chatbot with provided configuration.

    Args:
        chatbot_data (ChatbotCreate): Data for chatbot creation.
        user_id: Authenticated user ID obtained from token.

    Returns:
        JSONResponse: Details of the created chatbot.
    """
    return await chatbot_service.create_chatbot(
        user_id, 
        chatbot_data
    )


@chatbot_router.get("/get-all-chatbots")
async def get_all_chatbots(
     user_id = Depends(authenticate_token)
):
    """
    Retrieve all chatbots created by the authenticated user.

    Args:
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: List of chatbots.
    """
    return await chatbot_service.get_all_chatbots(user_id)


@chatbot_router.get("/{chatbot_id}")
async def read_chatbot(
    chatbot_id: str,
    user_id = Depends(authenticate_token)
):
    """
    Get a specific chatbot by its ID.

    Args:
        chatbot_id (str): ID of the chatbot to retrieve.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Chatbot details.
    """
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
    """
    Update chatbot configuration or metadata.

    Args:
        chatbot_id (str): ID of the chatbot to update.
        update_data (ChatbotUpdate): New chatbot data.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Updated chatbot information.
    """
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
    """
    Upload knowledge base files to a specific chatbot.

    Args:
        chatbot_id (str): ID of the chatbot to upload files to.
        files (List[UploadFile]): List of files to upload.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Upload status and details.
    """
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
    """
    Delete a chatbot and all associated data.

    Args:
        chatbot_id (str): ID of the chatbot to delete.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Deletion status.
    """
    return await chatbot_service.delete_chatbot(
        user_id, chatbot_id
    )


@chatbot_router.get("/get-leads/{chatbot_id}")
async def get_leads_of_chatbot(
    chatbot_id: str,
    user_id = Depends(authenticate_token),
):
    """
    Retrieve collected leads from a specific chatbot.

    Args:
        chatbot_id (str): ID of the chatbot to fetch leads from.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: List of lead data.
    """
    return await chatbot_service.get_leads_by_chatbot_id(
        user_id, chatbot_id
    )
