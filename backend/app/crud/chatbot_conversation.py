import datetime
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from schemas.chatbot_conversation import DeleteConversationIds
from crud.chatbot import ChatbotCrud
from db.mongodb import base_chatbot_collection, base_chatbot_conversation_collection
from typing import List, Dict, Optional


class ChatbotConversationCrud():
    def __init__(self):
        self.collection = base_chatbot_conversation_collection
        self.chatbot_crud = ChatbotCrud()

    async def create_chatbot_conversation(
        self, chatbot_id: str, user_id: str
    ):
        collection = self.collection
        chatbot = await self.chatbot_crud.get_chatbot_by_id(
            ObjectId(chatbot_id), user_id
        )
        greeting_msg = None
        greeting_msg = chatbot.get("welcome_message", None)
        new_chatbot_conversation = await collection.insert_one(
            {
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
                "conversation_history": [
                    {
                        "message_id": str(ObjectId()),
                        "message": greeting_msg
                        or f"Hello, my name is {chatbot.get('name')}. How may I help you today?",
                        "sender": "bot",
                        "timestamp": int(datetime.datetime.now().timestamp()),
                        "confidence_score": 100.00,
                    }
                ],
            }
        )
        return new_chatbot_conversation

    async def get_conversation_by_id(self, conversation_id: ObjectId):
        collection = self.collection
        chatbot_conversation = await collection.find_one({"_id": conversation_id})
        return chatbot_conversation

    async def get_user_conversation_by_id(
        self, conversation_id: ObjectId, user_id: str
    ):
        collection = self.collection
        chatbot_conversation = await collection.find_one(
            {"_id": conversation_id, "user_id": user_id}
        )
        return chatbot_conversation
    
    async def get_all_non_single_conversations_by_user_id(
        self, user_id: str
    ):
        conversation_list = []
        collection = self.collection
        async for conversation in collection.find(
            {"user_id": user_id, "total_messages": {"$ne": 1}},
            # {"conversation_history": 0},
        ):
            conversation_list.append(conversation)
        return conversation_list
    
    async def update_chatbot_conversation_message_by_message_id(
        self,
        message_id: str,
        conversation_id: ObjectId,
        new_message: str,
    ):
        current_timestamp = int(datetime.datetime.now().timestamp())
        collection = self.collection
        await collection.update_one(
            {
                "_id": conversation_id,
                "conversation_history.message_id": message_id
            },
            {
                "$set": {
                    "conversation_history.$.message": new_message,
                    "conversation_history.$.timestamp": current_timestamp,
                    "most_recent": current_timestamp
                }
            },
        )

    async def get_conversation_history_by_id(
        self, conversation_id: ObjectId, user_id: str
    ):
        collection = self.collection
        chatbot_conversation = await collection.find_one(
            {"_id": conversation_id, "user_id": user_id}
        )
        return chatbot_conversation.get("conversation_history")
    
    async def update_chatbot_conversation_last_message(
        self,
        conversation_id: ObjectId,
        user_id: str,
        user_msg: str = None,
        collect_lead_fields: Optional[List[Dict[str, str]]] = None,
    ):
        collection = self.collection
        conversation_history = await self.get_conversation_history_by_id(
            conversation_id, user_id
        )

        current_timestamp = int(datetime.datetime.now().timestamp())
 
        # Append the new message if available
        if user_msg:
            conversation_history.append(
                {
                    "message_id": str(ObjectId()),
                    "message": user_msg,
                    "sender": "user",
                    "timestamp": current_timestamp,
                    "confidence_score": 100.00,
                }
            )

        update_data = {
            "conversation_history": conversation_history,
            "most_recent": current_timestamp,
            "total_messages": len(conversation_history),
        }

        # Include collect_lead_fields directly in the update data
        if collect_lead_fields:
            update_data["collect_lead_fields"] = collect_lead_fields

        # Update the conversation record with the new data
        await collection.update_one(
            {"_id": conversation_id},
            {"$set": update_data},
        )

    async def update_chatbot_conversation(
        self, conversation_data, conversation_id: ObjectId
    ):
        collection = self.collection
        conversation_dict = jsonable_encoder(
            conversation_data, exclude_unset=True, exclude_defaults=True, by_alias=True
        )
        conversation_dict["most_recent"] = int(datetime.datetime.now().timestamp())

        await collection.update_one(
            {"_id": conversation_id}, {"$set": conversation_dict}
        )

    async def delete_conversations(
        self,
        delete_conversation_ids: DeleteConversationIds,
        user_id: str,
    ):
        collection = self.collection
        object_ids = [ObjectId(id) for id in delete_conversation_ids.conversation_ids]

        await collection.delete_many(
            {
                "_id": {"$in": object_ids},
                "user_id": user_id,
            }
        )