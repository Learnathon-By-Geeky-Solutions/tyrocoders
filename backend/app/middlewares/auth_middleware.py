"""
Token Authentication Module

This module provides functionality for authenticating users via JWT bearer tokens
using FastAPI's dependency injection system. It is intended for use in routes that
require protected access based on verified user identity.

Dependencies:
    - FastAPI
    - PyJWT (jwt)
    - HTTPStatus
    - bson.ObjectId
    - core.security (for token verification)
    - crud.user (for user data access)

Key Components:
    - HTTPBearer: FastAPI security scheme for handling `Authorization: Bearer` tokens
    - authenticate_token: Dependency function to verify and authenticate incoming JWT tokens
"""

from http import HTTPStatus
from bson import ObjectId
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from fastapi import Depends, HTTPException
from core.security import verify_token
from crud.user import UserCrud

# Initialize User CRUD operations
user_crud = UserCrud()

# HTTPBearer instance to prompt Swagger UI for Authorization header
security = HTTPBearer()

async def authenticate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Dependency function to authenticate a JWT bearer token.

    Extracts the token from the `Authorization` header, verifies its validity,
    retrieves the associated user from the database, and returns the user ID.

    Args:
        credentials (HTTPAuthorizationCredentials): Automatically extracted
            by FastAPI from the Authorization header.

    Returns:
        ObjectId: The authenticated user's MongoDB ObjectId.

    Raises:
        HTTPException: If the token is expired, invalid, or the user does not exist.
    """
    token = credentials.credentials  # Extract Bearer token

    try:
        # Verify and decode token to get user ID
        user_id = verify_token(token)
        if not user_id:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Invalid token subject"
            )

        # Fetch the user from the database
        user = await user_crud.get_user_by_id(ObjectId(user_id))
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Unauthorized user"
            )

        # Return user ID if all checks pass
        return user.get("_id")

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid Token"
        )
