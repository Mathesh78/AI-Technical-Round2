"""Recreate FAISS file from SQLite after changing Ollama embedding model."""
from app.services.storage import initialize
from app.services.vector import rebuild
if __name__=='__main__':
    initialize()
    print(f'Rebuilt index with {rebuild()} chunks')
