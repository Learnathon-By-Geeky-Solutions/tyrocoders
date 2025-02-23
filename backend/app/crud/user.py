import datetime
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from db.mongodb import base_admin_users_collection 



class UserCrud():
    def __init__(self):
        self.collection = base_admin_users_collection

    async def get_all_users(self):
        collection = self.collection
        users = []
        async for user in collection.find():
            users.append(user)
        return users

    async def get_user_by_email(self, email: str):
        collection = self.collection
        user = await collection.find_one({"email": email})
        return user

    async def get_user_by_username(self, username: str):
        collection = self.collection
        user = await collection.find_one({"username": username})
        return user

    async def get_user_by_id(self, user_id: ObjectId):
        collection = self.collection
        user = await collection.find_one({"_id": user_id})
        return user