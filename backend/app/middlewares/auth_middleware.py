from http import HTTPStatus
from bson import ObjectId
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from fastapi import Depends, HTTPException
from core.security import verify_token
from crud.user import UserCrud

user_crud = UserCrud()


# FastAPI's HTTPBearer for swagger UI to show the Authorization header
security = HTTPBearer()


# Function to decode and authenticate token
async def authenticate_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials  # Extract Bearer token

    try:
        user_id = verify_token(token)
        if not user_id:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token subject"
            )

        user = await user_crud.get_user_by_id(ObjectId(user_id))
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Unauthorized user"
            )

        user_id = user.get("_id")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid Token")