from fastapi import APIRouter, Depends
from schemas.user import UpdateUserRequest
from middlewares.auth_middleware import authenticate_token
from services.user_service import UserService

user_router = APIRouter()
user_service = UserService()



@user_router.get("/self")
async def get_self_users_details(user_id: dict = Depends(authenticate_token)):
    """
    Retrieve the details of the authenticated user.

    Args:
        user_id (dict): Authenticated user ID obtained from the token.

    Returns:
        JSONResponse: The authenticated user's details.
    """
    return await user_service.get_self_details(user_id)


@user_router.patch("/update")
async def update_self_users_details(
    user_details: UpdateUserRequest, user_id: dict = Depends(authenticate_token)
):
    """
    Update the details of the authenticated user.

    Args:
        user_details (UpdateUserRequest): The new user details to update.
        user_id (dict): Authenticated user ID obtained from the token.

    Returns:
        JSONResponse: Confirmation of user details update.
    """
    return await user_service.update_self_details(
        user_id, user_details
    )


@user_router.get("/dashboard-stats")
async def get_dashboard_stats(user_id: dict = Depends(authenticate_token)):
    """
    Retrieve dashboard statistics for the authenticated user.

    Args:
        user_id (dict): Authenticated user ID obtained from the token.

    Returns:
        JSONResponse: User's dashboard statistics, including metrics like usage, subscriptions, or performance.
    """
    return await user_service.get_dashboard_stats(user_id)