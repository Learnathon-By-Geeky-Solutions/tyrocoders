from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class ProductSchema(BaseModel):
    """
    Model for product details.

    This model represents a product and includes various attributes such as the product's URL,
    name, description, SKU, images, pricing information, availability, and more.

    Attributes:
        url (HttpUrl): The product's URL on the website.
        name (str): The name of the product.
        description (Optional[str]): A description of the product (optional).
        sku (Optional[str]): The product's SKU (optional).
        image (List[HttpUrl]): A list of URLs pointing to product images.
        originalPrice (Optional[str]): The original price of the product (optional).
        discount (Optional[str]): The discounted price of the product (optional).
        priceCurrency (Optional[str]): The currency in which the product is priced (optional).
        availability (Optional[str]): The availability status of the product (optional).
        seller (Optional[str]): The seller's name or ID (optional).
        ratingValue (Optional[str]): The product's rating value (optional).
        ratingCount (Optional[str]): The number of ratings the product has received (optional).

    Example:
        {
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
    """
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
    """
    Model for creating a new chatbot.

    This model is used to create a new chatbot for a website. It includes basic information such as the chatbot's
    name, website URL, AI model name, and other optional fields like description, user ID, and product file.

    Attributes:
        name (str): The name of the chatbot.
        website_url (HttpUrl): The URL of the website where the chatbot will be deployed.
        ai_model_name (str): The name of the AI model being used for the chatbot.
        description (Optional[str]): A description of the chatbot (optional).
        is_active (bool): Whether the chatbot is active or not.
        user_id (Optional[str]): The user ID associated with the chatbot (optional).
        products_file (Optional[str]): A file containing the products the chatbot can recommend (optional).

    Example:
        {
            "name": "My Store Chatbot",
            "website_url": "https://example.com",
            "ai_model_name": "GPT-4o",
            "description": "A chatbot for my online store",
            "is_active": True
        }
    """
    name: str = Field(..., min_length=3, max_length=100)
    website_url: HttpUrl
    ai_model_name: str
    description: Optional[str] = None
    is_active: bool = True
    user_id: Optional[str] = None
    products_file: Optional[str] = None  

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
    """
    Model for lead collection field.

    This model defines a field used for collecting additional lead information during a conversation.
    
    Attributes:
        field_name (str): The name of the field.
        field_question (str): The question related to the field for collecting information.

    Example:
        {
            "field_name": "location",
            "field_question": "Where are you located?"
        }
    """
    field_name: str
    field_question: str

class ChatbotUpdate(BaseModel):
    """
    Model for updating chatbot configuration.

    This model allows for updating the configuration of an existing chatbot. It includes options for modifying
    basic information, appearance settings, conversation rules, lead collection settings, and human handover options.

    Attributes:
        name (Optional[str]): The name of the chatbot (optional).
        description (Optional[str]): A description of the chatbot (optional).
        website_url (Optional[HttpUrl]): The website URL (optional).
        is_active (Optional[bool]): Whether the chatbot is active (optional).
        ai_model_name (Optional[str]): The name of the AI model used by the chatbot (optional).
        role_of_chatbot (Optional[str]): The role or purpose of the chatbot (optional).
        language (Optional[str]): The language the chatbot speaks (optional).
        upload_files (Optional[List[str]]): Files that the chatbot can use (optional).

        appearance (Optional): Settings for the chatbot's appearance such as color, avatar, and bubble style.

        conversation (Optional): Settings related to chatbot conversation, such as messages and predefined questions.

        lead_collection (Optional): Configuration for collecting leads from users during conversations.

        human_handover (Optional): Settings for human handover, if enabled, including triggers and emails.

    Example:
        {
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
    """
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    website_url: Optional[HttpUrl] = None
    is_active: Optional[bool] = None
    ai_model_name: Optional[str] = None
    role_of_chatbot: Optional[str] = None
    language: Optional[str] = None
    upload_files: Optional[List[str]] = None

    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None
    chat_bubble_style: Optional[str] = None
    font_style: Optional[str] = None
    position: Optional[str] = None

    welcome_message: Optional[str] = None
    predefined_questions: Optional[List[str]] = None
    fallback_message: Optional[str] = None

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
    """
    Model for a chatbot query request.

    This model represents a user query sent to the chatbot.

    Attributes:
        query (str): The query text that the user asks the chatbot.

    Example:
        {
            "query": "What products do you have available?"
        }
    """
    query: str = Field(..., min_length=1, max_length=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What products do you have available?"
            }
        }
