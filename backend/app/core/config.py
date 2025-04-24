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



# Base project directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Data and Knowledge Base directories
DATA_DIR = os.path.join(BASE_DIR, "chatbot_data")
BASE_KB_DIR = os.path.join(BASE_DIR, "kb_storage")  # Ensure consistent naming
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BASE_KB_DIR, exist_ok=True)

# Supported file extensions
SUPPORTED_EXTENSIONS = [".txt", ".md", ".pdf", ".docx", ".csv", ".json", ".xlsx"]

# GROQ API Settings
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# GEMINI API Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# You can swap in another Gemini model name if desired
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

# Free/alternative LLM settings (Together API has been removed)
FREE_LLM_OPTIONS = {
    "huggingface": {
        "api_url": "https://api-inference.huggingface.co/models/google/flan-t5-large",
        "api_key_env": "HUGGINGFACE_API_KEY"
    },
    "ollama": {
        "api_url": "http://localhost:11434/api/generate",  # Local Ollama instance
        "api_key_env": None  # Ollama typically doesn't require an API key for local usage
    }
}

# Read free LLM provider from environment or default to HuggingFace
FREE_LLM_PROVIDER = os.getenv("FREE_LLM_PROVIDER", "huggingface")
FREE_LLM_CONFIG = FREE_LLM_OPTIONS.get(FREE_LLM_PROVIDER, FREE_LLM_OPTIONS["huggingface"])
FREE_LLM_API_URL = FREE_LLM_CONFIG["api_url"]
FREE_LLM_API_KEY = os.getenv(FREE_LLM_CONFIG["api_key_env"], "") if FREE_LLM_CONFIG["api_key_env"] else None

class Settings(BaseSettings):
    BASE_URL: str
    PROJECT_TITLE: str
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    PASS_RESET_TOKEN_EXPIRE_MINUTES: int
    ASSEMBLYAI_API_KEY: str

    # IS_RELOAD: bool

    MONGO_URI: str
    MONGO_DB: str
    
    class Config:
        env_file = ".env"

settings = Settings()
print("PROJECT_TITLE_AFTERWARDS:", settings.PROJECT_TITLE)


async def validation_exception_handler(exc: RequestValidationError):
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