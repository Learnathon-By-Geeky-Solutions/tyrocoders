import datetime
from http import HTTPStatus
from typing import Optional
from bson import ObjectId
from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from services.chatbot_service import ChatbotService
from services.user_service import UserService
from schemas.chatbot_conversation import (
    ContinueConversation,
    DeleteConversationIds,
    LeadCollectConversation,
    UpdateConversationTag,
    UpdateSingleConversation,
    HandoverMessageConversation,
)
from crud.chatbot_conversation import ChatbotConversationCrud
from crud.chatbot import ChatbotCrud
from utils.converter import convert_object_id_to_string
from crud.user import UserCrud
from core.logger import logger
from processing.server import handle_client
from processing.db_storage import DatabaseStorageManager


chatbot_crud = ChatbotCrud()
chatbot_conversation_crud = ChatbotConversationCrud()
user_crud = UserCrud()
chatbot_service = ChatbotService()
user_service = UserService()
storage_mgr = DatabaseStorageManager()

USER_NOT_FOUND_MSG = "User not found"
CHATBOT_NOT_FOUND_MSG = "Chatbot not found"
CHATBOT_CONVERSATION_NOT_FOUND_MSG = "Conversation not found"

class ChatbotConversationService:
    """
    Service class responsible for managing chatbot conversations.
    
    This class provides methods for starting, retrieving, updating, and deleting
    chatbot conversations. It also provides functionality to continue conversations
    and collect lead information.
    """

    async def validate_conversation(
        self, user_id: ObjectId, conversation_id: str
    ):
        """
        Validate if a conversation with the specified ID exists for the given user.
        
        Args:
            user_id (ObjectId): The ID of the user.
            conversation_id (str): The ID of the conversation to validate.
            
        Returns:
            dict or None: The conversation document if found, None otherwise.
            
        Notes:
            This method logs debug and info messages during the validation process.
        """
        logger.debug(
            f"User ID: {user_id} | Checking if conversation with id {conversation_id} exists or not"
        )
        existing_conversation = (
            await chatbot_conversation_crud.get_user_conversation_by_id(
                ObjectId(conversation_id), str(user_id)
            )
        )
        if not existing_conversation:
            logger.info(
                f"User ID: {user_id} | Conversation with id {conversation_id} not found"
            )
            return None
        logger.info(
            f"User ID: {user_id} | Conversation with id {conversation_id} found"
        )
        return existing_conversation

    async def start_conversation_with_chatbot(
        self,
        user_id: ObjectId,
        chatbot_id: str,
    ):
        """
        Start a new conversation with a chatbot.
        
        Args:
            user_id (ObjectId): The ID of the user starting the conversation.
            chatbot_id (str): The ID of the chatbot to converse with.
            
        Returns:
            JSONResponse: A response containing the newly created conversation details
            or an error message with an appropriate HTTP status code.
            
        Raises:
            Exception: If any error occurs during the process.
            
        Notes:
            - Validates if the user and chatbot exist before creating a conversation.
            - Returns HTTP 404 if user or chatbot not found.
            - Returns HTTP 500 if an internal server error occurs.
            - Returns HTTP 201 with conversation data on success.
        """
        try:
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
                )

            if not await chatbot_crud.get_chatbot_by_id(
                chatbot_id, user_id
            ):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": CHATBOT_NOT_FOUND_MSG},
                )

            logger.debug(
                f"User ID: {user_id} | Creating new chatbot conversation"
            )
            new_chatbot_conversation = (
                await chatbot_conversation_crud.create_chatbot_conversation(
                    chatbot_id, str(user_id)
                )
            )
            new_chatbot_conversation = (
                await chatbot_conversation_crud.get_conversation_by_id(
                    new_chatbot_conversation.inserted_id
                )
            )
            new_chatbot_conversation = convert_object_id_to_string(
                new_chatbot_conversation
            )
            logger.info(
                f"User ID: {user_id} | New chatbot conversation created successfully"
            )

            return JSONResponse(
                status_code=HTTPStatus.CREATED,
                content={
                    "message": "New Chatbot Conversation created successfully",
                    "data": new_chatbot_conversation,
                },
            )
        except Exception as e:
            logger.error(
                f"User ID: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
    
    async def fetch_single_conversation_by_id(
        self, user_id: ObjectId, conversation_id: str
    ):
        """
        Fetch a single conversation by its ID for a specific user.
        
        Args:
            user_id (ObjectId): The ID of the user.
            conversation_id (str): The ID of the conversation to fetch.
            
        Returns:
            JSONResponse: A response containing the conversation details or an error
            message with an appropriate HTTP status code.
            
        Raises:
            Exception: If any error occurs during the process.
            
        Notes:
            - Validates if the user and conversation exist.
            - Returns HTTP 404 if user or conversation not found.
            - Returns HTTP 500 if an internal server error occurs.
            - Returns HTTP 200 with conversation data on success.
        """
        try:
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
                )

            existing_conversation = await self.validate_conversation(
                user_id, conversation_id
            )
            if not existing_conversation:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": CHATBOT_NOT_FOUND_MSG},
                )

            existing_conversation = convert_object_id_to_string(existing_conversation)

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Conversation Fetched successfully",
                    "data": existing_conversation,
                },
            )
        except Exception as e:
            logger.error(
                f"User ID: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )

    async def get_all_conversations(self, user_id: ObjectId):
        """
        Get all non-single conversations for a user.
        
        Args:
            user_id (ObjectId): The ID of the user whose conversations to fetch.
            
        Returns:
            JSONResponse: A response containing a list of conversations or an error
            message with an appropriate HTTP status code.
            
        Raises:
            Exception: If any error occurs during the process.
            
        Notes:
            - Validates if the user exists before fetching conversations.
            - Returns HTTP 404 if user not found.
            - Returns HTTP 500 if an internal server error occurs.
            - Returns HTTP 200 with conversations list on success.
        """
        try:
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
                )

            logger.debug(
                f"User ID: {user_id} | Getting all conversations for user with id {user_id}"
            )
            conversation_list = await chatbot_conversation_crud.get_all_non_single_conversations_by_user_id(
                str(user_id)
            )

            conversation_list = [
                convert_object_id_to_string(conversation)
                for conversation in conversation_list
            ]
            logger.info(
                f"User ID: {user_id} | All Conversations fetched successfully for user with id {user_id}"
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": f"List of all conversations retrieved successfully for user_id: {user_id}",
                    "data": conversation_list,
                },
            )
        except Exception as e:
            logger.error(
                f"User ID: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
        
    async def update_single_conversation_message(
        self,
        data: UpdateSingleConversation,
        user_id: ObjectId,
    ):
        """
        Update a specific message in a conversation.
        
        Args:
            data (UpdateSingleConversation): The data containing conversation ID, 
                message ID, and the new message content.
            user_id (ObjectId): The ID of the user.
            
        Returns:
            JSONResponse: A response containing the updated conversation details or an error
            message with an appropriate HTTP status code.
            
        Raises:
            Exception: If any error occurs during the process.
            
        Notes:
            - Validates if the user and conversation exist.
            - Returns HTTP 404 if user or conversation not found.
            - Returns HTTP 500 if an internal server error occurs.
            - Returns HTTP 200 with updated conversation data on success.
        """
        try:
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
                )

            if not await self.validate_conversation(
                user_id, data.conversation_id
            ):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": CHATBOT_NOT_FOUND_MSG},
                )

            logger.debug(
                f"User ID: {user_id} | Updating conversation message with id {data.conversation_id}"
            )
            await chatbot_conversation_crud.update_chatbot_conversation_message_by_message_id(
                data.message_id,
                ObjectId(data.conversation_id),
                data.new_message,
            )
            updated_conversation = await chatbot_conversation_crud.get_conversation_by_id(
                ObjectId(data.conversation_id)
            )
            updated_conversation = convert_object_id_to_string(updated_conversation)
            logger.info(
                f"User ID: {user_id} | Conversation message updated successfully"
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Conversation message Updated successfully",
                    "data": updated_conversation,
                },
            )
        except Exception as e:
            logger.error(
                f"User ID: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
        
    
    async def continue_conversation(
        self,
        continue_conversation: ContinueConversation,
        user_id: ObjectId,
        conversation_id: str,
    ):
        """
        Continue an existing conversation by processing a new user message and generating a bot response.
        
        Args:
            continue_conversation (ContinueConversation): The data containing the user message.
            user_id (ObjectId): The ID of the user.
            conversation_id (str): The ID of the conversation to continue.
            
        Returns:
            JSONResponse: A response containing the bot's response message or an error
            message with an appropriate HTTP status code.
            
        Raises:
            Exception: If any error occurs during the process.
            
        Notes:
            - Validates if the user and conversation exist.
            - Fetches conversation history and chatbot details.
            - Processes the user message using the LLM client.
            - Updates the conversation history with both user and bot messages.
            - Returns HTTP 404 if user or conversation not found.
            - Returns HTTP 500 if an internal server error occurs or if LLM processing fails.
            - Returns HTTP 200 with bot response on success.
        """
        try:
            user = await user_service.validate_user(user_id)
            if not user:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
                )

            existing_conversation = await self.validate_conversation(
                user_id, conversation_id
            )
            if not existing_conversation:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": CHATBOT_NOT_FOUND_MSG},
                )

            logger.debug(
                f"User ID: {user_id} | Getting the conversation history from exsiting conversation"
            )
            conversation_history = (
                await chatbot_conversation_crud.get_conversation_history_by_id(
                    ObjectId(conversation_id), str(user_id)
                )
            )
            logger.info(
                f"User ID: {user_id} | Conversation history fetched successfully"
            )

            logger.debug(
                f"User ID: {user_id} | Getting the chatbot details"
            )

            chatbot_id = existing_conversation.get("chatbot_id")
            chatbot = await chatbot_crud.get_chatbot_by_id(
                ObjectId(chatbot_id), user_id
            )

            # add the user msg to the conversation history
            logger.debug(
                f"User ID: {user_id} | Getting the fallback response from the chatbot"
            )

            fallback_response = chatbot.get("fallback_message", "Sorry, I couldn't understand that.")
            logger.info(
                f"User ID: {user_id} | Fallback response fetched successfully"
            )

            logger.debug("Getting the chatbot prompt role")
            custom_prompt_role_of_chatbot = chatbot.get(
                "role_of_chatbot"
            )
            
            logger.debug("Getting the chatbot ai_model_name")
            ai_model_name = chatbot.get(
                "ai_model_name"
            )
            
            starting_prompt = custom_prompt_role_of_chatbot
            logger.info("Chatbot prompt role fetched successfully")

            logger.debug(
                f"User ID: {user_id} | Generating the llm response based on user query"
            )

            print(ai_model_name)
            print(starting_prompt)

            is_success, bot_response_msg, error_msg = await handle_client(
                chatbot_id=existing_conversation.get("chatbot_id"),
                user_message=continue_conversation.user_message,
                conversation_history=conversation_history,
                conversation_id=conversation_id,
                user_id=str(user_id),
            )


            if not is_success:
                return JSONResponse(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content={
                        "message": f"Internal server error. ERROR: {error_msg}"
                    },
                )

            logger.info(
                f"User ID: {user_id} | Bot response: "
            )
            print(bot_response_msg)
            logger.debug(
                f"User ID: {user_id} | Adding the user message to the conversation history"
            )
            conversation_history.append(
                {
                    "message_id": str(ObjectId()),
                    "confidence_score": 50.0,
                    "message": continue_conversation.user_message,
                    "sender": "user",
                    "timestamp": int(datetime.datetime.now().timestamp()),
                }
            )
            logger.info(
                f"User ID: {user_id} | User message added to the conversation history"
            )
            conversation_history.append(
                {
                    "message_id": str(ObjectId()),
                    "confidence_score": 100.0,
                    "message": bot_response_msg or fallback_response,
                    "sender": "bot",
                    "timestamp": int(datetime.datetime.now().timestamp()),
                }
            )
            total_messages = len(conversation_history)
            logger.info(
                f"User ID: {user_id} | Langchain thing done successfully"
            )

            logger.debug(
                f"User ID: {user_id} | Updating the conversation history in the db"
            )
            await chatbot_conversation_crud.update_chatbot_conversation(
                {
                    "conversation_history": conversation_history,
                    "total_messages": total_messages,
                },
                ObjectId(conversation_id)
            )

            updated_conversation = (
                await chatbot_conversation_crud.get_conversation_by_id(
                    ObjectId(conversation_id)
                )
            )
            updated_conversation = convert_object_id_to_string(updated_conversation)
            logger.info(
                f"User ID: {user_id} | Conversation history updated in the db successfully"
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Conversation Continued successfully",
                    "data": bot_response_msg or fallback_response
                },
            )
        except Exception as e:
            logger.error(
                f"User ID: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
        
    async def lead_collect(
        self,
        lead_collect_conversation: LeadCollectConversation,
        user_id: ObjectId,
        conversation_id: str,
    ):
        """
        Collect lead information from a conversation.
        
        Args:
            lead_collect_conversation (LeadCollectConversation): The data containing 
                lead fields to collect.
            user_id (ObjectId): The ID of the user.
            conversation_id (str): The ID of the conversation.
            
        Returns:
            JSONResponse: A response containing the updated conversation details or an error
            message with an appropriate HTTP status code.
            
        Raises:
            Exception: If any error occurs during the process.
            
        Notes:
            - Validates if the user and conversation exist.
            - Updates the conversation with collected lead fields.
            - Returns HTTP 404 if user or conversation not found.
            - Returns HTTP 500 if an internal server error occurs.
            - Returns HTTP 200 with updated conversation data on success.
        """
        try:
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
                )

            existing_conversation = await self.validate_conversation(
                user_id, conversation_id
            )
            if not existing_conversation:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": CHATBOT_NOT_FOUND_MSG},
                )

            logger.debug(
                f"User ID: {user_id} | Updating the lead info in the db"
            )

            await chatbot_conversation_crud.update_chatbot_conversation_last_message(
                ObjectId(conversation_id),
                str(user_id),             
                collect_lead_fields=lead_collect_conversation.collect_lead_fields,
            )

            logger.info(
                f"User ID: {user_id} | Lead collected & updated in the db successfully"
            )

            updated_conversation = await chatbot_conversation_crud.get_conversation_by_id(
                ObjectId(conversation_id)
            )
            updated_conversation = convert_object_id_to_string(updated_conversation)
            logger.info(
                f"User ID: {user_id} | Lead collected successfully"
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Lead collected successfully",
                    "data": updated_conversation,
                },
            )
        except Exception as e:
            logger.error(
                f"User ID: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
            
    async def delete_conversations(
        self,
        delete_conversation_ids: DeleteConversationIds,
        user_id: ObjectId,
    ):
        """
        Delete multiple conversations for a user.
        
        Args:
            delete_conversation_ids (DeleteConversationIds): The data containing IDs of 
                conversations to delete.
            user_id (ObjectId): The ID of the user.
            
        Returns:
            JSONResponse: A response indicating success or an error
            message with an appropriate HTTP status code.
            
        Raises:
            Exception: If any error occurs during the process.
            
        Notes:
            - Validates if the user exists before deleting conversations.
            - Returns HTTP 404 if user not found.
            - Returns HTTP 500 if an internal server error occurs.
            - Returns HTTP 200 on successful deletion.
        """
        try:
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
                )

            logger.debug(
                f"User ID: {user_id} | Deleting the conversations with ids {delete_conversation_ids.conversation_ids}"
            )
            await chatbot_conversation_crud.delete_conversations(
                delete_conversation_ids,
                str(user_id),
            )
            logger.info(
                f"User ID: {user_id} | Conversations deleted successfully"
            )
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Conversations deleted successfully",
                },
            )
        except Exception as e:
            logger.error(
                f"User ID: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )