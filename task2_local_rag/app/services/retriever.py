"""Small retrieval facade to keep ingestion and querying separate."""

def retrieve_top_k(question: str, k: int = 3):
    if not question.strip():
        return []
    from .store import retrieve
    return retrieve(question, top_k=k)
