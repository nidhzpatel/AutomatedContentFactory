"""Shared chromadb store for the RAG layer."""

import chromadb

from backend.config import settings

_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def get_collection():
    return get_client().get_or_create_collection("acf_knowledge")
