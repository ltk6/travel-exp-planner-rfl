import os
from dotenv import load_dotenv

# Load local .env relative to this file's root if present during development
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
load_dotenv(os.path.join(_root, ".env"))

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
LIGHT_EMBEDDING_MODEL_NAME = os.getenv("LIGHT_EMBEDDING_MODEL_NAME", "intfloat/multilingual-e5-small")

