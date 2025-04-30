from schemas.chatbot import ChatbotCreate, ChatbotUpdate
from db.mongodb import base_chatbot_collection
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class ChatbotCrud:
    """
    CRUD operations for chatbot documents in the MongoDB collection.
    """

    def __init__(self):
        self.collection = base_chatbot_collection

    async def create_chatbot(self, chatbot: ChatbotCreate):
        """
        Create a new chatbot document.

        Args:
            chatbot (ChatbotCreate): The chatbot data model to be inserted.

        Returns:
            InsertOneResult: Result of the insertion operation.
        """
        chatbot_dict = chatbot.model_dump(mode='json')
        new_chatbot = await self.collection.insert_one(chatbot_dict)
        return new_chatbot

    async def get_chatbot_by_id(self, chatbot_id: str, user_id: str):
        """
        Retrieve a chatbot by its ID and the user ID it belongs to.

        Args:
            chatbot_id (str): The ObjectId of the chatbot as a string.
            user_id (str): The user ID who owns the chatbot.

        Returns:
            dict or None: The chatbot document if found, otherwise None.
        """
        chatbot = await self.collection.find_one({
            "_id": ObjectId(chatbot_id),
            "user_id": str(user_id)
        })
        return chatbot

    async def get_chatbot_by_chatbot_name_and_user_id(self, name: str, user_id: str):
        """
        Retrieve a chatbot using its name and associated user ID.

        Args:
            name (str): Name of the chatbot.
            user_id (str): The user ID who owns the chatbot.

        Returns:
            dict or None: The chatbot document if found, otherwise None.
        """
        chatbot = await self.collection.find_one({
            "name": name,
            "user_id": user_id
        })
        return chatbot

    async def update_chatbot(self, chatbot_id: str, update_data: ChatbotUpdate):
        """
        Update a chatbot document.

        Args:
            chatbot_id (str): The ObjectId of the chatbot as a string.
            update_data (ChatbotUpdate): Data fields to update.

        Returns:
            UpdateResult: Result of the update operation.
        """
        update_dict = jsonable_encoder(
            update_data, exclude_unset=True, exclude_defaults=True, by_alias=True
        )
        result = await self.collection.update_one(
            {"_id": ObjectId(chatbot_id)},
            {"$set": update_dict}
        )
        return result

    async def delete_chatbot(self, chatbot_id: str):
        """
        Delete a chatbot by its ID.

        Args:
            chatbot_id (str): The ObjectId of the chatbot as a string.

        Returns:
            DeleteResult: Result of the delete operation.
        """
        result = await self.collection.delete_one({"_id": ObjectId(chatbot_id)})
        return result

    async def get_all_chatbots_by_user_id(self, user_id: str):
        """
        Get all chatbots created by a specific user.

        Args:
            user_id (str): The user ID.

        Returns:
            List[dict]: A list of chatbot documents owned by the user.
        """
        chatbots = []
        async for chatbot in self.collection.find({"user_id": user_id}):
            chatbots.append(chatbot)
        return chatbots
