from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from schemas.response import ValidationErrorResponse

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load .env if not already loaded
if os.getenv("PROJECT_TITLE") is None:
    load_dotenv()

# Supported file extensions
SUPPORTED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx", ".csv", ".json", ".xlsx"]

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_TITLE: str
    BASE_URL: str

    # --- JWT Settings ---
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    PASS_RESET_TOKEN_EXPIRE_MINUTES: int

    # --- External APIs ---
    GEMINI_API_KEY: str
    ASSEMBLYAI_API_KEY: str
    GROQ_API_KEY: str | None = None

    # --- MongoDB ---
    MONGO_URI: str
    MONGO_DB: str

    # --- Free LLM Provider Config ---
    FREE_LLM_PROVIDER: str = "huggingface"
    HUGGINGFACE_API_KEY: str | None = None  # Optional for HuggingFace
    FRONTEND_URL: str = "http://localhost:5173"

    STRIPE_SECRET_KEY: str | None = None

    class Config:
        env_file = ".env"

settings = Settings()

# Derived Directories
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "chatbot_data")
BASE_KB_DIR = os.path.join(BASE_DIR, "kb_storage")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BASE_KB_DIR, exist_ok=True)

# GEMINI API Configuration
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
)

# Free/alternative LLM settings
FREE_LLM_OPTIONS = {
    "huggingface": {
        "api_url": "https://api-inference.huggingface.co/models/google/flan-t5-large",
        "api_key_env": settings.HUGGINGFACE_API_KEY,
    },
    "ollama": {
        "api_url": "http://localhost:11434/api/generate",
        "api_key_env": None,
    },
}

FREE_LLM_CONFIG = FREE_LLM_OPTIONS.get(
    settings.FREE_LLM_PROVIDER, FREE_LLM_OPTIONS["huggingface"]
)
FREE_LLM_API_URL = FREE_LLM_CONFIG["api_url"]
FREE_LLM_API_KEY = FREE_LLM_CONFIG.get("api_key_env", None)

# Debug Print (can remove in production)
print("PROJECT_TITLE:", settings.PROJECT_TITLE)

# FastAPI Custom Validation Error Handler
async def validation_exception_handler(exc: RequestValidationError):
    errors = exc.errors()
    custom_errors = [
        {
            "field": error["loc"][-1],
            "message": error["msg"],
        }
        for error in errors
    ]
    error_response = ValidationErrorResponse(
        message="Payload Validation failed", errors=custom_errors
    )
    return JSONResponse(status_code=422, content=error_response.dict())
