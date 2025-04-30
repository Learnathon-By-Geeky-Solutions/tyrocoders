from fastapi import APIRouter, BackgroundTasks, Depends, Path
from typing import Optional
from services.auth_service import AuthService
from schemas.auth import (
    GenerateResetPassword,
    RefreshTokenRequest,
    ResetPassword,
    UserCreate,
    UserLogin,
)

auth_router = APIRouter()
auth_service = AuthService()


auth_router = APIRouter()
auth_service = AuthService()


@auth_router.post("/signup")
async def register(
    user_data: UserCreate,
):
    """
    Register a new user.

    Args:
        user_data (UserCreate): User registration data including email, password, etc.

    Returns:
        JSONResponse: A success message with user info or error details.
    """
    return await auth_service.register(
        user_data
    )


@auth_router.post("/login")
async def login(
    user_login: UserLogin
):
    """
    Authenticate a user and return access and refresh tokens.

    Args:
        user_login (UserLogin): User credentials (email and password).

    Returns:
        JSONResponse: A token pair (access, refresh) if successful, or error message.
    """
    return await auth_service.login(
        user_login
    )


@auth_router.post("/renew-access-token")
async def renew_access_token(
    refresh_token_request: RefreshTokenRequest, 
):
    """
    Renew an expired access token using a valid refresh token.

    Args:
        refresh_token_request (RefreshTokenRequest): Contains the refresh token.

    Returns:
        JSONResponse: New access token or error message if the token is invalid/expired.
    """
    return await auth_service.renew_access_token(
        refresh_token_request.refresh_token
    )


@auth_router.post("/generate-pass-reset")
async def generate_pass_reset_token(
    generate_reset_password: GenerateResetPassword,
    background_tasks: BackgroundTasks,
):
    """
    Initiate the password reset process by generating a reset token.

    Args:
        generate_reset_password (GenerateResetPassword): Contains user email.
        background_tasks (BackgroundTasks): FastAPI background task manager.

    Returns:
        JSONResponse: Confirmation message if the reset token was sent.
    """
    return await auth_service.generate_pass_reset_token(
        generate_reset_password, background_tasks, 
    )


@auth_router.post("/reset-password")
async def check_password_reset_token_and_reset_password(
    reset_password: ResetPassword, 
):
    """
    Verify the password reset token and update the user's password.

    Args:
        reset_password (ResetPassword): Contains reset token and new password.

    Returns:
        JSONResponse: Success message if password reset is successful, or error details.
    """
    return await auth_service.check_password_reset_token_and_reset_password(
        reset_password, 
    )
