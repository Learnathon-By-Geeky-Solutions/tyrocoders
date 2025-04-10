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
    description: Optional[str] = None
    is_active: bool = True
    user_id: Optional[str] = None
    products_file: Optional[str] = None  

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
    products_file: Optional[str] = None

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
