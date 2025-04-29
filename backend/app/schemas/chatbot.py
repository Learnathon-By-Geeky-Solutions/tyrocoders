from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class ProductSchema(BaseModel):
    url: HttpUrl
    name: str
    description: Optional[str] = None
    sku: Optional[str] = None
    image: List[HttpUrl] = []
    originalPrice: Optional[str] = None
    discount: Optional[str] = None
    priceCurrency: Optional[str] = None
    availability: Optional[str] = None
    seller: Optional[str] = None
    ratingValue: Optional[str] = None
    ratingCount: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/product",
                "name": "Product Name",
                "description": "This is a product description",
                "sku": "ABC123",
                "image": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ],
                "originalPrice": "99.99",
                "discount": "79.99",
                "priceCurrency": "USD",
                "availability": "In Stock",
                "seller": "Example Seller",
                "ratingValue": "4.5",
                "ratingCount": "100"
            }
        }

class ChatbotCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    website_url: HttpUrl
    ai_model_name: str
    description: Optional[str] = None
    is_active: bool = True
    user_id: Optional[str] = None
    products_file: Optional[str] = None  
    sitemap_url: Optional[HttpUrl] = None

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "name": "My Store Chatbot",
                "website_url": "https://example.com",
                "ai_model_name": "GPT-4o",
                "description": "A chatbot for my online store",
                "is_active": True
            }
        }

class LeadField(BaseModel):
    field_name: str
    field_question: str

class ChatbotUpdate(BaseModel):
    # Basic Info
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    ai_model_name: Optional[str] = None
    role_of_chatbot: Optional[str] = None
    language: Optional[str] = None
    upload_files: Optional[List[str]] = None

    # Appearance
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    chat_bubble_style: Optional[str] = None  # e.g., 'sharp', 'rounded'
    font_style: Optional[str] = None  # e.g., 'modern', 'classic'
    position: Optional[str] = None  # e.g., 'left', 'right'

    # Conversation
    welcome_message: Optional[str] = None
    predefined_questions: Optional[List[str]] = None
    fallback_message: Optional[str] = None

    # Lead Collection
    enable_lead_collection: Optional[bool] = None
    lead_collection_after_messages: Optional[int] = None
    collect_name: Optional[bool] = None
    collect_name_question: Optional[str] = None
    collect_email: Optional[bool] = None
    collect_email_question: Optional[str] = None
    collect_phone: Optional[bool] = None
    collect_phone_question: Optional[str] = None
    additional_lead_fields: Optional[List[LeadField]] = None
    send_email_on_lead_capture: Optional[bool] = None

    # Human Handover (basic)
    enable_human_handover: Optional[bool] = None
    human_handover_trigger_message_count: Optional[int] = None
    human_handover_message: Optional[str] = None
    handover_emails: Optional[List[str]] = None

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "name": "ShopAssist Pro",
                "description": "Smart assistant to guide customers in product selection.",
                "is_active": True,
                "primary_color": "#4F46E5",
                "secondary_color": "#818CF8",
                "avatar_url": "https://api.dicebear.com/6.x/bottts/svg?seed=shop",
                "chat_bubble_style": "sharp",
                "font_style": "modern",
                "position": "right",
                "welcome_message": "Welcome to our shop! How can I help you find the perfect product today?",
                "predefined_questions": [
                    "What are your shipping options?",
                    "Do you have a return policy?",
                    "What's your best-selling product?",
                    "Are there any current promotions?"
                ],
                "fallback_message": "Sorry, I didn't understand that.",
                "enable_lead_collection": True,
                "lead_collection_after_messages": 2,
                "collect_name": True,
                "collect_name_question": "May I have your name?",
                "collect_email": True,
                "collect_email_question": "What's your email address?",
                "collect_phone": True,
                "collect_phone_question": "Can you share your phone number?",
                "additional_lead_fields": [
                    {"field_name": "location", "field_question": "Where are you located?"}
                ],
                "send_email_on_lead_capture": True,
                "enable_human_handover": True,
                "human_handover_trigger_message_count": 3,
                "human_handover_message": "Let me connect you with a human support agent.",
                "handover_emails": ["support@shop.com"]
            }
        }


class ChatbotQueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What products do you have available?"
            }
        }
