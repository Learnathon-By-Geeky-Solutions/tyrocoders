from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field
import re

class UpdateUserRequest(BaseModel):
    """
    Model representing a request to update user information.

    This model is used for handling user information updates, such as changing the username, name, email, and password. 
    It includes validation for password complexity and ensures that the provided fields meet the required conditions.

    Attributes:
        username (str): The username of the user. Must be at least 3 characters long.
        name (str): The full name of the user. Must be at least 3 characters long.
        email (EmailStr, optional): The email address of the user. If provided, must be a valid email format.
        password (str): The password of the user. Must be at least 8 characters long and meet specific complexity requirements.

    Example:
        {
            "username": "mohtasim",
            "name": "M. Mohtasim Hossain",
            "email": "mohtasim@gmail.com",
            "password": "Strongpassword123@"
        }

    Validators:
        - `password_complexity`: Ensures that the password contains at least one uppercase letter, one lowercase letter,
          one number, and one special character.
    """
    
    username: Optional[str] = Field(..., min_length=3)
    name: Optional[str] = Field(..., min_length=3)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(..., min_length=8)

    class Config:
        """
        Configuration class for the Pydantic model. It includes customization for additional fields and provides an example schema.
        """
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
        """
        Validates the complexity of the provided password to ensure it meets the required conditions.

        - Password must contain at least one uppercase letter.
        - Password must contain at least one lowercase letter.
        - Password must contain at least one number.
        - Password must contain at least one special character (e.g., !, @, #, etc.).

        Args:
            value (str): The password to be validated.

        Raises:
            ValueError: If the password does not meet the complexity requirements.

        Returns:
            str: The validated password value.
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