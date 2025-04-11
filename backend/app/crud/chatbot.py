from schemas.chatbot import ChatbotCreate, ChatbotUpdate
from db.mongodb import base_chatbot_collection
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class ChatbotCrud():
    def __init__(self):
        self.collection = base_chatbot_collection
        
    async def create_chatbot(self, chatbot: ChatbotCreate):
        collection = self.collection
        chatbot_dict = chatbot.model_dump(mode='json')
        new_chatbot = await collection.insert_one(chatbot_dict)
        return new_chatbot
    
    async def get_chatbot_by_id(self, chatbot_id: str, user_id: str):
        chatbot = await self.collection.find_one({"_id": ObjectId(chatbot_id), "user_id": str(user_id)})
        return chatbot
    
    async def get_chatbot_by_chatbot_name_and_user_id(self, name: str, user_id: str):
        chatbot = await self.collection.find_one({"name": name, "user_id": user_id})
        return chatbot
    
    async def update_chatbot(self, chatbot_id: str, update_data: ChatbotUpdate):
        update_dict = jsonable_encoder(
            update_data, exclude_unset=True, exclude_defaults=True, by_alias=True
        )
        result = await self.collection.update_one(
            {"_id": ObjectId(chatbot_id)},
            {"$set": update_dict}
        )
        return result
    
    async def delete_chatbot(self, chatbot_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(chatbot_id)})
        return result