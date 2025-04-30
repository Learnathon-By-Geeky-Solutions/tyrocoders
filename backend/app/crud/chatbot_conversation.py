"""
ChatbotConversationCrud: Handles operations related to chatbot conversations,
including creation, retrieval, updates, and deletions in the MongoDB collection.

Dependencies:
- `ChatbotCrud` for chatbot details.
- `base_chatbot_conversation_collection` as the MongoDB collection.
- `DeleteConversationIds` schema for delete requests.
"""

import datetime
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from schemas.chatbot_conversation import DeleteConversationIds
from crud.chatbot import ChatbotCrud
from db.mongodb import base_chatbot_conversation_collection
from typing import List, Dict, Optional


class ChatbotConversationCrud:
    """
    CRUD operations for chatbot conversations stored in MongoDB.
    """

    def __init__(self):
        """Initialize MongoDB collection and chatbot CRUD dependency."""
        self.collection = base_chatbot_conversation_collection
        self.chatbot_crud = ChatbotCrud()

    async def create_chatbot_conversation(self, chatbot_id: str, user_id: str):
        """
        Creates a new chatbot conversation with a greeting message.

        Args:
            chatbot_id (str): The ID of the chatbot.
            user_id (str): The user who initiated the conversation.

        Returns:
            InsertOneResult: MongoDB result of the insert operation.
        """
        collection = self.collection
        chatbot = await self.chatbot_crud.get_chatbot_by_id(ObjectId(chatbot_id), user_id)

        greeting_msg = chatbot.get("welcome_message") or f"Hello, my name is {chatbot.get('name')}. How may I help you today?"

        new_chatbot_conversation = await collection.insert_one({
            "chatbot_id": chatbot_id,
            "chatbot_name": chatbot.get("name"),
            "user_id": user_id,
            "started_on": int(datetime.datetime.now().timestamp()),
            "most_recent": int(datetime.datetime.now().timestamp()),
            "total_messages": 1,
            "feedback": "Neutral",
            "confidence": 100.0,
            "channel": "Web",
            "is_live_now": False,
            "live_chat_info": None,
            "conversation_history": [{
                "message_id": str(ObjectId()),
                "message": greeting_msg,
                "sender": "bot",
                "timestamp": int(datetime.datetime.now().timestamp()),
                "confidence_score": 100.00,
            }],
        })
        return new_chatbot_conversation

    async def get_conversation_by_id(self, conversation_id: ObjectId):
        """
        Retrieves a conversation by its ID.

        Args:
            conversation_id (ObjectId): The ID of the conversation.

        Returns:
            dict: The conversation document.
        """
        return await self.collection.find_one({"_id": conversation_id})

    async def get_user_conversation_by_id(self, conversation_id: ObjectId, user_id: str):
        """
        Retrieves a conversation by its ID and user ID for ownership verification.

        Args:
            conversation_id (ObjectId): The conversation ID.
            user_id (str): The user ID.

        Returns:
            dict: The conversation document.
        """
        return await self.collection.find_one({"_id": conversation_id, "user_id": user_id})

    async def get_all_non_single_conversations_by_user_id(self, user_id: str):
        """
        Gets all conversations with more than one message for a specific user.

        Args:
            user_id (str): The user's ID.

        Returns:
            List[dict]: List of conversation documents.
        """
        conversations = []
        async for convo in self.collection.find({"user_id": user_id, "total_messages": {"$ne": 1}}):
            conversations.append(convo)
        return conversations

    async def update_chatbot_conversation_message_by_message_id(
        self, message_id: str, conversation_id: ObjectId, new_message: str
    ):
        """
        Updates a specific message within a conversation.

        Args:
            message_id (str): The ID of the message to update.
            conversation_id (ObjectId): The ID of the conversation.
            new_message (str): The new message content.
        """
        timestamp = int(datetime.datetime.now().timestamp())
        await self.collection.update_one(
            {"_id": conversation_id, "conversation_history.message_id": message_id},
            {
                "$set": {
                    "conversation_history.$.message": new_message,
                    "conversation_history.$.timestamp": timestamp,
                    "most_recent": timestamp
                }
            }
        )

    async def get_conversation_history_by_id(self, conversation_id: ObjectId, user_id: str):
        """
        Fetches only the conversation history of a conversation.

        Args:
            conversation_id (ObjectId): Conversation ID.
            user_id (str): User ID for validation.

        Returns:
            list: Conversation history messages.
        """
        convo = await self.collection.find_one({"_id": conversation_id, "user_id": user_id})
        return convo.get("conversation_history")

    async def update_chatbot_conversation_last_message(
        self,
        conversation_id: ObjectId,
        user_id: str,
        user_msg: str = None,
        collect_lead_fields: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Appends a user message and optionally updates lead field data.

        Args:
            conversation_id (ObjectId): The conversation ID.
            user_id (str): The user ID.
            user_msg (str, optional): The message to add.
            collect_lead_fields (List[Dict[str, str]], optional): Fields collected from the user.
        """
        history = await self.get_conversation_history_by_id(conversation_id, user_id)
        timestamp = int(datetime.datetime.now().timestamp())

        if user_msg:
            history.append({
                "message_id": str(ObjectId()),
                "message": user_msg,
                "sender": "user",
                "timestamp": timestamp,
                "confidence_score": 100.00,
            })

        update_data = {
            "conversation_history": history,
            "most_recent": timestamp,
            "total_messages": len(history),
        }

        if collect_lead_fields:
            update_data["collect_lead_fields"] = collect_lead_fields

        await self.collection.update_one({"_id": conversation_id}, {"$set": update_data})

    async def update_chatbot_conversation(self, conversation_data, conversation_id: ObjectId):
        """
        Updates a full conversation document based on passed data.

        Args:
            conversation_data: The updated conversation data.
            conversation_id (ObjectId): The ID of the conversation to update.
        """
        data = jsonable_encoder(conversation_data, exclude_unset=True, exclude_defaults=True, by_alias=True)
        data["most_recent"] = int(datetime.datetime.now().timestamp())
        await self.collection.update_one({"_id": conversation_id}, {"$set": data})

    async def delete_conversations(self, delete_conversation_ids: DeleteConversationIds, user_id: str):
        """
        Deletes multiple conversations by ID and user ID.

        Args:
            delete_conversation_ids (DeleteConversationIds): List of conversation IDs to delete.
            user_id (str): The user ID to validate ownership.
        """
        object_ids = [ObjectId(id) for id in delete_conversation_ids.conversation_ids]
        await self.collection.delete_many({"_id": {"$in": object_ids}, "user_id": user_id})

    async def get_leads_by_chatbot_id(self, chatbot_id: ObjectId):
        """
        Extracts lead data collected across all conversations for a specific chatbot.

        Args:
            chatbot_id (ObjectId): The ID of the chatbot.

        Returns:
            List[Dict[str, str]]: List of collected lead field data from conversations.

        Raises:
            RuntimeError: If an error occurs during data extraction.
        """
        try:
            cursor = self.collection.find({"chatbot_id": chatbot_id}, {"_id": 0, "collect_lead_fields": 1})
            conversations = await cursor.to_list(length=None)

            leads = []
            for convo in conversations:
                fields = convo.get("collect_lead_fields", [])
                lead = {
                    field["field_name"]: field["field_value"]
                    for field in fields
                    if "field_name" in field and "field_value" in field
                }
                if lead:
                    leads.append(lead)

            return leads
        except Exception as e:
            raise RuntimeError(f"Error retrieving leads for chatbot ID {chatbot_id}: {e}")
