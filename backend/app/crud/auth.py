"""
Authentication CRUD Operations

This module handles user registration and password reset operations for admin users
stored in a MongoDB collection.

Dependencies:
- `UserCreate` schema for user input validation.
- `base_admin_users_collection` for MongoDB connection.
"""

from schemas.auth import UserCreate
from db.mongodb import base_admin_users_collection
from datetime import datetime, timedelta
import secrets


class AuthCrud:
    """
    CRUD operations for authentication-related tasks such as registering
    new users and resetting passwords for admin users.
    """

    def __init__(self):
        """
        Initializes the AuthCrud class with the base admin users MongoDB collection.
        """
        self.collection = base_admin_users_collection

    async def register(self, user: UserCreate):
        """
        Registers a new admin user.

        Args:
            user (UserCreate): A validated UserCreate object containing the user's
                               username, password, email, and name.

        Returns:
            InsertOneResult: The result of the insert operation from MongoDB.
        """
        collection = self.collection

        new_user = await collection.insert_one(
            {
                "username": user.username,
                "password": user.password,  # Should ideally be hashed before storage
                "email": user.email,
                "name": user.name,
            }
        )
        return new_user

    async def password_reset(self, email: str, new_password: str):
        """
        Resets the password for an existing user with the given email.

        Args:
            email (str): The email address of the user.
            new_password (str): The new password to set (should be hashed).

        Returns:
            bool: True if the password was successfully updated, False if no user was found.
        """
        user = await self.collection.find_one({"email": email})
        if user:
            user["password"] = new_password  # Replace with hashed password in production
            await self.collection.update_one({"email": email}, {"$set": user})
            return True
        return False
