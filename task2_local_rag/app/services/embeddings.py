"""Shared local embedding interface. Uses Ollama nomic-embed-text."""
from app import config


def model_name() -> str:
    return config.OLLAMA_EMBED if hasattr(config, "OLLAMA_EMBED") else config.EMBED
