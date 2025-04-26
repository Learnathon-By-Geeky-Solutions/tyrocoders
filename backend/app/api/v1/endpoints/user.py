from fastapi import APIRouter, Depends
from schemas.user import UpdateUserRequest
from middlewares.auth_middleware import authenticate_token
from services.user_service import UserService

user_router = APIRouter()
user_service = UserService()



@user_router.get("/self")
async def get_self_users_details(user_id: dict = Depends(authenticate_token)):
    return await user_service.get_self_details(user_id)


@user_router.patch("/update")
async def update_self_users_details(
    user_details: UpdateUserRequest, user_id: dict = Depends(authenticate_token)
):
    return await user_service.update_self_details(
        user_id, user_details
    )


@user_router.get("/dashboard-stats")
async def get_dashboard_stats(user_id: dict = Depends(authenticate_token)):
    return await user_service.get_dashboard_stats(user_id)