"""Document ingestion: chunk, embed, and store in the local vector DB."""

import uuid

from backend.rag.embedder import embed_documents
from backend.rag.store import get_collection
from backend.observability.logger import get_logger

logger = get_logger("rag.ingestion")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list:
    """Split text into overlapping character-window chunks."""
    text = text.strip()
    if not text:
        return []
    chunks = []
    step = max(1, chunk_size - overlap)
    for start in range(0, len(text), step):
        chunk = text[start:start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        if start + chunk_size >= len(text):
            break
    return chunks


def ingest_document(text: str, source: str = "") -> dict:
    """Chunk and embed a document into the knowledge collection.

    Blocking (network + vector DB) — call via asyncio.to_thread from async code.
    """
    chunks = chunk_text(text)
    if not chunks:
        return {"source": source, "status": "empty", "chunks": 0}

    embeddings = embed_documents(chunks)
    collection = get_collection()
    ids = [str(uuid.uuid4()) for _ in chunks]
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=[{"source": source} for _ in chunks],
    )
    logger.info(f"Ingested {len(chunks)} chunks (source: {source or 'unknown'})")
    return {"source": source, "status": "ingested", "chunks": len(chunks)}
