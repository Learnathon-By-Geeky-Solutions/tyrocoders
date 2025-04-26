from schemas.auth import UserCreate
from db.mongodb import base_admin_users_collection 
from datetime import datetime, timedelta
import secrets


class AuthCrud():
    def __init__(self):
        self.collection = base_admin_users_collection

    async def register(self, user: UserCreate):
        collection = self.collection

        new_user = await collection.insert_one(
            {
                "username": user.username,
                "password": user.password,
                "email": user.email,
                "name": user.name,
            }
        )
        return new_user

    async def password_reset(self, email: str, new_password: str):
        user = await self.collection.find_one({"email": email})
        if user:
            user["password"] = new_password
            await self.collection.update_one({"email": email}, {"$set": user})
            return True
        return False