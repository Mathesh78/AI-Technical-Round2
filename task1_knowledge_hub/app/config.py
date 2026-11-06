"""Application configuration; paths stay relative to this project."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("HUB_DATA_DIR", str(ROOT / "data")))
DB = DATA / "harvest.sqlite3"
INDEX = DATA / "vectors.faiss"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
LLM = os.getenv("OLLAMA_LLM", "llama3.2:1b")
EMBED = os.getenv("OLLAMA_EMBED", "nomic-embed-text")
MAX_FILE = 2 * 1024 * 1024
MAX_URLS = 30
MAX_HTML = 4 * 1024 * 1024
