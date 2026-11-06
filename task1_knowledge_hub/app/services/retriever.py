"""Small retrieval facade to keep ingestion and querying separate."""

def retrieve_top_k(question: str, k: int = 3):
    if not question.strip():
        return []
    from .vector import search
    return search(question, k=k)
