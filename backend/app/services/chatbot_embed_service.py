from http import HTTPStatus
from bson import ObjectId
from fastapi.responses import JSONResponse
from services.chatbot_service import ChatbotService
from services.user_service import UserService
from utils.converter import convert_object_id_to_string
from crud.user import UserCrud
from core.logger import logger

user_crud = UserCrud()
user_service = UserService()
user_service = UserService()
chatbot_service = ChatbotService()


class ChatbotEmbedService:
    pass