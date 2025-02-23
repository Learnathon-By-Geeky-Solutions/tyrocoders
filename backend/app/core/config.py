from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from schemas.response import ValidationErrorResponse
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

print("PROJECT_TITLE:", os.getenv("PROJECT_TITLE"))

if os.getenv("PROJECT_TITLE") is None:
    print("calling load_dotenv()")
    load_dotenv()


class Settings(BaseSettings):
    BASE_URL: str
    PROJECT_TITLE: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    PASS_RESET_TOKEN_EXPIRE_MINUTES: int

    # IS_RELOAD: bool

    MONGO_URI: str
    MONGO_DB: str
    
    class Config:
        env_file = ".env"

settings = Settings()
print("PROJECT_TITLE_AFTERWARDS:", settings.PROJECT_TITLE)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    custom_errors = [
        {
            "field": error["loc"][-1],
            "message": error["msg"],  # The actual error message
        }
        for error in errors
    ]
    error_response = ValidationErrorResponse(
        message="Payload Validation failed", errors=custom_errors
    )
    return JSONResponse(status_code=422, content=error_response.dict())