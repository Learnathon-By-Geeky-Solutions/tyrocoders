from training.web_scraper import WebScraper
from training.chatbot_training import ContextualChatbot
from crud.chatbot import ChatbotCrud
from crud.user import UserCrud
from schemas.chatbot import ChatbotCreate, ChatbotUpdate
from core.logger import logger
from fastapi.responses import JSONResponse
from http import HTTPStatus
from utils.converter import convert_object_id_to_string
from bson import ObjectId

chatbot_crud = ChatbotCrud()
user_crud = UserCrud()

class ChatbotService:
    
    async def validate_user(self, user_id: ObjectId):
        logger.debug(f"Validating user with ID: {user_id}")
        user = await user_crud.get_user_by_id(user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found")
            return False
        logger.info(f"User with ID {user_id} found")
        return True
    
    async def create_chatbot(
        self,
        user_id: ObjectId,
        chatbot: ChatbotCreate,
    ):
        try:
            logger.debug(
                f"Validating user with ID: {user_id}"
            )
            
            if not await self.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
            
            logger.debug(
                f"Attempting to create new chatbot for website: {chatbot.website_url}"
            )
            
            logger.debug(f"Scraping website for products")
            scraper = WebScraper(str(chatbot.website_url))
            products = scraper.crawl()
            
            if not products:
                logger.info(f"No products found for website: {chatbot.website_url}")
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={"message": "No products could be scraped from the provided URL"},
                )
            
            logger.info(f"Found {len(products)} products from website")
            chatbot.products = products
            chatbot.user_id = user_id
            
            logger.debug(f"Saving chatbot to database")
            new_inserted_chatbot = await chatbot_crud.create_chatbot(chatbot)
            new_chatbot = await chatbot_crud.get_chatbot_by_id(
                new_inserted_chatbot.inserted_id
            )
            
            new_chatbot = convert_object_id_to_string(new_chatbot)
            logger.info(f"Chatbot created successfully")
            
            logger.debug(f"Initializing contextual chatbot model")
            chatbot_instance = ContextualChatbot(products, new_chatbot.get("_id"))
            
            return JSONResponse(
                status_code=HTTPStatus.CREATED,
                content={
                    "message": "Chatbot created successfully",
                    "data": new_chatbot,
                },
            )
        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
    
    async def query_chatbot(self, user_id: ObjectId, chatbot_id: str, query: str):
        try:
            logger.debug(
                f"Validating user with ID: {user_id}"
            )
            
            if not await self.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
            
            logger.debug(
                f"Querying chatbot with ID: {chatbot_id}"
            )
            
            chatbot_data = await chatbot_crud.get_chatbot_by_id(chatbot_id)
            
            if not chatbot_data:
                logger.info(
                    f"Chatbot with ID {chatbot_id} not found"
                )
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "Chatbot not found"},
                )
            
            # Verify the chatbot belongs to the user
            if str(chatbot_data.get("user_id")) != str(user_id):
                logger.info(
                    f"Chatbot with ID {chatbot_id} does not belong to user {user_id}"
                )
                return JSONResponse(
                    status_code=HTTPStatus.FORBIDDEN,
                    content={"message": "You don't have permission to access this chatbot"},
                )
            
            logger.info(
                f"Chatbot with ID {chatbot_id} found"
            )
            
            logger.debug(f"Initializing contextual chatbot with products data")
            chatbot_instance = ContextualChatbot(chatbot_data.get('products', []), chatbot_id)
            
            logger.debug(f"Generating response for query: {query}")
            response = chatbot_instance.generate_response(query)
            
            logger.info(f"Generated response successfully")
            
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Query processed successfully",
                    "data": {
                        "response": response,
                        "chatbot_id": chatbot_id,
                    },
                },
            )
        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
    
    async def update_chatbot(self, user_id: ObjectId, chatbot_id: str, update_data: ChatbotUpdate):
        try:
            logger.debug(
                f"Validating user with ID: {user_id}"
            )
            
            if not await self.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
            
            logger.debug(
                f"Updating chatbot with ID: {chatbot_id}"
            )
            
            chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id)
            
            if not chatbot:
                logger.info(
                    f"Chatbot with ID {chatbot_id} not found"
                )
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "Chatbot not found"},
                )
            
            # Verify the chatbot belongs to the user
            if str(chatbot.get("user_id")) != str(user_id):
                logger.info(
                    f"Chatbot with ID {chatbot_id} does not belong to user {user_id}"
                )
                return JSONResponse(
                    status_code=HTTPStatus.FORBIDDEN,
                    content={"message": "You don't have permission to update this chatbot"},
                )
            
            logger.info(
                f"Chatbot with ID {chatbot_id} found"
            )
            
            logger.debug(f"Applying update to chatbot")
            result = await chatbot_crud.update_chatbot(chatbot_id, update_data)
            
            updated_chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id)
            updated_chatbot = convert_object_id_to_string(updated_chatbot)
            
            logger.info(f"Chatbot updated successfully")
            
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Chatbot updated successfully",
                    "data": updated_chatbot,
                },
            )
        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
    
    async def delete_chatbot(self, user_id: ObjectId, chatbot_id: str):
        try:
            logger.debug(
                f"Validating user with ID: {user_id}"
            )
            
            if not await self.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
            
            logger.debug(
                f"Deleting chatbot with ID: {chatbot_id}"
            )
            
            chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id)
            
            if not chatbot:
                logger.info(
                    f"Chatbot with ID {chatbot_id} not found"
                )
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "Chatbot not found"},
                )
            
            # Verify the chatbot belongs to the user
            if str(chatbot.get("user_id")) != str(user_id):
                logger.info(
                    f"Chatbot with ID {chatbot_id} does not belong to user {user_id}"
                )
                return JSONResponse(
                    status_code=HTTPStatus.FORBIDDEN,
                    content={"message": "You don't have permission to delete this chatbot"},
                )
            
            logger.info(
                f"Chatbot with ID {chatbot_id} found"
            )
            
            logger.debug(f"Removing chatbot from database")
            result = await chatbot_crud.delete_chatbot(chatbot_id)
            
            logger.info(f"Chatbot deleted successfully")
            
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Chatbot deleted successfully",
                },
            )
        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )