from training.web_scraper import WebScraper
from training.scrape_products import scrape_from_website
from training.chatbot_training import ContextualChatbot
from crud.chatbot import ChatbotCrud
from crud.user import UserCrud
from schemas.chatbot import ChatbotCreate, ChatbotUpdate
from core.logger import logger
from fastapi.responses import JSONResponse
from http import HTTPStatus
from utils.converter import convert_object_id_to_string
from bson import ObjectId
import uuid
import json
from datetime import datetime

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
    
    async def create_chatbot(self, user_id: ObjectId, chatbot: ChatbotCreate):
        try:
            logger.debug(f"Validating user with ID: {user_id}")
            if not await self.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
            existing_chatbot = (
                await chatbot_crud.get_chatbot_by_chatbot_name_and_user_id(
                    chatbot.name, str(user_id)
                )
            )
            if existing_chatbot:
                logger.info(
                   f"User ID: {user_id} | Chatbot with name '{chatbot.name}' already exists"
                )
                existing_chatbot = convert_object_id_to_string(existing_chatbot)
                return JSONResponse(
                    status_code=HTTPStatus.CONFLICT,
                    content={
                        "message": f"Chatbot with name {chatbot.name} already exists",
                        # "data": existing_chatbot,
                    },
                )

            logger.debug(f"Scraping website for products: {chatbot.website_url}")
            products = await scrape_from_website(
                str(chatbot.website_url),
                scrape_limit=10,
                sample_size=3,
                max_concurrent=20
            )

            if not products:
                logger.info(f"No products found for website: {chatbot.website_url}")
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={"message": "No products could be scraped from the provided URL"},
                )

            # Generate a unique file name using user_id, current timestamp, and a unique suffix.
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            unique_suffix = uuid.uuid4().hex[:6]  # A short random string.
            products_file_name = f"products_user_{str(user_id)}_{timestamp}_{unique_suffix}.json"

            try:
                with open(products_file_name, "w", encoding="utf-8") as f:
                    json.dump(products, f, indent=4)
                logger.info(f"Products JSON saved locally to {products_file_name}")
            except Exception as e:
                logger.error(f"Failed to save product JSON locally: {e}")
                return JSONResponse(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content={"message": "Error saving products file."},
                )

            chatbot.products_file = products_file_name
            chatbot.user_id = str(user_id)  

            logger.debug("Saving chatbot to database")
            new_inserted_chatbot = await chatbot_crud.create_chatbot(chatbot)
            new_chatbot = await chatbot_crud.get_chatbot_by_id(new_inserted_chatbot.inserted_id, str(user_id))
            new_chatbot = convert_object_id_to_string(new_chatbot)
            logger.info("Chatbot created successfully")

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
    
    async def read_chatbot(self, user_id: ObjectId, chatbot_id: str):
        try:
            if not await self.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )

            existing_chatbot = await chatbot_crud.get_chatbot_by_id(
                chatbot_id, str(user_id)
            )
            if not existing_chatbot:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": f"Chatbot not found"},
                )

            existing_chatbot = convert_object_id_to_string(existing_chatbot)

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": f"Chatbot Fetched successfully",
                    "data": existing_chatbot,
                },
            )
        except Exception as e:
            logger.error(
                f" User ID: {user_id} | Internal server error. ERROR: {e}"
            )
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
            
            chatbot_data = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
            
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
    
    async def update_chatbot(self, user_id: ObjectId, chatbot_id: str, chatbot_data: ChatbotUpdate):
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
            
            chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
            
            if not chatbot:
                logger.info(
                    f"Chatbot with ID {chatbot_id} not found"
                )
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "Chatbot not found"},
                )
            
            logger.debug(f"Applying update to chatbot")
            result = await chatbot_crud.update_chatbot(chatbot_id, chatbot_data)
            
            updated_chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
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
            
            chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
            
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