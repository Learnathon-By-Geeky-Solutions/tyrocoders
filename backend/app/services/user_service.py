from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from bson import ObjectId
from fastapi.responses import JSONResponse
from schemas.user import UpdateUserRequest
from utils.converter import convert_object_id_to_string
from crud.user import UserCrud
from crud.chatbot_conversation import ChatbotConversationCrud
from core.logger import logger
from crud.chatbot import ChatbotCrud
from utils.hashing import hash_password

user_crud = UserCrud()
chatbot_conversation_crud = ChatbotConversationCrud()
chatbot_crud = ChatbotCrud()

class UserService:
    """
    Service class responsible for handling user-related business logic such as validation,
    retrieving self details, and updating profile information.

    Utilizes CRUD operations through `UserCrud`, `ChatbotCrud`, and `ChatbotConversationCrud`.
    Logs important events and returns consistent JSON responses.
    """


    async def validate_user(self, user_id: ObjectId):
        """
        Validates whether a user with the given ObjectId exists in the database.

        Args:
            user_id (ObjectId): The ID of the user to validate.

        Returns:
            dict or None: The user document if found, otherwise None.

        Logs:
            - DEBUG when validation starts.
            - INFO if user is found or not.
        """

        logger.debug(f"Validating user with ID: {user_id}")
        user = await user_crud.get_user_by_id(user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found")
            return None
        logger.info(f"User with ID {user_id} found")
        return user

    async def get_self_details(self, user_id: ObjectId):
        """
        Retrieves the authenticated user's own details.

        Args:
            user_id (ObjectId): The ID of the user requesting their information.

        Returns:
            JSONResponse: HTTP 200 with user details if successful.
                          HTTP 404 if user not found.
                          HTTP 500 on server error.

        Logs:
            - ERROR if an exception occurs during data retrieval.
        """

        try:
            user = await self.validate_user(user_id)
            if not user:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )

            user = convert_object_id_to_string(user)

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "User details retrieved successfully",
                    "data": user,
                },
            )
        except Exception as e:
            logger.error(
                f"User id: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )

    async def update_self_details(self, user_id: ObjectId, updated_data: UpdateUserRequest):
        """
        Updates the authenticated user's profile details.

        Args:
            user_id (ObjectId): The ID of the user making the update.
            updated_data (UpdateUserRequest): A Pydantic model containing updated fields,
                                              including an optional password.

        Returns:
            JSONResponse: HTTP 200 with updated user details if successful.
                          HTTP 404 if user is not found.
                          HTTP 500 on server error.

        Notes:
            - If a password is provided, it is hashed before storage.
            - Converts ObjectId fields to strings before returning to frontend.

        Logs:
            - DEBUG for update operation start.
            - INFO on successful update.
            - ERROR if an exception occurs.
        """

        try:
            user = await self.validate_user(user_id)
            if not user:
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )

            logger.debug(
                f"User id: {user_id} | Updating user details"
            )
            if updated_data.password:
                updated_data.password = hash_password(updated_data.password)

            await user_crud.update_user(user_id, updated_data)
            updated_user = await user_crud.get_user_by_id(user_id)
            updated_user = convert_object_id_to_string(updated_user)

            logger.info(
                f"User id: {user_id} | User updated successfully"
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "User updated successfully",
                    "data": updated_user,
                },
            )
        except Exception as e:
            logger.error(
                f"User id: {user_id} | Internal server error. ERROR: {e}"
            )
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
