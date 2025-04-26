from pydantic import BaseModel, EmailStr, validator, constr, Field
from datetime import datetime, timedelta
import re, secrets
from typing import Optional

PASSWORD_SUGGEST = "Strongpassword123@"

class UserCreate(BaseModel):
    username: Optional[str] = Field(..., min_length=3)
    name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=8)

    class Config:
        extra = "allow"
        json_schema_extra = {
            "example": {
                "username": "mohtasim",
                "name": "M. Mohtasim Hossain",
                "email": "mohtasim@gmail.com",
                "password": PASSWORD_SUGGEST,
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


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "mohtasim@gmail.com",
                "password": "Temp@1234"
            }
        }


class GenerateResetPassword(BaseModel):
    reset_form_url: str
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "email": "test@example.com",
                "reset_form_url": "http://localhost:8000/reset-password",
            }
        }


class ResetPassword(BaseModel):
    pass_reset_token: str
    new_password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "pass_reset_token": "zzzzzzzzzzzzzzzzzzzzz",
                "new_password": PASSWORD_SUGGEST,
            }
        }

    @validator("new_password")
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


class RefreshTokenRequest(BaseModel):
    refresh_token: str = "dasdasdsadsad"
