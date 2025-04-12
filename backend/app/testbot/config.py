import os
import logging
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Loading chatbot configuration without Together API integration...")

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

logger.info(f"Primary LLM: Gemini ({GEMINI_MODEL})")
logger.info(f"Secondary LLM: {FREE_LLM_PROVIDER}")
logger.info("Configuration loaded successfully.")
