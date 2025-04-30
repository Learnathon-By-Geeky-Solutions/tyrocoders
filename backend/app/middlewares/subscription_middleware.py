"""
Subscription Check Module

This module provides functionality to check if a user has an active subscription 
before granting access to certain resources. The `check_subscription` function
is used to verify if the authenticated user has an active subscription and raises
an appropriate HTTPException if the user is not subscribed.

Dependencies:
    - FastAPI
    - bson.ObjectId
    - middlewares.auth_middleware (for token authentication)
    - crud.user (for checking user subscription status)
"""

from http import HTTPStatus
from bson import ObjectId
from fastapi import Depends, HTTPException
from middlewares.auth_middleware import authenticate_token
from crud.user import UserCrud

# Initialize User CRUD operations
user_crud = UserCrud()

async def check_subscription(user_id: ObjectId = Depends(authenticate_token)):
    """
    Dependency function to check if the authenticated user has an active subscription.

    This function uses the `authenticate_token` dependency to verify the user's identity.
    It then checks the user's subscription status in the database. If the subscription is
    not active, it raises an HTTPException with a 402 status code.

    Args:
        user_id (ObjectId): The authenticated user's MongoDB ObjectId, provided by the 
            `authenticate_token` dependency.

    Returns:
        ObjectId: The authenticated user's MongoDB ObjectId if the subscription is active.

    Raises:
        HTTPException: If the user does not have an active subscription, or an error occurs
            while fetching the subscription status.
    """
    try:
        # Check the user's subscription status
        subscription_status = await user_crud.get_subscription_status_by_user_id(user_id)
        if subscription_status != "active":
            raise HTTPException(
                status_code=HTTPStatus.PAYMENT_REQUIRED, detail="Subscription required"
            )
    except Exception as e:
        # If an error occurs, raise HTTPException with a 402 status code
        raise HTTPException(
            status_code=HTTPStatus.PAYMENT_REQUIRED, detail="Subscription required"
        ) from e

    # Return the user_id if subscription is active
    return user_id
