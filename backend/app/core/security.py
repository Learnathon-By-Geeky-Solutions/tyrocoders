"""
JWT Utility Module

This module handles creation and verification of different JWT tokens used across the system:
- Access tokens
- Refresh tokens
- Password reset tokens

Functions:
- create_access_token(user_id)
- create_refresh_token(user_id)
- verify_token(token)
- create_pass_reset_token(user_email)
"""

from datetime import datetime, timedelta, timezone
import jwt
from core.config import settings
from core.logger import logger


def create_access_token(user_id: str):
    """
    Create a JWT access token for the given user ID.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        tuple: Encoded JWT token (str) and its expiration timestamp (int).
    """
    to_encode = {
        "sub": user_id,
        "type": "access",  # Token type identifier
        "exp": datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt, int(to_encode["exp"].timestamp())


def create_refresh_token(user_id: str):
    """
    Create a JWT refresh token for the given user ID.

    Args:
        user_id (str): The unique identifier of the user.

    Returns:
        tuple: Encoded JWT token (str) and its expiration timestamp (int).
    """
    to_encode = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt, int(to_encode["exp"].timestamp())


def verify_token(token: str):
    """
    Verify the validity of a JWT token and return the subject (user_id or email).

    Args:
        token (str): The JWT token to verify.

    Returns:
        str: The subject ("sub") from the token payload if valid.

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is malformed or invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    except jwt.ExpiredSignatureError as e:
        logger.error("Token has expired")
        raise e
    except jwt.InvalidTokenError as e:
        logger.error("Token is invalid")
        raise e


def create_pass_reset_token(user_email: str):
    """
    Create a password reset JWT token using the user's email as the subject.

    Args:
        user_email (str): Email of the user requesting a password reset.

    Returns:
        str: Encoded JWT token with an expiration timestamp.
    """
    to_encode = {"sub": user_email}

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASS_RESET_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
