# config.py
import os

# Base directory for the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Directory to store sample data files
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Directory to store the saved KB indexes and document lists
KB_STORAGE_DIR = os.path.join(BASE_DIR, "kb_storage")
os.makedirs(KB_STORAGE_DIR, exist_ok=True)

# Gemini API configuration (replace with your valid API key)
GEMINI_API_KEY = "AIzaSyA369Ut5Cyl13bNVzuQZzzIPG_PDBBPhTU"  # Replace with your Gemini API key
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
