from schemas.chatbot import ChatbotCreate, ChatbotUpdate
from db.mongodb import base_transaction_collection
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class SubscriptionCrud():
    def __init__(self):
        self.collection = base_transaction_collection
        
    async def save_transaction(self, transaction_data: dict):
        collection = self.collection
        new_transaction = await collection.insert_one(transaction_data)