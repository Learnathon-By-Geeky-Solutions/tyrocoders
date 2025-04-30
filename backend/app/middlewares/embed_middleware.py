"""
User Authentication Middleware

This middleware checks if the request contains a valid `User-Id` header, retrieves the 
corresponding user from the database, and returns the user ID if the user is valid.
It is intended to be used as part of a FastAPI app to ensure that only authenticated users
can access certain endpoints.

Dependencies:
    - FastAPI
    - bson.ObjectId
    - crud.user (for user data access)

Key Components:
    - embed_middleware: Middleware function for authenticating users based on `User-Id` header.
"""

from http import HTTPStatus
from bson import ObjectId
from fastapi import Depends, HTTPException, Request
from crud.user import UserCrud

# Initialize User CRUD operations
user_crud = UserCrud()

async def embed_middleware(
    request: Request,
):
    """
    Middleware function to authenticate users by checking the `User-Id` header.

    This function attempts to retrieve the `User-Id` from the request headers, validates
    the user by checking if the ID exists in the database, and returns the user ID if valid.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        ObjectId: The authenticated user's MongoDB ObjectId.

    Raises:
        HTTPException: If the `User-Id` header is missing or the user does not exist in the database.
    """
    user_id = request.headers.get("User-Id")  # Extract User-Id from headers
    if not user_id:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="User-Id required in headers"
        )

    # Check if the user exists in the database
    user = await user_crud.get_user_by_id(ObjectId(user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Unauthorized user"
        )

    # Return the valid user ID
    user_id = user.get("_id")
    return user_id
