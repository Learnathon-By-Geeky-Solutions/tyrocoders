from training.web_scraper import WebScraper
from training.scrape_products import scrape_from_website
from training.chatbot_training import ContextualChatbot
from services.user_service import UserService
from crud.chatbot import ChatbotCrud
from crud.chatbot_conversation import ChatbotConversationCrud
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
import os
from processing.kb import build_knowledge_base, rebuild_kb_after_upload
from processing.vanna_integrator import VannaIntegrator
import os

api_key = os.getenv("VANNA_API_KEY", "")
vanna_config = {'api_key' : f"{api_key}", 'model': "gemini-2.0-flash"}
vanna = VannaIntegrator(config=vanna_config)

USER_NOT_FOUND_MSG = "User not found"
CHATBOT_NOT_FOUND_MSG = "Chatbot not found"

chatbot_crud = ChatbotCrud()
user_crud = UserCrud()
user_service = UserService()
chatbot_conversation_crud = ChatbotConversationCrud()

class ChatbotService:
    """
    Service class for managing chatbot operations.
    
    This service handles CRUD operations for chatbots, user validation,
    and chatbot interaction functionality. It connects to the database through
    CRUD services and manages the processing of website scraping and 
    knowledge base creation for chatbots.
    """
    
    async def validate_user(self, user_id: ObjectId):
        """
        Validate if a user exists in the database.
        
        Args:
            user_id (ObjectId): The MongoDB ObjectId of the user to validate.
            
        Returns:
            bool: True if the user exists, False otherwise.
        """
        logger.debug(f"Validating user with ID: {user_id}")
        user = await user_crud.get_user_by_id(user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found")
            return False
        logger.info(f"User with ID {user_id} found")
        return True
    
    async def create_chatbot(self, user_id: ObjectId, chatbot: ChatbotCreate):
        """
        Create a new chatbot for a user with website scraping and knowledge base building.
        
        This method performs several steps:
        1. Validates the user exists
        2. Checks for duplicate chatbot names
        3. Scrapes products from the provided website URL
        4. Stores the scraped data in a JSON file
        5. Builds a knowledge base from the scraped data
        6. Creates a chatbot entry in the database
        
        Args:
            user_id (ObjectId): The MongoDB ObjectId of the user creating the chatbot.
            chatbot (ChatbotCreate): The chatbot creation model containing name, website URL, and other details.
            
        Returns:
            JSONResponse: HTTP response with status code and message:
                - 201 CREATED: Successful creation with chatbot data
                - 404 NOT_FOUND: User not found
                - 409 CONFLICT: Chatbot with same name already exists
                - 400 BAD_REQUEST: No products could be scraped
                - 500 INTERNAL_SERVER_ERROR: Server error with error message
        """
        try:
            if not await user_service.validate_user(user_id):
                return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={"message": USER_NOT_FOUND_MSG})

            # prevent duplicate names
            existing = await chatbot_crud.get_chatbot_by_chatbot_name_and_user_id(chatbot.name, str(user_id))
            if existing:
                return JSONResponse(status_code=HTTPStatus.CONFLICT,
                                    content={"message": f"Chatbot with name {chatbot.name} already exists"})

            # scrape products
            logger.debug(f"Scraping {chatbot.website_url}")
            products = await scrape_from_website(str(chatbot.website_url), scrape_limit=100, sample_size=3,
                                                max_concurrent=20)
            if not products:
                return JSONResponse(status_code=HTTPStatus.BAD_REQUEST,
                                    content={"message": "No products could be scraped from the provided URL"})

            # prepare file storage
            new_uuid = str(uuid.uuid4())
            filename = f"products_{new_uuid}.json"
            chatbot.products_file = filename
            chatbot.user_id = str(user_id)

            # save to DB
            inserted = await chatbot_crud.create_chatbot(chatbot)
            record = await chatbot_crud.get_chatbot_by_id(inserted.inserted_id, str(user_id))
            record = convert_object_id_to_string(record)

            # ensure directories
            scrap_dir = Path("scrapped_files") / record["_id"]
            scrap_dir.mkdir(parents=True, exist_ok=True)
            json_path = scrap_dir / filename
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(products, f, indent=2)
            logger.info(f"Saved scraped products to {json_path}")

            # build knowledge base directly from JSON file using generic loader
            kb_dir = Path("kb_storage") / record["_id"]
            kb_dir.mkdir(parents=True, exist_ok=True)
            success = build_knowledge_base(record["_id"], [str(json_path)])
            if success:
                logger.info(f"Knowledge base built for chatbot {record['_id']}")
            else:
                logger.warning(f"Failed to build knowledge base for chatbot {record['_id']}")

            return JSONResponse(status_code=HTTPStatus.CREATED,
                                content={"message": "Chatbot created successfully with knowledge base",
                                        "data": record})
        except Exception as e:
            logger.error(f"Error in create_chatbot: {e}")
            return JSONResponse(status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                content={"message": f"Internal server error: {e}"})
    
    async def read_chatbot(self, user_id: ObjectId, chatbot_id: str):
        """
        Retrieve a specific chatbot by ID.
        
        Args:
            user_id (ObjectId): The MongoDB ObjectId of the user.
            chatbot_id (str): The ID of the chatbot to retrieve.
            
        Returns:
            JSONResponse: HTTP response with status code and message:
                - 200 OK: Successful retrieval with chatbot data
                - 404 NOT_FOUND: User or chatbot not found
                - 500 INTERNAL_SERVER_ERROR: Server error with error message
        """
        try:
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
                )

            existing_chatbot = await chatbot_crud.get_chatbot_by_id(
                chatbot_id, str(user_id)
            )
            if not existing_chatbot:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": CHATBOT_NOT_FOUND_MSG},
                )

            existing_chatbot = convert_object_id_to_string(existing_chatbot)

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Chatbot Fetched successfully",
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
        """
        Process user query against a specific chatbot.
        
        This method validates the user and chatbot, then sends the user query to the
        contextual chatbot for processing and response generation.
        
        Args:
            user_id (ObjectId): The MongoDB ObjectId of the user.
            chatbot_id (str): The ID of the chatbot to query.
            query (str): The user's query text to be processed by the chatbot.
            
        Returns:
            JSONResponse: HTTP response with status code and message:
                - 200 OK: Successful query with generated response
                - 404 NOT_FOUND: User or chatbot not found
                - 403 FORBIDDEN: User doesn't have permission to access the chatbot
                - 500 INTERNAL_SERVER_ERROR: Server error with error message
        """
        try:
            logger.debug(
                f"Validating user with ID: {user_id}"
            )
            
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
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
                    content={"message": CHATBOT_NOT_FOUND_MSG},
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
            
            logger.debug("Initializing contextual chatbot with products data")
            chatbot_instance = ContextualChatbot(chatbot_data.get('products', []), chatbot_id)
            
            logger.debug(f"Generating response for query: {query}")
            response = chatbot_instance.generate_response(query)
            
            logger.info("Generated response successfully")
            
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
        """
        Update an existing chatbot's information.
        
        Args:
            user_id (ObjectId): The MongoDB ObjectId of the user.
            chatbot_id (str): The ID of the chatbot to update.
            chatbot_data (ChatbotUpdate): The updated chatbot data.
            
        Returns:
            JSONResponse: HTTP response with status code and message:
                - 200 OK: Successful update with updated chatbot data
                - 404 NOT_FOUND: User or chatbot not found
                - 500 INTERNAL_SERVER_ERROR: Server error with error message
        """
        try:
            logger.debug(
                f"Validating user with ID: {user_id}"
            )
            
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
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
                    content={"message": CHATBOT_NOT_FOUND_MSG},
                )
            
            logger.debug("Applying update to chatbot")
            await chatbot_crud.update_chatbot(chatbot_id, chatbot_data)
            
            updated_chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
            updated_chatbot = convert_object_id_to_string(updated_chatbot)
            
            logger.info("Chatbot updated successfully")
            
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
        """
        Delete a specific chatbot.
        
        This method validates the user and ensures they own the chatbot before deletion.
        
        Args:
            user_id (ObjectId): The MongoDB ObjectId of the user.
            chatbot_id (str): The ID of the chatbot to delete.
            
        Returns:
            JSONResponse: HTTP response with status code and message:
                - 200 OK: Successful deletion
                - 404 NOT_FOUND: User or chatbot not found
                - 403 FORBIDDEN: User doesn't have permission to delete the chatbot
                - 500 INTERNAL_SERVER_ERROR: Server error with error message
        """
        try:
            logger.debug(
                f"Validating user with ID: {user_id}"
            )
            
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
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
                    content={"message": CHATBOT_NOT_FOUND_MSG},
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
            
            logger.debug("Removing chatbot from database")
            await chatbot_crud.delete_chatbot(chatbot_id)
            
            logger.info("Chatbot deleted successfully")
            
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
        """
        Retrieve all chatbots owned by a specific user.
        
        Args:
            user_id (ObjectId): The MongoDB ObjectId of the user.
            
        Returns:
            JSONResponse: HTTP response with status code and message:
                - 200 OK: Successful retrieval with list of chatbots
                - 404 NOT_FOUND: User not found
                - 500 INTERNAL_SERVER_ERROR: Server error with error message
        """
        try:
            logger.debug(
                f"Validating user with ID: {user_id}"
            )
            
            if not await user_service.validate_user(user_id):
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": USER_NOT_FOUND_MSG},
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
        
        
    # async def upload_chatbot_files(self, user_id: ObjectId, chatbot_id: str, uploaded_files: List[UploadFile]):
    #     """
    #     Update files for a chatbot knowledge base.
    #     Each call completely replaces the previous set of files with the new set.
        
    #     Args:
    #         user_id: The ID of the user
    #         chatbot_id: The ID of the chatbot
    #         uploaded_files: Complete list of files that should exist after this update
    #     """
    #     try:
    #         logger.debug(f"Validating user with ID: {user_id}")
    #         if not await user_service.validate_user(user_id):
    #             return JSONResponse(
    #                 status_code=HTTPStatus.NOT_FOUND,
    #                 content={"message": USER_NOT_FOUND_MSG},
    #             )
                
    #         logger.debug(f"Fetching chatbot with ID: {chatbot_id}")
    #         chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
    #         if not chatbot:
    #             logger.info(f"Chatbot with ID {chatbot_id} not found")
    #             return JSONResponse(
    #                 status_code=HTTPStatus.NOT_FOUND,
    #                 content={"message": CHATBOT_NOT_FOUND_MSG},
    #             )
                
    #         # Get current files and prepare directory
    #         current_files = chatbot.get("knowledge_files", [])
    #         knowledge_dir = Path("knowledge_bases") / str(chatbot_id)
    #         knowledge_dir.mkdir(parents=True, exist_ok=True)
    #         db_dir = Path("db_storage") / chatbot_id
    #         db_dir.mkdir(parents=True, exist_ok=True)

    #         # 1) Detect database files by extension
    #         db_exts = {".sqlite", ".db", ".sqlite3", ".sql", ".dump"}
    #         db_candidates = [f for f in uploaded_files if Path(f.filename).suffix.lower() in db_exts]
    #         if db_candidates:
    #             # Process DB ingestion via Vanna AI
    #             from processing.db_detector import DatabaseDetector
    #             from processing.db_storage import DatabaseStorageManager

    #             detector = DatabaseDetector()
    #             storage_mgr = DatabaseStorageManager()

    #             saved_db_info = []
    #             for db_file in db_candidates:
    #                 saved_path = storage_mgr.save_uploaded_file(chatbot_id, db_file.file, db_file.filename)
    #                 detect = detector.detect_db_type(saved_path)
    #                 saved_db_info.append({
    #                     "original_name": db_file.filename,
    #                     "saved_path": str(saved_path),
    #                     "db_type": detect.get("db_type"),
    #                     **({"error": detect["error"]} if detect.get("error") else {})
    #                 })
    #             # Configure Vanna with first valid DB
    #             primary = next((d for d in saved_db_info if d["db_type"] != "unknown"), saved_db_info[0])
    #             config = {
    #                 "db_type": primary["db_type"],
    #                 "db_path": primary["saved_path"],
    #             }
    #             storage_mgr.save_config(chatbot_id, config)
    #             # rebuild_result = vanna.rebuild_kb(config)
    #             vanna.get_instance(chatbot_id)
    #             vanna.train_sqlite(config, chatbot_id)
    #             return JSONResponse(
    #                 status_code=HTTPStatus.OK,
    #                 content={
    #                     "message": "Database ingested successfully",
    #                     "processed_db_files": saved_db_info,
    #                 },
    #             )

            
    #         # Map original filenames to their UUID versions
    #         existing_files_map = {}
    #         for f in current_files:
    #             try:
    #                 parts = f.split('_', 1)
    #                 if len(parts) == 2:
    #                     uuid_part, original_name = parts
    #                     existing_files_map[original_name] = f
    #             except:
    #                 continue
                    
    #         # Get all original file names being uploaded
    #         new_file_names = [file.filename for file in uploaded_files]
            
    #         # Clean up old files that aren't in the new upload
    #         for original_name, uuid_filename in existing_files_map.items():
    #             if original_name not in new_file_names:
    #                 # Delete file that's not in the new upload
    #                 file_path = knowledge_dir / uuid_filename
    #                 if file_path.exists():
    #                     file_path.unlink()
    #                     logger.debug(f"Deleted file: {uuid_filename}")
            
    #         # Process all uploads, whether new or replacements
    #         final_files = []
    #         for new_file in uploaded_files:
    #             original_name = new_file.filename
                
    #             # If this filename already exists, delete the old version
    #             if original_name in existing_files_map:
    #                 old_path = knowledge_dir / existing_files_map[original_name]
    #                 if old_path.exists():
    #                     old_path.unlink()
                        
    #             # Save new file with UUID prefix
    #             new_uuid = str(uuid.uuid4())
    #             new_filename = f"{new_uuid}_{original_name}"
    #             file_path = knowledge_dir / new_filename
    #             with open(file_path, "wb") as buffer:
    #                 shutil.copyfileobj(new_file.file, buffer)
    #             final_files.append(new_filename)
            
    #         # Update database with complete file list
    #         chatbot_data = ChatbotUpdate(knowledge_files=final_files)
    #         await chatbot_crud.update_chatbot(chatbot_id, chatbot_data)
            
    #         # Rebuild the knowledge base after file upload
    #         from processing.kb import rebuild_kb_after_upload
    #         rebuild_result = rebuild_kb_after_upload(chatbot_id)

    #         return JSONResponse(
    #             status_code=HTTPStatus.OK,
    #             content={
    #                 "message": "Files processed successfully",
    #                 "total_files": len(final_files),
    #                 "kb_rebuilt": rebuild_result
    #             },
    #         )
    #     except Exception as e:
    #         logger.error(f"File upload failed. ERROR: {e}")
    #         return JSONResponse(
    #             status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    #             content={"message": f"Internal server error. ERROR: {e}"},
    #         )

    async def upload_chatbot_files(self, user_id: ObjectId, chatbot_id: str, uploaded_files: List[UploadFile]):
        """
        Upload and manage files for a chatbot's knowledge base.

        This method replaces the chatbot's existing knowledge base files with the new uploaded set.
        It supports both regular knowledge documents and database files (SQLite, SQL dumps, etc.).
        If database files are uploaded, they are handled separately to configure Vanna AI.

        Args:
            user_id (ObjectId): The ID of the user uploading files.
            chatbot_id (str): The ID of the chatbot for which files are uploaded.
            uploaded_files (List[UploadFile]): List of uploaded files to associate with the chatbot.

        Returns:
            JSONResponse: A response object containing status and result message.
        """
        try:
            # Validate user and chatbot
            validation_response = await self._validate_user_and_chatbot(user_id, chatbot_id)
            if isinstance(validation_response, JSONResponse):
                return validation_response
            
            chatbot = validation_response
            
            # Prepare directories
            knowledge_dir, db_dir = self._prepare_directories(chatbot_id)
            
            # Check for database files and process them if found
            db_candidates = self._get_database_files(uploaded_files)
            if db_candidates:
                return await self._process_database_files(chatbot_id, db_candidates)
            
            # Process regular files
            current_files = chatbot.get("knowledge_files", [])
            existing_files_map = self._map_existing_files(current_files)
            
            # Clean up old files
            self._clean_up_old_files(
                knowledge_dir, 
                existing_files_map, 
                [file.filename for file in uploaded_files]
            )
            
            # Process new files
            final_files = self._process_new_files(knowledge_dir, existing_files_map, uploaded_files)
            
            # Update database and rebuild knowledge base
            return await self._update_chatbot_and_rebuild_kb(chatbot_id, final_files)
            
        except Exception as e:
            logger.error(f"File upload failed. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )

    async def _validate_user_and_chatbot(self, user_id, chatbot_id):
        """
        Validates the existence of the user and the chatbot.

        Args:
            user_id (ObjectId): The ID of the user.
            chatbot_id (str): The ID of the chatbot.

        Returns:
            Union[dict, JSONResponse]: The chatbot document if found, otherwise a JSON error response.
        """
        logger.debug(f"Validating user with ID: {user_id}")
        if not await self.validate_user(user_id):
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content={"message": USER_NOT_FOUND_MSG},
            )
                
        logger.debug(f"Fetching chatbot with ID: {chatbot_id}")
        chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
        if not chatbot:
            logger.info(f"Chatbot with ID {chatbot_id} not found")
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content={"message": CHATBOT_NOT_FOUND_MSG},
            )
        
        return chatbot

    def _prepare_directories(self, chatbot_id):
        """
        Prepare the directory structure for storing knowledge and database files.

        Args:
            chatbot_id (str): The ID of the chatbot.

        Returns:
            Tuple[Path, Path]: Paths to the knowledge base directory and database directory.
        """

        knowledge_dir = Path("knowledge_bases") / str(chatbot_id)
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        db_dir = Path("db_storage") / chatbot_id
        db_dir.mkdir(parents=True, exist_ok=True)
        
        return knowledge_dir, db_dir

    def _get_database_files(self, uploaded_files):
        """
        Identify uploaded files that are database files based on their extension.

        Args:
            uploaded_files (List[UploadFile]): List of uploaded files.

        Returns:
            List[UploadFile]: List of database file candidates.
        """

        db_exts = {".sqlite", ".db", ".sqlite3", ".sql", ".dump"}
        return [f for f in uploaded_files if Path(f.filename).suffix.lower() in db_exts]

    async def _process_database_files(self, chatbot_id, db_candidates):
        """
        Handle database file ingestion and Vanna AI configuration.

        Args:
            chatbot_id (str): The ID of the chatbot.
            db_candidates (List[UploadFile]): List of uploaded database files.

        Returns:
            JSONResponse: A response containing success message and processing results.
        """

        from processing.db_detector import DatabaseDetector
        from processing.db_storage import DatabaseStorageManager
        
        detector = DatabaseDetector()
        storage_mgr = DatabaseStorageManager()
        saved_db_info = []
        
        for db_file in db_candidates:
            saved_path = storage_mgr.save_uploaded_file(chatbot_id, db_file.file, db_file.filename)
            detect = detector.detect_db_type(saved_path)
            saved_db_info.append({
                "original_name": db_file.filename,
                "saved_path": str(saved_path),
                "db_type": detect.get("db_type"),
                **({"error": detect["error"]} if detect.get("error") else {})
            })
        
        # Configure Vanna with first valid DB
        primary = next((d for d in saved_db_info if d["db_type"] != "unknown"), saved_db_info[0])
        config = {
            "db_type": primary["db_type"],
            "db_path": primary["saved_path"],
        }
        
        storage_mgr.save_config(chatbot_id, config)
        vanna.get_instance(chatbot_id)
        vanna.train_sqlite(config, chatbot_id)
        
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={
                "message": "Database ingested successfully",
                "processed_db_files": saved_db_info,
            },
        )

    def _map_existing_files(self, current_files):
        """
        Map original filenames to the existing stored UUID-prefixed versions.

        Args:
            current_files (List[str]): List of filenames already stored.

        Returns:
            Dict[str, str]: Mapping from original filename to stored UUID-prefixed filename.
        """

        existing_files_map = {}
        for f in current_files:
            try:
                parts = f.split('_', 1)
                if len(parts) == 2:
                    uuid_part, original_name = parts
                    existing_files_map[original_name] = f
            except (AttributeError, ValueError) as e:
                print(uuid_part)
                print(f"Error processing file {f}: {str(e)}")
                continue
        
        return existing_files_map

    def _clean_up_old_files(self, knowledge_dir, existing_files_map, new_file_names):
        """
        Remove files from disk that are not part of the new upload.

        Args:
            knowledge_dir (Path): Directory where knowledge files are stored.
            existing_files_map (Dict[str, str]): Mapping of original filenames to stored versions.
            new_file_names (List[str]): Filenames that are being uploaded in this update.
        """

        for original_name, uuid_filename in existing_files_map.items():
            if original_name not in new_file_names:
                file_path = knowledge_dir / uuid_filename
                if file_path.exists():
                    file_path.unlink()
                    logger.debug(f"Deleted file: {uuid_filename}")

    def _process_new_files(self, knowledge_dir, existing_files_map, uploaded_files):
        """
        Save uploaded files to disk, replacing existing ones if necessary.

        Args:
            knowledge_dir (Path): Directory where knowledge files are stored.
            existing_files_map (Dict[str, str]): Mapping of original filenames to stored versions.
            uploaded_files (List[UploadFile]): List of uploaded files.

        Returns:
            List[str]: List of stored filenames with UUID prefixes.
        """

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
        
        return final_files

    async def _update_chatbot_and_rebuild_kb(self, chatbot_id, final_files):
        """
        Update chatbot record in the database and trigger knowledge base rebuild.

        Args:
            chatbot_id (str): The ID of the chatbot.
            final_files (List[str]): List of processed and stored knowledge files.

        Returns:
            JSONResponse: A response indicating the result of the update and rebuild.
        """
        chatbot_data = ChatbotUpdate(knowledge_files=final_files)
        await chatbot_crud.update_chatbot(chatbot_id, chatbot_data)

        # Rebuild the knowledge base after file upload
        from processing.kb import rebuild_kb_after_upload
        rebuild_result = rebuild_kb_after_upload(chatbot_id)

        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={
                "message": "Files processed successfully",
                "total_files": len(final_files),
                "kb_rebuilt": rebuild_result
            },
        )
            
    async def get_leads_by_chatbot_id(self, user_id: ObjectId, chatbot_id: str):
        """
        Retrieve all lead conversations associated with a given chatbot.

        Args:
            user_id (ObjectId): ID of the user requesting the leads.
            chatbot_id (str): ID of the chatbot whose leads are to be fetched.

        Returns:
            JSONResponse: Response containing list of leads or an error message.
        """
        logger.debug(f"Validating user with ID: {user_id}")
        if not await user_service.validate_user(user_id):
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content={"message": USER_NOT_FOUND_MSG},
            )
            
        logger.debug(f"Fetching chatbot with ID: {chatbot_id}")
        chatbot = await chatbot_crud.get_chatbot_by_id(chatbot_id, str(user_id))
        if not chatbot:
            logger.info(f"Chatbot with ID {chatbot_id} not found")
            return JSONResponse(
                status_code=HTTPStatus.NOT_FOUND,
                content={"message": "Chatbot not found"},
            )
        
        leads = await chatbot_conversation_crud.get_leads_by_chatbot_id(
        chatbot_id
        )
            
        return JSONResponse(
            status_code=HTTPStatus.OK,
            content={
                "message": f"Leads retrieved successfully for chatbot ID {chatbot_id}",
                "data": leads,
            },
        )