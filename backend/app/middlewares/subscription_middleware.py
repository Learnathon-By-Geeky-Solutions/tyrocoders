from http import HTTPStatus
from bson import ObjectId
from fastapi import Depends, HTTPException
from middlewares.auth_middleware import authenticate_token
from crud.user import UserCrud

user_crud = UserCrud()

# Function to check subscription
async def check_subscription(user_id: ObjectId = Depends(authenticate_token)):
    try:
        subscription_status = await user_crud.get_subscription_status_by_user_id(
            user_id
        )
        if subscription_status != "active":
            raise HTTPException(
                status_code=HTTPStatus.PAYMENT_REQUIRED, detail="Subscription required"
            )
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.PAYMENT_REQUIRED, detail="Subscription required"
        ) from e

    return user_id