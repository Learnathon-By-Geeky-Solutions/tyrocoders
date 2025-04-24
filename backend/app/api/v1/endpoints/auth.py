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


@auth_router.post("/signup")
async def register(
    user_data: UserCreate,
):
    return await auth_service.register(
        user_data
    )


@auth_router.post("/login")
async def login(
    user_login: UserLogin
):
    return await auth_service.login(
        user_login
    )


@auth_router.post("/renew-access-token")
async def renew_access_token(
    refresh_token_request: RefreshTokenRequest, 
):
    return await auth_service.renew_access_token(
        refresh_token_request.refresh_token
    )


@auth_router.post("/generate-pass-reset")
async def generate_pass_reset_token(
    generate_reset_password: GenerateResetPassword,
    background_tasks: BackgroundTasks,
):
    return await auth_service.generate_pass_reset_token(
        generate_reset_password, background_tasks, 
    )


@auth_router.post("/reset-password")
async def check_password_reset_token_and_reset_password(
    reset_password: ResetPassword, 
):
    return await auth_service.check_password_reset_token_and_reset_password(
        reset_password, 
    )
