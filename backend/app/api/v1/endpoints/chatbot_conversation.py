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


@chatbot_conversation_router.post(
    "/chat/{chatbot_id}"
)
async def start_conversation_with_chatbot(
    chatbot_id: str = Path(..., description="The ID of the chatbot to start"),
    user_id = Depends(authenticate_token)
):
    return await chatbot_conversation_service.start_conversation_with_chatbot(
        user_id, chatbot_id
    )


@chatbot_conversation_router.get(
    "/read/{conversation_id}")
async def fetch_single_conversation_by_id(
    conversation_id: str = Path(..., description="The ID of the conversation to fetch"),
    user_id = Depends(authenticate_token)
):
    return await chatbot_conversation_service.fetch_single_conversation_by_id(
        user_id, conversation_id, 
    )


@chatbot_conversation_router.get(
    "/get-all-conversations")
async def get_all_conversations(user_id = Depends(authenticate_token)):
    return await chatbot_conversation_service.get_all_conversations(
        user_id, 
    )


@chatbot_conversation_router.post(
    "/update-single-message")
async def update_single_conversation_message(
    data: UpdateSingleConversation,
    user_id = Depends(authenticate_token)
):
    return await chatbot_conversation_service.update_single_conversation_message(
        data, user_id, 
    )


@chatbot_conversation_router.post(
    "/continue-conversation/{conversation_id}",)
async def continue_conversation(
    continue_conversation: ContinueConversation,
    conversation_id: str = Path(
        ..., description="The ID of the conversation to continue messaging"
    ),
    user_id = Depends(authenticate_token)
):
    return await chatbot_conversation_service.continue_conversation(
        continue_conversation, user_id, conversation_id, 
    )


@chatbot_conversation_router.post(
    "/lead-collect/{conversation_id}")
async def lead_collect(
    lead_collect_conversation: LeadCollectConversation,
    conversation_id: str = Path(
        ..., description="The ID of the conversation to collect lead"
    ),
    user_id = Depends(authenticate_token)
):
    return await chatbot_conversation_service.lead_collect(
        lead_collect_conversation, user_id, conversation_id, 
    )

# @chatbot_conversation_router.post(
#     "/handover-message/{conversation_id}")
# async def user_message_handover(
#     handover_message_conversation: HandoverMessageConversation,
#     background_tasks: BackgroundTasks,
#     conversation_id: str = Path(
#         ..., description="The ID of the conversation to collect handover message",
#     ),
#     user_id = Depends(authenticate_token)
    
# ):
#     return await chatbot_conversation_service.user_message_handover(
#         handover_message_conversation, user_id, conversation_id, background_tasks
#     )


@chatbot_conversation_router.delete(
    "/delete")
async def delete_conversation(
    delete_conversation_ids: DeleteConversationIds,
    user_id = Depends(authenticate_token)
):
    return await chatbot_conversation_service.delete_conversations(
        delete_conversation_ids, user_id
    )