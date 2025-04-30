"""
MongoDB Client Module

This module provides an asynchronous MongoDB client using Motor (async driver for MongoDB).
It handles the connection lifecycle and allows access to specific collections.

Dependencies:
- motor.motor_asyncio
- core.config (for configuration settings like MONGO_URI and MONGO_DB)
- core.logger (for logging purposes)

Usage:
    await connect_to_mongo()
    collection = mongodb_client.get_collection("example_collection")
    await close_mongo_connection()
"""

from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from core.logger import logger


class MongoDBClient:
    """
    A MongoDB asynchronous client that handles connection and collection access.

    Attributes:
        client (AsyncIOMotorClient): The Motor MongoDB client instance.
        db (Database): The selected database from the MongoDB URI.
    """
    def __init__(self):
        """
        Initializes the MongoDB client with URI and database from settings.
        """
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]

    async def connect(self):
        """
        Asynchronously connects to MongoDB and logs connection status.

        Performs a 'ping' to verify connectivity and lists existing collections.
        Logs error in case of failure.
        """
        try:
            await self.client.admin.command("ping")
            logger.info("Connected to MongoDB!")
            collections = await self.db.list_collection_names()
            logger.info(f"No of collections: {len(collections)}")
            logger.info(f"Collections: {collections}")
        except Exception as e:
            logger.critical(f"Error connecting to MongoDB: {e}")

    async def close(self):
        """
        Closes the MongoDB connection and logs the action.
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_collection(self, collection_name: str):
        """
        Retrieves a specific collection from the database.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The requested MongoDB collection.
        """
        return self.db.get_collection(collection_name)


# Global client instance
mongodb_client = MongoDBClient()


async def connect_to_mongo():
    """
    Initializes MongoDB connection on application startup.
    """
    await mongodb_client.connect()


async def close_mongo_connection():
    """
    Closes MongoDB connection on application shutdown.
    """
    await mongodb_client.close()


# Collection instances for specific use cases
base_admin_users_collection = mongodb_client.get_collection("customer_users")
base_chatbot_collection = mongodb_client.get_collection("chatbots")
base_chatbot_conversation_collection = mongodb_client.get_collection("chatbot_conversations")
base_transaction_collection = mongodb_client.get_collection("transactions")
