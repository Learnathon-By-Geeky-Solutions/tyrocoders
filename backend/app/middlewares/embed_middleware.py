
from http import HTTPStatus
from bson import ObjectId
from fastapi import Depends, HTTPException, Request
from crud.user import UserCrud

user_crud = UserCrud()


async def embed_middleware(
    request: Request,
):
    user_id = request.headers.get("User-Id")
    if not user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="User-Id required in headers"
        )

    user = await user_crud.get_user_by_id(ObjectId(user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Unauthorized user"
        )

    user_id = user.get("_id")
    # subscription_status = await user_crud.get_subscription_status_by_user_id(
    #     user_id
    # )
    # if subscription_status != "paid":
    #     raise HTTPException(
    #         status_code=HTTPStatus.PAYMENT_REQUIRED, detail="Subscription required"
    #     )
    return user_id
