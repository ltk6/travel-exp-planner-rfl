"""
N18 Orchestrator — Local Config
Contains n18-specific constants and server configuration.
General config (logging, API keys, DB) is imported directly from the global `config` module.
"""

import os
from dotenv import load_dotenv

# Load local .env relative to this file's root if present during development
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(_root, ".env"))

# ====================== RECOMMENDATION SETTINGS ======================
TOP_K_LOCATIONS = int(os.getenv("TOP_K_LOCATIONS", "5"))
TOP_K_ACTIVITIES = int(os.getenv("TOP_K_ACTIVITIES", "5"))

# ====================== API SERVER (N18) ======================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_DEBUG = os.getenv("API_DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8501,http://localhost:8502,http://127.0.0.1:8501,http://127.0.0.1:8502"
).split(",")

PROTECTED_ROUTES: set[str] = {"/locations", "/activities", "/explore"}

# ====================== EXTERNAL MICROSERVICES ======================
N1_SERVICE_URL = os.getenv("N1_SERVICE_URL", "http://127.0.0.1:8001")

