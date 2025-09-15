
import os
from dotenv import load_dotenv


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Please set OPENAI_API_KEY in environment before running")

VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "chroma").lower()
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "./chroma_db")