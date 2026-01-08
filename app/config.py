import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
DEBUG = os.getenv("DEBUG", "False") == "True"

# API
API_TITLE = "ConsumeSafe"
API_DESCRIPTION = "Check if products are boycotted and find Tunisian alternatives"
API_VERSION = "1.0.0"

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# CORS
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

# Rate limiting
RATE_LIMIT_ENABLED = True
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_PERIOD = 3600  # 1 hour
