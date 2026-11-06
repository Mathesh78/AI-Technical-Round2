"""Configuration shared by the API, ingestion, and local Ollama client."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("RAG_DATA_DIR", str(BASE_DIR / "data")))
CHROMA_DIR = DATA_DIR / "chroma"
UPLOAD_DIR = DATA_DIR / "uploads"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_LLM = os.getenv("OLLAMA_LLM", "llama3.2:latest")
OLLAMA_EMBED = os.getenv("OLLAMA_EMBED", "nomic-embed-text")
MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_QUESTION_CHARS = 2000
