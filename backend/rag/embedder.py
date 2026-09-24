"""Embeddings via the local Ollama /api/embed endpoint."""

from typing import List

import httpx

from backend.config import settings


def _embed_url() -> str:
    return f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/embed"


def get_embedding(text: str) -> List[float]:
    """Embed a single text. Raises on failure (callers decide how to degrade)."""
    response = httpx.post(
        _embed_url(),
        json={"model": settings.OLLAMA_EMBED_MODEL, "input": text},
        timeout=60.0,
    )
    response.raise_for_status()
    return response.json()["embeddings"][0]


def embed_documents(texts: List[str]) -> List[List[float]]:
    """Embed a batch of texts in one request."""
    response = httpx.post(
        _embed_url(),
        json={"model": settings.OLLAMA_EMBED_MODEL, "input": texts},
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()["embeddings"]
