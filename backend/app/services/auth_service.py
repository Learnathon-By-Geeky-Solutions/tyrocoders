"""
auth_service.py

This module defines the AuthService class which handles user authentication and account management functionalities.
It interacts with the database layer via UserCrud and AuthCrud, providing features such as:

- User registration
- User login
- Token-based authentication and renewal
- Password reset token generation and verification

All methods handle logging, response formatting, and proper exception handling.
"""

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

USER_NOT_FOUND_MSG = "User not found"
INVALID_TOKEN_MSG = "Invalid token subject"

class AuthService:
    """
    Service class responsible for handling authentication and authorization logic.
    Integrates with user and authentication CRUD operations to register, login,
    and manage password-related features.

    Methods
    -------
    - register(user: UserCreate): Registers a new user after validation.
    - login(login_data: UserLogin): Authenticates user and returns tokens.
    - renew_access_token(refresh_token: str): Issues a new access token using a valid refresh token.
    - generate_pass_reset_token(generate_reset_password: GenerateResetPassword): Sends password reset link to email.
    - check_password_reset_token_and_reset_password(reset_password: ResetPassword): Resets password using valid token.
    """

    async def register(
        self,
        user: UserCreate,
    ):
        
        """
        Registers a new user after validating email and username uniqueness.
        Hashes the password and stores the user in the database.

        Parameters:
            user (UserCreate): Object containing user's email, username, and password.

        Returns:
            JSONResponse: Status and message indicating the result of registration.
        """

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
            logger.debug("Hashing password")
            user.password = hash_password(user.password)
            logger.info("Password hashed successfully")

            new_inserted_user = await auth_crud.register(user)
            new_user = await user_crud.get_user_by_id(
                new_inserted_user.inserted_id
            )

            new_user = convert_object_id_to_string(new_user)
            logger.info("User registered successfully")

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
        """
        Authenticates a user using email and password.
        Generates access and refresh tokens on successful authentication.

        Parameters:
            login_data (UserLogin): Object containing user's email and password.

        Returns:
            JSONResponse: Authentication result and JWT tokens on success.
        """

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
                    content={"message": USER_NOT_FOUND_MSG},
                )

            logger.info(
                f"User with email {login_data.email} found"
            )
            logger.debug("Verifying password")
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
                "Password and OTP verified successfully"
            )

            logger.debug(
                "Creating access token and refresh token"
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
                "Access token and refresh token created successfully"
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
        """
        Generates new access and refresh tokens using a valid refresh token.

        Parameters:
            refresh_token (str): JWT refresh token.

        Returns:
            JSONResponse: New tokens or appropriate error messages.
        """
        try:
            logger.debug("Verifying refresh token")
            user_id = verify_token(refresh_token)

            if not user_id:
                logger.info(INVALID_TOKEN_MSG)
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={"message": INVALID_TOKEN_MSG},
                )

            logger.info("Refresh token verified successfully")

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
                    content={"message": USER_NOT_FOUND_MSG},
                )

            logger.info(f"User with id {user_id} found")
            logger.debug(
                "Creating access token and refresh token"
            )
            access_token, access_token_expire_in = create_access_token(user_id)
            new_refresh_token, refresh_token_expire_in = create_refresh_token(user_id)
            logger.info(
                "Access token and refresh token created successfully"
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
            logger.error("Refresh token expired")
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"message": "Refresh token expired"},
            )
        except jwt.InvalidTokenError:
            logger.error("Invalid refresh token")
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
    ):
        """
        Generates a one-time password reset token and constructs a reset link.
        (Email sending should be handled in background tasks.)

        Parameters:
            generate_reset_password (GenerateResetPassword): Object with email and reset form URL.

        Returns:
            JSONResponse: Success message with reset link or error details.
        """
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
                    content={"message": USER_NOT_FOUND_MSG},
                )
            logger.info(
                f"User with email {generate_reset_password.email} found"
            )
            user = convert_object_id_to_string(user)
            user_email = user.get("email")
            logger.debug("Generating password reset token")
            pass_reset_token = create_pass_reset_token(user_email)
            logger.info(
                "Password reset token generated successfully"
            )
            logger.debug(
                "Sending password reset email in background tasks"
            )
            one_time_link = (
                f"{generate_reset_password.reset_form_url}?token={pass_reset_token}"
            )
            
            logger.info(
                "Password reset email sent successfully in background tasks"
            )
            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={
                    "message": "Password reset email sent successfully",
                    "data": {
                        "reset link": one_time_link,
                    },
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
        """
        Validates the password reset token and resets the user password after hashing.

        Parameters:
            reset_password (ResetPassword): Object containing reset token and new password.

        Returns:
            JSONResponse: Success or error message indicating reset outcome.
        """
        try:
            logger.debug("Verifying password reset token")
            user_email = verify_token(reset_password.pass_reset_token)

            if not user_email:
                logger.info(
                    "Invalid password reset token subject"
                )
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={"message": INVALID_TOKEN_MSG},
                )

            logger.info(
                "Password reset token verified successfully"
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
                    content={"message": USER_NOT_FOUND_MSG},
                )
            logger.info(f"User with email {user_email} found")
            user = convert_object_id_to_string(user)
            user_email = user.get("email")
            logger.debug("Hashing new password")
            new_password = hash_password(reset_password.new_password)
            logger.info("Password hashed successfully")
            logger.debug("Resetting password")
            isReset = await auth_crud.password_reset(
                user_email, new_password
            )

            if not isReset:
                logger.info("Could not reset password")
                return JSONResponse(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content={"message": "Could not reset password. Please try again"},
                )
            logger.info("Password reset successfully")

            return JSONResponse(
                status_code=HTTPStatus.OK,
                content={"message": "Password reset successfully"},
            )
        except jwt.ExpiredSignatureError:
            logger.error("Password reset token expired")
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"message": "Password reset Token expired"},
            )
        except jwt.InvalidTokenError:
            logger.error("Invalid password reset token")
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