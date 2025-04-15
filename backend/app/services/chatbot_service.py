from training.web_scraper import WebScraper
from training.scrape_products import scrape_from_website
from training.chatbot_training import ContextualChatbot
from crud.chatbot import ChatbotCrud
from crud.user import UserCrud
from schemas.chatbot import ChatbotCreate, ChatbotUpdate
from core.logger import logger
from fastapi import UploadFile
from typing import List
from fastapi.responses import JSONResponse
from http import HTTPStatus
from utils.converter import convert_object_id_to_string
from bson import ObjectId
import uuid
import json
from datetime import datetime
from pathlib import Path
import shutil

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
                scrape_limit=10000,
                sample_size=3,
                max_concurrent=20
            )

            if not products:
                logger.info(f"No products found for website: {chatbot.website_url}")
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={"message": "No products could be scraped from the provided URL"},
                )

            new_uuid = str(uuid.uuid4())
            products_file_name = f"products_user_{new_uuid}.json"

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
        
    async def get_all_chatbots(self, user_id: ObjectId):
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
                f"Getting all chatbots for user with id {user_id}"
            )
            chatbots_list = await chatbot_crud.get_all_chatbots_by_user_id(
                str(user_id)
            )
            
            chatbots_list = [
                convert_object_id_to_string(chatbot) for chatbot in chatbots_list
            ]
            logger.info(
                f"User ID: {user_id} | All Chatbots fetched successfully for user with id {user_id}"
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": f"List of all chatbots retrieved successfully for user_id: {user_id}",
                    "data": chatbots_list,
                },
            )
        except Exception as e:
            logger.error(
                f"User ID: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
        
    async def upload_clatbot_files(self, user_id: ObjectId, chatbot_id: str, uploaded_files: List[UploadFile]):
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
                f"Fetching chatbot with ID: {chatbot_id}"
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

            current_files = chatbot.get("knowledge_files", [])
            knowledge_dir = Path("knowledge_bases") / str(chatbot_id)
            knowledge_dir.mkdir(parents=True, exist_ok=True)

            # Create mapping of original filenames to their current UUID versions
            existing_files_map = {}
            for f in current_files:
                try:
                    parts = f.split('_', 1)
                    if len(parts) == 2:
                        uuid_part, original_name = parts
                        existing_files_map[original_name] = f
                except:
                    continue

            final_files = []
            processed_names = set()

            # Process new uploads
            for new_file in uploaded_files:
                original_name = new_file.filename
                processed_names.add(original_name)

                # Only replace if this exact filename existed before
                if original_name in existing_files_map:
                    # Delete old version
                    old_path = knowledge_dir / existing_files_map[original_name]
                    if old_path.exists():
                        old_path.unlink()

                # Save new file with new UUID
                new_uuid = str(uuid.uuid4())
                new_filename = f"{new_uuid}_{original_name}"
                file_path = knowledge_dir / new_filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(new_file.file, buffer)
                final_files.append(new_filename)

            # Preserve all files that weren't modified
            for original_name, uuid_filename in existing_files_map.items():
                if original_name not in processed_names:
                    final_files.append(uuid_filename)

            # Update database with complete file list
            chatbot_data = ChatbotUpdate(upload_files=final_files)
            await chatbot_crud.update_chatbot(chatbot_id, chatbot_data)

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Files processed successfully",
                    "updated_files": [f for f in final_files if f.split('_', 1)[1] in processed_names],
                    "preserved_files": [f for f in final_files if f.split('_', 1)[1] not in processed_names],
                    "total_files": len(final_files)
                },
            )

        except Exception as e:
            logger.error(f"File upload failed. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
        
    async def upload_chatbot_files(self, user_id: ObjectId, chatbot_id: str, uploaded_files: List[UploadFile]):
        """
        Update files for a chatbot knowledge base.
        Each call completely replaces the previous set of files with the new set.
        
        Args:
            user_id: The ID of the user
            chatbot_id: The ID of the chatbot
            uploaded_files: Complete list of files that should exist after this update
        """
        try:
            logger.debug(f"Validating user with ID: {user_id}")
            if not await self.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
                
            logger.debug(f"Fetching chatbot with ID: {chatbot_id}")
            chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
            if not chatbot:
                logger.info(f"Chatbot with ID {chatbot_id} not found")
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "Chatbot not found"},
                )
                
            # Get current files and prepare directory
            current_files = chatbot.get("knowledge_files", [])
            knowledge_dir = Path("knowledge_bases") / str(chatbot_id)
            knowledge_dir.mkdir(parents=True, exist_ok=True)
            
            # Map original filenames to their UUID versions
            existing_files_map = {}
            for f in current_files:
                try:
                    parts = f.split('_', 1)
                    if len(parts) == 2:
                        uuid_part, original_name = parts
                        existing_files_map[original_name] = f
                except:
                    continue
                    
            # Get all original file names being uploaded
            new_file_names = [file.filename for file in uploaded_files]
            
            # Clean up old files that aren't in the new upload
            for original_name, uuid_filename in existing_files_map.items():
                if original_name not in new_file_names:
                    # Delete file that's not in the new upload
                    file_path = knowledge_dir / uuid_filename
                    if file_path.exists():
                        file_path.unlink()
                        logger.debug(f"Deleted file: {uuid_filename}")
            
            # Process all uploads, whether new or replacements
            final_files = []
            for new_file in uploaded_files:
                original_name = new_file.filename
                
                # If this filename already exists, delete the old version
                if original_name in existing_files_map:
                    old_path = knowledge_dir / existing_files_map[original_name]
                    if old_path.exists():
                        old_path.unlink()
                        
                # Save new file with UUID prefix
                new_uuid = str(uuid.uuid4())
                new_filename = f"{new_uuid}_{original_name}"
                file_path = knowledge_dir / new_filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(new_file.file, buffer)
                final_files.append(new_filename)
            
            # Update database with complete file list
            chatbot_data = ChatbotUpdate(knowledge_files=final_files)
            await chatbot_crud.update_chatbot(chatbot_id, chatbot_data)
            
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Files processed successfully",
                    "total_files": len(final_files)
                },
            )
        except Exception as e:
            logger.error(f"File upload failed. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )