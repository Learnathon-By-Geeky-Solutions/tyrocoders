"""
Configuration and environment setup for the chatbot backend.

- Loads environment variables from .env file if not already set.
- Defines supported file extensions for chatbot knowledge base.
- Sets project and API configurations using Pydantic's BaseSettings.
- Constructs derived directories for storing data and knowledge base.
- Configures external APIs such as Gemini and free LLM providers (e.g., HuggingFace, Ollama).
- Includes a custom FastAPI validation error handler.
"""
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from schemas.response import ValidationErrorResponse

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables if not already loaded
if os.getenv("PROJECT_TITLE") is None:
    load_dotenv()

# Supported file extensions for knowledge base uploads
SUPPORTED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx", ".csv", ".json", ".xlsx"]

class Settings(BaseSettings):
    """
    Loads environment-based configuration using Pydantic's BaseSettings.
    All values can be overridden via a `.env` file.
    """

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
    GROQ_API_KEY: str | None = None  # Optional: Not all deployments use Groq

    # --- MongoDB Configuration ---
    MONGO_URI: str
    MONGO_DB: str

    # --- Free LLM Provider Settings ---
    FREE_LLM_PROVIDER: str = "huggingface"  # Default to HuggingFace
    HUGGINGFACE_API_KEY: str | None = None  # Optional API key for HuggingFace
    FRONTEND_URL: str = "http://localhost:5173"

    # --- Payment Gateway ---
    STRIPE_SECRET_KEY: str | None = None  # Optional Stripe integration

    class Config:
        env_file = ".env"  # Automatically load values from .env file


# Initialize settings from environment
settings = Settings()

# Directory paths derived from current file location
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "chatbot_data")
BASE_KB_DIR = os.path.join(BASE_DIR, "kb_storage")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BASE_KB_DIR, exist_ok=True)

# GEMINI API Configuration
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
)

# Define configuration for supported free/alternative LLM providers
FREE_LLM_OPTIONS = {
    "huggingface": {
        "api_url": "https://api-inference.huggingface.co/models/google/flan-t5-large",
        "api_key_env": settings.HUGGINGFACE_API_KEY,
    },
    "ollama": {
        "api_url": "http://localhost:11434/api/generate",
        "api_key_env": None,  # Ollama typically runs locally without an API key
    },
}

# Load selected free LLM configuration based on environment setting
FREE_LLM_CONFIG = FREE_LLM_OPTIONS.get(
    settings.FREE_LLM_PROVIDER, FREE_LLM_OPTIONS["huggingface"]
)
FREE_LLM_API_URL = FREE_LLM_CONFIG["api_url"]
FREE_LLM_API_KEY = FREE_LLM_CONFIG.get("api_key_env", None)

# Debug log (can be removed or replaced with logging)
print("PROJECT_TITLE:", settings.PROJECT_TITLE)

# Custom validation error handler for FastAPI to standardize validation responses
async def validation_exception_handler(exc: RequestValidationError):
    """
    Formats FastAPI validation errors into a unified JSON structure.
    
    Args:
        exc (RequestValidationError): The validation exception raised by FastAPI.

    Returns:
        JSONResponse: A custom formatted error response.
    """
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
