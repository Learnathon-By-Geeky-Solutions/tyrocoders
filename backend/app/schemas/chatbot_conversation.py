"""
Conversation Models for Chatbot System

This module contains Pydantic models representing different types of conversations
and messages in a chatbot system. These models are used for validating and serializing
data related to lead collection, handover messages, conversation updates, and more.

Each model has an associated `Config` class to customize its behavior, including
providing example data for Swagger UI or other documentation generation tools.

Models:
    - LeadCollectConversation: Represents the structure of data for collecting leads
      during a conversation.
    - HandoverMessageConversation: Represents the structure of data for sending a 
      handover message.
    - DeleteConversationIds: Represents the structure for deleting multiple conversations
      by their IDs.
    - ContinueConversation: Represents the structure for continuing a conversation
      with a new user message.
    - UpdateConversationTag: Represents the structure for updating conversation tags
      and feedback.
    - UpdateSingleConversation: Represents the structure for updating a single conversation's message.
    - ConversationMessage: Represents a single message in a conversation with its metadata.
    - ChatbotConversationModel: Represents a full chatbot conversation, including 
      its history and metadata.
"""

from bson import ObjectId
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict

class LeadCollectConversation(BaseModel):
    """
    Model for collecting lead information during a conversation.
    
    This model is used to capture the details provided by the user, including their 
    email, name, phone number, company, and position.

    Attributes:
        collect_lead_fields (Optional[List[Dict[str, str]]]): List of fields collected
            from the user during the conversation.
    """
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
    """
    Model for handling handover messages during a conversation.

    This model represents a handover message containing the user's email and the 
    message they want to send to a human agent.

    Attributes:
        email (EmailStr): The email of the user.
        message (str): The message that the user wants to send.
    """
    email: EmailStr
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "mohtasim@gmail.com",
                "message": "I would like to know in details about this packages"
            }
        }

class DeleteConversationIds(BaseModel):
    """
    Model for deleting multiple conversations based on their IDs.

    Attributes:
        conversation_ids (List[str]): List of conversation IDs to be deleted.
    """
    conversation_ids: List[str] = [
        "67077476f896412f11e8a7c8",
        "67077476f896412f11e8a7c9",
    ]

class ContinueConversation(BaseModel):
    """
    Model for continuing a conversation with a new user message.

    Attributes:
        user_message (str): The message provided by the user to continue the conversation.
    """
    user_message: str = "Give me a list of popular topics"

class UpdateConversationTag(BaseModel):
    """
    Model for updating the tags and feedback of a conversation.

    Attributes:
        tags (List[str]): List of tags associated with the conversation.
        feedback (str): Feedback on the conversation.
    """
    tags: List[str] = ["important", "urgent"]
    feedback: str = "Neutral"

class UpdateSingleConversation(BaseModel):
    """
    Model for updating a single message in a conversation.

    Attributes:
        conversation_id (str): The ID of the conversation to be updated.
        message_id (str): The ID of the message to be updated.
        new_message (str): The new message content.
    """
    conversation_id: str
    message_id: str
    new_message: str

class ConversationMessage(BaseModel):
    """
    Model for a single message within a conversation.

    Attributes:
        message (str): The content of the message.
        sender (str): The sender of the message (either 'user' or 'bot').
        timestamp (int): The timestamp of when the message was sent.
        confidence_score (float): The confidence score of the message from the bot.
    """
    message: str
    sender: str
    timestamp: int
    confidence_score: float

class ChatbotConversationModel(BaseModel):
    """
    Model representing a full chatbot conversation, including metadata and history.

    Attributes:
        _id (ObjectId): The unique identifier of the conversation.
        chatbot_id (str): The ID of the chatbot handling the conversation.
        chatbot_name (str): The name of the chatbot.
        user_id (str): The ID of the user interacting with the chatbot.
        started_on (int): The timestamp when the conversation started.
        most_recent (int): The timestamp of the most recent message.
        confidence (float): The overall confidence score for the conversation.
        total_messages (int): The total number of messages in the conversation.
        feedback (str): The feedback on the conversation.
        channel (str): The communication channel used (e.g., Web).
        is_live_now (bool): Whether the conversation is currently live.
        live_chat_info (dict): Information about the live chat, if applicable.
        conversation_history (List[ConversationMessage]): List of messages exchanged in the conversation.
    """
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
