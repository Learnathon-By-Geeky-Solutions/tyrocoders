from datetime import datetime, timedelta
from bson import ObjectId
from fastapi.encoders import jsonable_encoder
from schemas.user import UpdateUserRequest
from db.mongodb import base_admin_users_collection 
from core.subscription_packages import SUBSCRIPTION_PACKAGES, COMMON_ADDONS

class UserCrud:
    """
    A CRUD utility class for managing user data and subscriptions in MongoDB.
    """

    def __init__(self):
        """
        Initialize the UserCrud with the user collection.
        """
        self.collection = base_admin_users_collection

    async def get_all_users(self):
        """
        Retrieve all users from the collection.

        Returns:
            List[dict]: A list of user documents.
        """
        users = []
        async for user in self.collection.find():
            users.append(user)
        return users

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by email.

        Args:
            email (str): User's email.

        Returns:
            dict | None: User document or None if not found.
        """
        return await self.collection.find_one({"email": email})

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by username.

        Args:
            username (str): User's username.

        Returns:
            dict | None: User document or None if not found.
        """
        return await self.collection.find_one({"username": username})

    async def get_user_by_id(self, user_id: ObjectId):
        """
        Retrieve a user by ObjectId.

        Args:
            user_id (ObjectId): MongoDB ObjectId of the user.

        Returns:
            dict | None: User document or None if not found.
        """
        return await self.collection.find_one({"_id": user_id})
    
    async def update_user(self, user_id: ObjectId, updated_data: UpdateUserRequest):
        """
        Update user details.

        Args:
            user_id (ObjectId): MongoDB ObjectId of the user.
            updated_data (UpdateUserRequest): New user data to update.
        """
        user_dict = jsonable_encoder(
            updated_data, exclude_unset=True, exclude_defaults=True, by_alias=True
        )
        await self.collection.update_one({"_id": user_id}, {"$set": user_dict})

    async def update_user_subscription(self, user_id: ObjectId, package_name: str, interval: str):
        """
        Update or assign a subscription package to a user.

        Args:
            user_id (ObjectId): MongoDB ObjectId of the user.
            package_name (str): Subscription package name (e.g., "Basic", "Pro", "Enterprise").
            interval (str): Duration of subscription ("month" or "year").

        Returns:
            bool: True if update successful, else raises exception.
        
        Raises:
            ValueError: If the subscription package name is invalid.
        """
        package = next(
            (p for p in SUBSCRIPTION_PACKAGES if p["name"].lower() == package_name.lower()),
            None
        )
        if not package:
            raise ValueError(f"Invalid package name: {package_name}")

        expiry_days = 365 if interval == "year" else 30
        expiry_date = datetime.now() + timedelta(days=expiry_days)
        new_expiry = int(expiry_date.timestamp())

        update_data = {
            "subscription.current_package": package["name"],
            "subscription.expiry_date": new_expiry,
            "subscription.status": "active",
            "subscription.used_message": 0,
            "subscription.last_updated": datetime.now()
        }

        for feature, value in package["features"].items():
            update_data[f"subscription.{feature}"] = value

        if package["name"] == "Enterprise":
            update_data["subscription.chatbot_limit"] = float('inf')
            update_data["subscription.monthly_message_limit"] = float('inf')
            update_data["subscription.character_training_limit"] = float('inf')

        await self.collection.update_one(
            {"_id": user_id},
            {"$set": update_data},
            upsert=True
        )
        return True

    async def update_user_addons(self, user_id: ObjectId, addon_type: str):
        """
        Apply an add-on (extra chatbots or extra messages) to a user's subscription.

        Args:
            user_id (ObjectId): MongoDB ObjectId of the user.
            addon_type (str): Add-on type. Must be one of the keys in COMMON_ADDONS.

        Raises:
            ValueError: If the user or subscription is not found, or the addon_type is invalid.
        """
        if addon_type not in COMMON_ADDONS:
            raise ValueError(f"Invalid addon type: {addon_type}. Must be one of: {list(COMMON_ADDONS.keys())}")

        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not user.get("subscription"):
            raise ValueError("User has no active subscription")
        
        current_tier = user["subscription"].get("current_package", "Free")

        quantity = COMMON_ADDONS[addon_type]["tier_quantities"].get(
            current_tier, 
            1 if addon_type == "extra_chatbot" else 500
        )

        update_operation = {
            "$set": {
                "subscription.last_updated": datetime.now()
            },
            "$inc": {}
        }

        if addon_type == "extra_chatbot":
            update_operation["$inc"]["subscription.extra_chatbots"] = quantity
        elif addon_type == "extra_messages":
            update_operation["$inc"]["subscription.monthly_message_limit"] = quantity

        await self.collection.update_one(
            {"_id": user_id},
            update_operation
        )
