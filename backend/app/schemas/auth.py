from pydantic import BaseModel, EmailStr, validator, constr, Field
from datetime import datetime, timedelta
import re, secrets
from typing import Optional

class UserCreate(BaseModel):
    username: Optional[constr(min_length=3)] = Field(
        default_factory=lambda: "user_" + secrets.token_hex(4)
    )
    name: constr(min_length=3)
    email: EmailStr
    password: constr(min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "username": "user_ab12cd34",  # Example output from the lambda function.
                "name": "M. Mohtasim Hossain",
                "email": "mohtasim@gmail.com",
                "password": "Strongpassword123@",
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
                "password": "Strongpassword123@"
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
    new_password: constr(min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "pass_reset_token": "zzzzzzzzzzzzzzzzzzzzz",
                "new_password": "Strongpassword123@",
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
