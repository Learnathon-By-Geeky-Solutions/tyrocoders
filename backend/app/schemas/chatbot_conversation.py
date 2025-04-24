from bson import ObjectId
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict

class LeadCollectConversation(BaseModel):
    collect_lead_fields: Optional[List[Dict[str, str]]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "collect_lead_fields": [
                    {"field_name": "email", "field_value": "test@gmail.com"},
                    {"field_name": "name", "field_value": "Mohtasim"},
                    {"field_name": "phone", "field_value": "01717171717"},
                    {"field_name": "company", "field_value": "TechCorp"},
                    {"field_name": "position", "field_value": "Software Engineer"},
                ]
            }
        }

class HandoverMessageConversation(BaseModel):
    email: EmailStr
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "mohtasim@gmail.com",
                "password": "I would like to know in details about this packages"
            }
        }


class DeleteConversationIds(BaseModel):
    conversation_ids: List[str] = [
        "67077476f896412f11e8a7c8",
        "67077476f896412f11e8a7c9",
    ]


class ContinueConversation(BaseModel):
    user_message: str = "Give me a list of popular topics"


class UpdateConversationTag(BaseModel):
    tags: List[str] = ["important", "urgent"]
    feedback: str = "Neutral"


class UpdateSingleConversation(BaseModel):
    conversation_id: str
    message_id: str
    new_message: str


class ConversationMessage(BaseModel):
    message: str
    sender: str
    timestamp: int
    confidence_score: float


class ChatbotConversationModel(BaseModel):
    _id: ObjectId
    chatbot_id: str
    chatbot_name: str
    user_id: str
    started_on: int
    most_recent: int
    confidence: float
    total_messages: int
    feedback: str
    channel: str
    is_live_now: bool
    live_chat_info: dict
    conversation_history: List[ConversationMessage]

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "_id": "67077476f896412f11e8a7c8",
                "chatbot_id": "6707690ec8eccff0b68404fd",
                "chatbot_name": "MyChatbot",
                "user_id": "6704d45c69b205813bccec23",
                "started_on": 1728541814,
                "most_recent": 1728541814,
                "tags": ["important", "urgent"],
                "email": "test@gmail.com",
                "name": "John",
                "phone": "01717171717",
                "confidence": 0.9,
                "total_messages": 4,
                "feedback": "Neutral",
                "channel": "Web",
                "is_live_now": False,
                "conversation_history": [
                    {
                        "message": "Hello, my name is MyChatbot. How may I help you today?",
                        "sender": "bot",
                        "timestamp": 1728541814,
                        "confidence_score": 0.9,
                    },
                    {
                        "message": "Give me a list of popular topics",
                        "sender": "user",
                        "timestamp": 1728541814,
                        "confidence_score": 0.9,
                    },
                ],
            }
        }
