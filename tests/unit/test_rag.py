import chromadb
import pytest

from backend.rag.ingestion import chunk_text, ingest_document
from backend.rag.retriever import retrieve_context

FAKE_VECTOR = [0.1, 0.2, 0.3, 0.4]


@pytest.fixture
def memory_store(monkeypatch):
    collection = chromadb.Client().get_or_create_collection("test_knowledge")
    monkeypatch.setattr("backend.rag.ingestion.get_collection", lambda: collection)
    monkeypatch.setattr("backend.rag.store.get_collection", lambda: collection)
    monkeypatch.setattr(
        "backend.rag.ingestion.embed_documents",
        lambda texts: [FAKE_VECTOR for _ in texts],
    )
    monkeypatch.setattr(
        "backend.rag.embedder.get_embedding",
        lambda text: FAKE_VECTOR,
    )
    return collection


def test_chunk_text_short_input_single_chunk():
    assert chunk_text("Short text.") == ["Short text."]


def test_chunk_text_empty():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_chunk_text_long_input_multiple_overlapping_chunks():
    text = "word " * 400  # ~2000 chars
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) > 2
    assert all(len(c) <= 500 for c in chunks)


def test_ingest_and_retrieve_roundtrip(memory_store):
    result = ingest_document("Solar panels convert sunlight into electricity via the photovoltaic effect.", source="energy-doc")
    assert result["status"] == "ingested"
    assert result["chunks"] >= 1

    contexts = retrieve_context("how do solar panels work", top_k=2)
    assert len(contexts) >= 1
    assert contexts[0]["source"] == "energy-doc"
    assert "photovoltaic" in contexts[0]["text"]


def test_ingest_empty_text(memory_store):
    result = ingest_document("   ", source="nothing")
    assert result == {"source": "nothing", "status": "empty", "chunks": 0}


def test_retrieve_context_fails_soft(memory_store, monkeypatch):
    def boom(text):
        raise RuntimeError("ollama down")

    monkeypatch.setattr("backend.rag.embedder.get_embedding", boom)
    assert retrieve_context("any query") == []


def test_retrieve_context_empty_query(memory_store):
    assert retrieve_context("   ") == []
