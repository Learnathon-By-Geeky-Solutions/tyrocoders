import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()  

# Base directory for the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Data directory for storing raw files - updated to match your structure
DATA_DIR = os.path.join(BASE_DIR, "chatbot_data")
os.makedirs(DATA_DIR, exist_ok=True)

# Knowledge Base Storage directory for FAISS indexes and documents
BASE_KB_DIR = os.path.join(BASE_DIR, "kb_storage")
os.makedirs(BASE_KB_DIR, exist_ok=True)

# Supported file extensions for building KB indexes
SUPPORTED_EXTENSIONS = [".md", ".csv", ".xlsx"]

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

GEMINI_API_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Configuration loaded successfully.")