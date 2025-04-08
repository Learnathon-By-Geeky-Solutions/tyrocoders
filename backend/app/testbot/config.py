import os
from dotenv import load_dotenv

load_dotenv()  # Loads environment variables from .env

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

KB_STORAGE_DIR = os.path.join(BASE_DIR, "kb_storage")
os.makedirs(KB_STORAGE_DIR, exist_ok=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
