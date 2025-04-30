from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Path
from schemas.chatbot_conversation import (
    ContinueConversation,
    LeadCollectConversation,
    UpdateConversationTag,
    UpdateSingleConversation,
    HandoverMessageConversation,
)
from services.chatbot_conversation_service import ChatbotConversationService
from middlewares.embed_middleware import embed_middleware
from schemas.chatbot_embed import ChatbotEmbedUpdateModel
from services.chatbot_service import ChatbotService
from middlewares.auth_middleware import authenticate_token
from services.chatbot_embed_service import ChatbotEmbedService

chatbot_embed_router = APIRouter()
chatbot_embed_service = ChatbotEmbedService()
chatbot_service = ChatbotService()
chatbot_conversation_service = ChatbotConversationService()


@chatbot_embed_router.get("/read-chatbot/{chatbot_id}")
async def read_chatbot_for_embed(
    chatbot_id: str = Path(..., description="The ID of the chatbot to read"),
    user_id = Depends(embed_middleware),
):
    """
    Retrieve details of a chatbot for embedded usage.

    Args:
        chatbot_id (str): The ID of the chatbot to fetch.
        user_id: Authenticated user ID obtained via embed middleware.

    Returns:
        JSONResponse: Chatbot metadata and configuration.
    """
    return await chatbot_service.read_chatbot(
        user_id, chatbot_id
    )


@chatbot_embed_router.post("/chatbot-conversation/start/{chatbot_id}")
async def start_conversation_with_chatbot(
    chatbot_id: str = Path(..., description="The ID of the chatbot to start"),
    user_id = Depends(embed_middleware),
):
    """
    Start a new embedded chatbot conversation.

    Args:
        chatbot_id (str): The ID of the chatbot to initiate a conversation with.
        user_id: Authenticated user ID from embed middleware.

    Returns:
        JSONResponse: New conversation instance.
    """
    return await chatbot_conversation_service.start_conversation_with_chatbot(
        user_id, chatbot_id
    )


@chatbot_embed_router.get("/chatbot-conversation/read/{conversation_id}")
async def fetch_single_conversation_by_id(
    conversation_id: str = Path(..., description="The ID of the conversation to fetch"),
    user_id = Depends(embed_middleware),
):
    """
    Fetch a specific embedded conversation by its ID.

    Args:
        conversation_id (str): The ID of the conversation to fetch.
        user_id: Authenticated user ID via embed middleware.

    Returns:
        JSONResponse: Conversation data or error if not found.
    """
    return await chatbot_conversation_service.fetch_single_conversation_by_id(
        user_id, conversation_id
    )


@chatbot_embed_router.post("/chatbot-conversation/update-single-message")
async def update_single_conversation_message(
    data: UpdateSingleConversation,
    user_id = Depends(embed_middleware),
):
    """
    Update a message in an embedded chatbot conversation.

    Args:
        data (UpdateSingleConversation): Payload containing message ID and new content.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Success status or error message.
    """
    return await chatbot_conversation_service.update_single_conversation_message(
        data, user_id
    )


@chatbot_embed_router.post("/chatbot-conversation/continue-conversation/{conversation_id}")
async def continue_conversation(
    continue_conversation: ContinueConversation,
    conversation_id: str = Path(
        ..., description="The ID of the conversation to continue messaging"
    ),
    user_id = Depends(embed_middleware),
):
    """
    Continue an embedded conversation with a new message.

    Args:
        continue_conversation (ContinueConversation): Data for the next user message.
        conversation_id (str): ID of the conversation to continue.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Updated conversation state.
    """
    return await chatbot_conversation_service.continue_conversation(
        continue_conversation, user_id, conversation_id
    )


@chatbot_embed_router.post("/chatbot-conversation/lead-collect/{conversation_id}")
async def lead_collect(
    lead_collect_conversation: LeadCollectConversation,
    conversation_id: str,
    user_id = Depends(embed_middleware),
):
    """
    Collect lead data from an embedded chatbot conversation.

    Args:
        lead_collect_conversation (LeadCollectConversation): Lead information to be stored.
        conversation_id (str): Conversation ID associated with the lead.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Confirmation of successful lead collection.
    """
    return await chatbot_conversation_service.lead_collect(
        lead_collect_conversation, user_id, conversation_id
    )
