from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

class ProductSchema(BaseModel):
    name: str
    price: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Product Name",
                "price": "$99.99",
                "description": "This is a product description",
                "url": "https://example.com/product",
                "image_url": "https://example.com/image.jpg"
            }
        }

class ChatbotCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    website_url: HttpUrl
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    products: List[ProductSchema] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Store Chatbot",
                "website_url": "https://example.com",
                "description": "A chatbot for my online store",
                "is_active": True
            }
        }

class ChatbotUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    website_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    products: Optional[List[ProductSchema]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Updated Chatbot Name",
                "description": "Updated chatbot description",
                "is_active": False
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