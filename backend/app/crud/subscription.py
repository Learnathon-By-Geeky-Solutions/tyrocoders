from schemas.chatbot import ChatbotCreate, ChatbotUpdate
from db.mongodb import base_transaction_collection
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class SubscriptionCrud:
    """
    CRUD operations related to subscription transactions in the MongoDB collection.
    """

    def __init__(self):
        """
        Initialize the SubscriptionCrud with the transaction collection.
        """
        self.collection = base_transaction_collection

    async def save_transaction(self, transaction_data: dict):
        """
        Save a subscription transaction record to the database.

        Args:
            transaction_data (dict): The transaction data to be stored.

        Returns:
            InsertOneResult: Result of the insert operation.
        """
        await self.collection.insert_one(transaction_data)
