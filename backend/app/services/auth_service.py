from fastapi import BackgroundTasks
from fastapi.responses import JSONResponse
from utils.hashing import hash_password, verify_password
from crud.user import UserCrud
from core.logger import logger
from utils.converter import convert_object_id_to_string
from datetime import datetime, timedelta
from core.config import settings
from typing import Optional
from urllib.parse import urlencode
from http import HTTPStatus
from schemas import UserCreate, UserLogin
from crud.auth import AuthCrud
from core.security import (
    create_access_token,
    create_pass_reset_token,
    create_refresh_token,
    verify_token,
)
from bson import ObjectId
import jwt, secrets
from schemas.auth import (
    GenerateResetPassword,
    ResetPassword,
    UserCreate,
    UserLogin,
)

user_crud = UserCrud()
auth_crud = AuthCrud()

class  AuthService:
    
    async def register(
        self,
        user: UserCreate,
    ):
        try:
            logger.debug(
                f"Checking if user with email {user.email} exists or not"
            )
            existing_user_by_email = await user_crud.get_user_by_email(
                user.email
            )
            if existing_user_by_email:
                logger.info(
                    f"User with email {user.email} already exists"
                )
                return JSONResponse(
                    status_code=HTTPStatus.CONFLICT,
                    content={"message": f"User with email {user.email} already exists"},
                )
            logger.info(
                f"User with email {user.email} does not exist"
            )
            logger.debug(
                f"Checking if user with username {user.username} exists or not"
            )
            existing_user_by_username = await user_crud.get_user_by_username(
                user.username
            )
            if existing_user_by_username:
                logger.info(
                    f"User with username {user.username} already exists"
                )
                return JSONResponse(
                    status_code=HTTPStatus.CONFLICT,
                    content={
                        "message": f"User with username {user.username} already exists"
                    },
                )
            logger.info(
                f"User with username {user.username} does not exist"
            )
            logger.debug(f"Hashing password")
            user.password = hash_password(user.password)
            logger.info(f"Password hashed successfully")

            new_inserted_user = await auth_crud.register(user)
            new_user = await user_crud.get_user_by_id(
                new_inserted_user.inserted_id
            )

            new_user = convert_object_id_to_string(new_user)
            logger.info(f"User registered successfully")

            return JSONResponse(
                status_code=HTTPStatus.CREATED,
                content={
                    "message": "User created successfully",
                    "data": new_user,
                },
            )
        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
        
    async def login(self, login_data: UserLogin):
        try:
            logger.debug(
                f"Login attempt for user with email {login_data.email}"
            )
            user = await user_crud.get_user_by_email(login_data.email)
            if not user:
                logger.info(
                    f"User with email {login_data.email} not found"
                )
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )

            logger.info(
                f"User with email {login_data.email} found"
            )
            logger.debug(f"Verifying password")
            if not verify_password(login_data.password, user.get("password")):
                return JSONResponse(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    content={"message": "Invalid password"},
                )
            # if not user.get('is_verified', False):
            if "is_verified" in user and not user["is_verified"]:
                return JSONResponse(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    content={"message": "Account not verified with OTP code"},
                )

            logger.info(
                f"Password and OTP verified successfully"
            )

            logger.debug(
                f"Creating access token and refresh token"
            )
            user = convert_object_id_to_string(user)
            user_id = user.get("_id")
            access_token, access_token_expire_in = create_access_token(user_id)
            refresh_token, refresh_token_expire_in = create_refresh_token(user_id)

            if not access_token:
                return JSONResponse(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content={
                        "message": "Could not create access token. Please try again"
                    },
                )

            if not refresh_token:
                return JSONResponse(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content={
                        "message": "Could not create access token. Please try again"
                    },
                )
            logger.info(
                f"Access token and refresh token created successfully"
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Login successful",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": "bearer",
                        "aceess_token_expire_in": access_token_expire_in,
                        "refresh_token_expire_in": refresh_token_expire_in,
                    },
                },
            )
        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )
        
    async def renew_access_token(self, refresh_token: str):
        try:
            logger.debug(f"Verifying refresh token")
            user_id = verify_token(refresh_token)

            if not user_id:
                logger.info(f"Invalid token subject")
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={"message": "Invalid token subject"},
                )

            logger.info(f"Refresh token verified successfully")

            logger.debug(
                f"Checking if user with id {user_id} exists or not"
            )

            user = await user_crud.get_user_by_id(ObjectId(user_id))

            if user is None:
                logger.info(
                    f"User with id {user_id} not found"
                )
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )

            logger.info(f"User with id {user_id} found")
            logger.debug(
                f"Creating access token and refresh token"
            )
            access_token, access_token_expire_in = create_access_token(user_id)
            new_refresh_token, refresh_token_expire_in = create_refresh_token(user_id)
            logger.info(
                f"Access token and refresh token created successfully"
            )

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Access token refreshed successfully",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": new_refresh_token,
                        "token_type": "bearer",
                        "aceess_token_expire_in": access_token_expire_in,
                        "refresh_token_expire_in": refresh_token_expire_in,
                    },
                },
            )

        except jwt.ExpiredSignatureError:
            logger.error(f"Refresh token expired")
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"message": "Refresh token expired"},
            )
        except jwt.InvalidTokenError:
            logger.error(f"Invalid refresh token")
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"message": "Invalid refresh token"},
            )
        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )

    async def generate_pass_reset_token(
        self,
        generate_reset_password: GenerateResetPassword,
        background_tasks: BackgroundTasks
    ):
        try:
            logger.debug(
                f"Checking if user with email {generate_reset_password.email} exists or not"
            )
            user = await user_crud.get_user_by_email(
                generate_reset_password.email
            )

            if not user:
                logger.info(
                    f"User with email {generate_reset_password.email} not found"
                )
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
            logger.info(
                f"User with email {generate_reset_password.email} found"
            )
            user = convert_object_id_to_string(user)
            user_email = user.get("email")
            user_name = user.get("username")
            logger.debug(f"Generating password reset token")
            pass_reset_token = create_pass_reset_token(user_email)
            logger.info(
                f"Password reset token generated successfully"
            )
            logger.debug(
                f"Sending password reset email in background tasks"
            )
            one_time_link = (
                f"{generate_reset_password.reset_form_url}?token={pass_reset_token}"
            )
            # background_tasks.add_task(
            #     send_password_reset_email, user_name, user_email, one_time_link
            # )
            logger.info(
                f"Password reset email sent successfully in background tasks"
            )
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Password reset email sent successfully",
                },
            )

        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )

    async def check_password_reset_token_and_reset_password(
        self, reset_password: ResetPassword
    ):
        try:
            logger.debug(f"Verifying password reset token")
            user_email = verify_token(reset_password.pass_reset_token)

            if not user_email:
                logger.info(
                    f"Invalid password reset token subject"
                )
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={"message": "Invalid token subject"},
                )

            logger.info(
                f"Password reset token verified successfully"
            )
            logger.debug(
                f"Checking if user with email {user_email} exists or not"
            )
            user = await user_crud.get_user_by_email(user_email)
            if not user:
                logger.info(
                    f"User with email {user_email} not found"
                )
                return JSONResponse(
                    status_code=HTTPStatus.NOT_FOUND,
                    content={"message": "User not found"},
                )
            logger.info(f"User with email {user_email} found")
            user = convert_object_id_to_string(user)
            user_email = user.get("email")
            logger.debug(f"Hashing new password")
            new_password = hash_password(reset_password.new_password)
            logger.info(f"Password hashed successfully")
            logger.debug(f"Resetting password")
            isReset = await auth_crud.password_reset(
                user_email, new_password
            )

            if not isReset:
                logger.info(f"Could not reset password")
                return JSONResponse(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content={"message": "Could not reset password. Please try again"},
                )
            logger.info(f"Password reset successfully")

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={"message": "Password reset successfully"},
            )
        except jwt.ExpiredSignatureError:
            logger.error(f"Password reset token expired")
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"message": "Password reset Token expired"},
            )
        except jwt.InvalidTokenError:
            logger.error(f"Invalid password reset token")
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"message": "Invalid password reset token"},
            )
        except Exception as e:
            logger.error(f"Internal server error. ERROR: {e}")
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content={"message": f"Internal server error. ERROR: {e}"},
            )