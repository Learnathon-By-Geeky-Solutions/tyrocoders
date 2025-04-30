from typing import Optional
from fastapi import APIRouter, BackgroundTasks, Depends, Path
from schemas.chatbot_conversation import (
    ContinueConversation,
    DeleteConversationIds,
    LeadCollectConversation,
    UpdateConversationTag,
    UpdateSingleConversation,
    HandoverMessageConversation
)
from services.chatbot_conversation_service import ChatbotConversationService
from middlewares.auth_middleware import authenticate_token



chatbot_conversation_router = APIRouter()
chatbot_conversation_service = ChatbotConversationService()


@chatbot_conversation_router.post("/chat/{chatbot_id}")
async def start_conversation_with_chatbot(
    chatbot_id: str = Path(..., description="The ID of the chatbot to start"),
    user_id = Depends(authenticate_token)
):
    """
    Start a new conversation with a specific chatbot.

    Args:
        chatbot_id (str): ID of the chatbot to initiate conversation with.
        user_id: Authenticated user ID extracted via token.

    Returns:
        JSONResponse: Details of the newly created conversation.
    """
    return await chatbot_conversation_service.start_conversation_with_chatbot(
        user_id, chatbot_id
    )


@chatbot_conversation_router.get("/read/{conversation_id}")
async def fetch_single_conversation_by_id(
    conversation_id: str = Path(..., description="The ID of the conversation to fetch"),
    user_id = Depends(authenticate_token)
):
    """
    Fetch a single conversation by its ID.

    Args:
        conversation_id (str): Unique identifier of the conversation.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: The full conversation object or error if not found.
    """
    return await chatbot_conversation_service.fetch_single_conversation_by_id(
        user_id, conversation_id, 
    )


@chatbot_conversation_router.get("/get-all-conversations")
async def get_all_conversations(user_id = Depends(authenticate_token)):
    """
    Retrieve all conversations for the authenticated user.

    Args:
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: List of all user conversations.
    """
    return await chatbot_conversation_service.get_all_conversations(
        user_id, 
    )


@chatbot_conversation_router.post("/update-single-message")
async def update_single_conversation_message(
    data: UpdateSingleConversation,
    user_id = Depends(authenticate_token)
):
    """
    Update a specific message in a conversation.

    Args:
        data (UpdateSingleConversation): Contains message ID and updated content.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Confirmation or error message.
    """
    return await chatbot_conversation_service.update_single_conversation_message(
        data, user_id, 
    )


@chatbot_conversation_router.post("/continue-conversation/{conversation_id}")
async def continue_conversation(
    continue_conversation: ContinueConversation,
    conversation_id: str = Path(
        ..., description="The ID of the conversation to continue messaging"
    ),
    user_id = Depends(authenticate_token)
):
    """
    Continue a conversation by sending a new message.

    Args:
        continue_conversation (ContinueConversation): Message data to continue the chat.
        conversation_id (str): ID of the ongoing conversation.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Updated conversation data after new message is added.
    """
    return await chatbot_conversation_service.continue_conversation(
        continue_conversation, user_id, conversation_id, 
    )


@chatbot_conversation_router.post("/lead-collect/{conversation_id}")
async def lead_collect(
    lead_collect_conversation: LeadCollectConversation,
    conversation_id: str = Path(
        ..., description="The ID of the conversation to collect lead"
    ),
    user_id = Depends(authenticate_token)
):
    """
    Collect lead information from a conversation.

    Args:
        lead_collect_conversation (LeadCollectConversation): User's lead info to be captured.
        conversation_id (str): Conversation ID related to the lead.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Confirmation of lead capture or error.
    """
    return await chatbot_conversation_service.lead_collect(
        lead_collect_conversation, user_id, conversation_id, 
    )



@chatbot_conversation_router.delete("/delete")
async def delete_conversation(
    delete_conversation_ids: DeleteConversationIds,
    user_id = Depends(authenticate_token)
):
    """
    Delete one or more conversations for the authenticated user.

    Args:
        delete_conversation_ids (DeleteConversationIds): List of conversation IDs to be deleted.
        user_id: Authenticated user ID.

    Returns:
        JSONResponse: Success or failure status for each conversation ID.
    """
    return await chatbot_conversation_service.delete_conversations(
        delete_conversation_ids, user_id
    )
