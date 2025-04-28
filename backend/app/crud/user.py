from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from schemas.user import UpdateUserRequest
from schemas.user import UpdateUserRequest
from db.mongodb import base_admin_users_collection 
from core.subscription_packages import SUBSCRIPTION_PACKAGES, COMMON_ADDONS



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
    
    async def update_user(
        self, user_id: ObjectId, updated_data: UpdateUserRequest
    ):
        collection = self.collection
        user_dict = jsonable_encoder(
            updated_data, exclude_unset=True, exclude_defaults=True, by_alias=True
        )
        await collection.update_one({"_id": user_id}, {"$set": user_dict})

    # async def update_user_subscription(self, user_id: ObjectId, package_name: str, interval: str):
    async def update_user_subscription(
        self, 
        user_id: ObjectId, 
        package_name: str, 
        interval: str
    ):
        package = next(
            (p for p in SUBSCRIPTION_PACKAGES 
            if p["name"].lower() == package_name.lower()),
            None
        )
        if not package:
            raise ValueError(f"Invalid package name: {package_name}")

        expiry_days = 365 if interval == "year" else 30
        expiry_date = datetime.now() + timedelta(days=expiry_days)
        new_expiry = int(expiry_date.timestamp())

        # Prepare base update
        update_data = {
            "subscription.current_package": package["name"],
            "subscription.expiry_date": new_expiry,
            "subscription.status": "active",
            "subscription.used_message": 0,
            "subscription.last_updated": datetime.now()
        }

        # Add all package features
        for feature, value in package["features"].items():
            update_data[f"subscription.{feature}"] = value

        # Handle Enterprise unlimited cases
        if package["name"] == "Enterprise":
            update_data["subscription.chatbot_limit"] = float('inf') 
            update_data["subscription.monthly_message_limit"] = float('inf')
            update_data["subscription.character_training_limit"] = float('inf')
    
        # MongoDB update operation
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data},
            upsert=True  # Creates subscription if doesn't exist
        )
        return True
    
    async def update_user_addons(
        self, 
        user_id: ObjectId, 
        addon_type: str  # "extra_chatbot" or "extra_messages"
    ):
        """
        Updates user's subscription with purchased add-ons
        Automatically determines user's current tier from their subscription
        
        Args:
            user_id: The user's MongoDB ObjectId
            addon_type: Type of add-on (must exist in COMMON_ADDONS)
        """
        # Validate addon type exists
        if addon_type not in COMMON_ADDONS:
            raise ValueError(f"Invalid addon type: {addon_type}. Must be one of: {list(COMMON_ADDONS.keys())}")

        # Get current user data with subscription info
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.get("subscription"):
            raise ValueError("User has no active subscription")
        
        current_tier = user["subscription"].get("current_package", "Free")
        
        # Prepare update operation
        quantity = COMMON_ADDONS[addon_type]["tier_quantities"].get(current_tier, 
            1 if addon_type == "extra_chatbot" else 500  # Default quantities
        )

        # Prepare update operation using proper MongoDB operators
        update_operation = {
            "$set": {
                "subscription.last_updated": datetime.now()
            },
            "$inc": {}
        }

        # Set the appropriate increment field
        if addon_type == "extra_chatbot":
            update_operation["$inc"]["subscription.extra_chatbots"] = quantity
        elif addon_type == "extra_messages":
            update_operation["$inc"]["subscription.monthly_message_limit"] = quantity

        await self.collection.update_one(
            {"_id": user_id},
            update_operation
        )