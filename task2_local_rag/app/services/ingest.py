"""Document chunking entry point for standalone ingestion workflows."""
from .chunking import chunk_text


def make_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 100):
    return chunk_text(text, size=chunk_size, overlap=chunk_overlap)
