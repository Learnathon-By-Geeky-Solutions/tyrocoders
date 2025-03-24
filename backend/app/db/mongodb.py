from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from core.logger import logger


class MongoDBClient:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]

    async def connect(self):
        try:
            await self.client.admin.command("ping")
            logger.info("Connected to MongoDB!")
            collections = await self.db.list_collection_names()
            logger.info(f"No of collections: {len(collections)}")
            logger.info(f"Collections: {collections}")
        except Exception as e:
            logger.critical(f"Error connecting to MongoDB: {e}")

    async def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_collection(self, collection_name: str):
        return self.db.get_collection(collection_name)


mongodb_client = MongoDBClient()


async def connect_to_mongo():
    await mongodb_client.connect()


async def close_mongo_connection():
    await mongodb_client.close()


base_admin_users_collection = mongodb_client.get_collection("customer_users")
base_chatbot_collection = mongodb_client.get_collection("chatbots")
