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

    async def validate_user(self, user_id: ObjectId):
        logger.debug(f"Validating user with ID: {user_id}")
        user = await user_crud.get_user_by_id(user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found")
            return None
        logger.info(f"User with ID {user_id} found")
        return user

    async def get_self_details(self, user_id: ObjectId):
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

    async def update_self_details(
        self, user_id: ObjectId, updated_data: UpdateUserRequest
    ):
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
