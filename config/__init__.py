import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# ====================== PROJECT SETUP ======================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load .env file
load_dotenv(
    dotenv_path=os.path.join(PROJECT_ROOT, ".env"),
    encoding="utf-8-sig",
    override=True
)

# ====================== API KEYS ======================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")

# ====================== DATABASE ======================
PG_URI = os.getenv("PG_URI")

# ====================== LOGGING ======================
LOG_DATEFMT = "%H:%M:%S"
LOG_LEVEL = logging.INFO

class DynamicFormatter(logging.Formatter):
    DETAILED_FORMAT = "%(asctime)s [%(levelname)s] %(name)s [%(filename)s:%(lineno)d]: %(message)s"
    SIMPLE_FORMAT = "[%(levelname)s] %(name)s: %(message)s"

    def __init__(self, datefmt=None):
        super().__init__(datefmt=datefmt)
        self.detailed_formatter = logging.Formatter(self.DETAILED_FORMAT, datefmt=datefmt)
        self.simple_formatter = logging.Formatter(self.SIMPLE_FORMAT, datefmt=datefmt)

    def format(self, record):
        if record.name.startswith("N18"):
            return self.detailed_formatter.format(record)
        return self.simple_formatter.format(record)


def setup_logging(name: str = __name__) -> logging.Logger:
    """Khởi tạo logging theo chuẩn dự án."""
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        formatter = DynamicFormatter(datefmt=LOG_DATEFMT)
        handler.setFormatter(formatter)
        root.addHandler(handler)
        root.setLevel(LOG_LEVEL)
    return logging.getLogger(name)