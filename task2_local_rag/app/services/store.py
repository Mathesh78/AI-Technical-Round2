"""Persistent local ChromaDB with application-controlled embeddings."""
import hashlib
import logging
import threading
from pathlib import Path

import chromadb
from app import config
from .chunking import chunk_text
from .documents import extract_pages
from .ollama import embeddings

logger = logging.getLogger(__name__)
_lock = threading.Lock()


def collection():
    config.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(config.CHROMA_DIR)).get_or_create_collection(
        name="documents", metadata={"hnsw:space": "cosine"})


def ingest(filename: str, raw: bytes) -> dict:
    """Stable content-hash doc ID; deduplicate repeated uploads."""
    name = Path(filename).name
    digest = hashlib.sha256(raw).hexdigest()[:20]
    doc_id = f"doc-{digest}"
    pages = extract_pages(name, raw)
    records = [(number, offset, text) for number, body in pages for offset, text in enumerate(chunk_text(body))]
    if not records:
        raise ValueError("No extractable text found; scanned PDFs need OCR")
    with _lock:
        coll = collection()
        existing = coll.get(where={"document_id": doc_id}, include=[])
        if existing["ids"]:
            return {"document_id": doc_id, "filename": name, "chunks": len(existing["ids"]), "duplicate": True}
        # Embed before storing, so failed Ollama calls do not insert partial documents.
        vectors = []
        for start in range(0, len(records), 16):
            vectors.extend(embeddings([r[2] for r in records[start:start + 16]]))
        ids = [f"{doc_id}-p{p}-c{n}" for p, n, _ in records]
        metadatas = [{"document_id": doc_id, "filename": name, "page": p, "chunk": n} for p, n, _ in records]
        for i in range(0, len(ids), 100):
            coll.add(ids=ids[i:i+100], documents=[r[2] for r in records[i:i+100]],
                     metadatas=metadatas[i:i+100], embeddings=vectors[i:i+100])
        logger.info("Indexed %s (%d chunks)", name, len(ids))
        return {"document_id": doc_id, "filename": name, "chunks": len(ids), "duplicate": False}


def retrieve(question: str, top_k: int = 5) -> list[dict]:
    coll = collection()
    if coll.count() == 0:
        return []
    vector = embeddings([question])[0]
    result = coll.query(query_embeddings=[vector], n_results=min(top_k, coll.count()),
                        include=["documents", "metadatas", "distances"])
    sources = []
    for i, (text, meta, distance) in enumerate(zip(result["documents"][0], result["metadatas"][0], result["distances"][0]), start=1):
        sources.append({"citation": f"[{i}]", "document_id": meta["document_id"], "filename": meta["filename"],
                        "page": meta["page"], "chunk": meta["chunk"], "score": round(1 - distance, 4), "text": text})
    return sources


def list_documents() -> list[dict]:
    meta = collection().get(include=["metadatas"])["metadatas"]
    unique = {}
    for item in meta:
        value = unique.setdefault(item["document_id"], {"document_id": item["document_id"], "filename": item["filename"], "chunks": 0})
        value["chunks"] += 1
    return list(unique.values())
