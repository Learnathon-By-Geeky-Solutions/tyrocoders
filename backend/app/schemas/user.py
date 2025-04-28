from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field
import re
    
class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(..., min_length=3)
    name: Optional[str] = Field(..., min_length=3)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(..., min_length=8)

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                 "username": "mohtasim",
                "name": "M. Mohtasim Hossain",
                "email": "mohtasim@gmail.com",
                "password": "Strongpassword123@"
            }
        }

    @validator("password")
    def password_complexity(cls, value):
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[^\w\s]", value):
            raise ValueError("Password must contain at least one special character")
        return value