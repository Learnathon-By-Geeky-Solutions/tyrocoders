from datetime import datetime, timedelta
import jwt
from core.config import settings
from core.logger import logger


def create_access_token(user_id: str):
    to_encode = {
        "sub": user_id,
        "type": "access",  
        "exp": datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt, int(to_encode["exp"].timestamp())


def create_refresh_token(user_id: str):
    to_encode = {
        "sub": user_id,
        "type": "refresh", 
        "exp": datetime.now() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    }
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt, int(to_encode["exp"].timestamp())


def verify_token(token):
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


def create_pass_reset_token(user_email):
    to_encode = {"sub": user_email}
    expire = datetime.utcnow() + timedelta(
        minutes=settings.PASS_RESET_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
