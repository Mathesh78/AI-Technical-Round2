"""Ollama HTTP endpoints using on-device models."""
import httpx
from app import config


class OllamaUnavailable(RuntimeError):
    pass


def embeddings(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    try:
        with httpx.Client(timeout=180) as client:
            response = client.post(f"{config.OLLAMA_URL}/api/embed", json={"model": config.OLLAMA_EMBED, "input": texts})
            response.raise_for_status()
            vectors = response.json()["embeddings"]
            if len(vectors) != len(texts):
                raise OllamaUnavailable("Ollama returned the wrong number of embeddings")
            return vectors
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise OllamaUnavailable(f"Ollama embeddings unavailable: {exc}") from exc


def answer(prompt: str) -> str:
    try:
        with httpx.Client(timeout=180) as client:
            response = client.post(f"{config.OLLAMA_URL}/api/generate", json={"model": config.OLLAMA_LLM,
                  "prompt": prompt, "stream": False, "options": {"temperature": 0}})
            response.raise_for_status()
            return response.json()["response"].strip()
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise OllamaUnavailable(f"Ollama generation unavailable: {exc}") from exc
