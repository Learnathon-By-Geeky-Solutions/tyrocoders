from pydantic import BaseModel, EmailStr, validator, constr, Field
from datetime import datetime, timedelta
import re, secrets
from typing import Optional

PASSWORD_SUGGEST = "Strongpassword123@"

class UserCreate(BaseModel):
    """
    Model for user creation.

    This model is used for creating a new user with the required information.
    It includes fields for the username, name, email, and password. The password is validated
    to ensure it meets specific complexity requirements (uppercase, lowercase, number, and special character).

    Attributes:
        username (Optional[str]): The unique username for the user, must be at least 3 characters long.
        name (str): The full name of the user, must be at least 3 characters long.
        email (EmailStr): The user's email address.
        password (str): The user's password, must be at least 8 characters long and meet complexity requirements.

    Example:
        {
            "username": "mohtasim",
            "name": "M. Mohtasim Hossain",
            "email": "mohtasim@gmail.com",
            "password": "Strongpassword123@"
        }
    """
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
        """
        Validates the complexity of the password to ensure it meets required security standards.
        
        Password must contain:
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one number
            - At least one special character
        """
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
    """
    Model for user login.

    This model is used when a user attempts to log in with their email and password.

    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.

    Example:
        {
            "email": "mohtasim@gmail.com",
            "password": "Strongpassword123@"
        }
    """
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "mohtasim@gmail.com",
                "password": PASSWORD_SUGGEST
            }
        }


class GenerateResetPassword(BaseModel):
    """
    Model for generating a password reset request.

    This model is used when a user requests to reset their password. It includes the user's email
    and the URL to the reset password form.

    Attributes:
        reset_form_url (str): The URL where the user can reset their password.
        email (EmailStr): The user's email address.

    Example:
        {
            "email": "test@example.com",
            "reset_form_url": "http://localhost:8000/reset-password",
        }
    """
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
    """
    Model for resetting a user's password.

    This model is used when a user submits a password reset request with a reset token and a new password.

    Attributes:
        pass_reset_token (str): The token received for resetting the password.
        new_password (str): The new password for the user, must meet complexity requirements.

    Example:
        {
            "pass_reset_token": "zzzzzzzzzzzzzzzzzzzzz",
            "new_password": "Strongpassword123@"
        }
    """
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
        """
        Validates the complexity of the new password to ensure it meets required security standards.
        
        New password must contain:
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one number
            - At least one special character
        """
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
    """
    Model for refreshing a user's session with a new refresh token.

    Attributes:
        refresh_token (str): The refresh token used to obtain a new session token.

    Example:
        {
            "refresh_token": "dasdasdsadsad"
        }
    """
    refresh_token: str = "dasdasdsadsad"
