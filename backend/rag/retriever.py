"""Context retrieval over the local knowledge collection.

Deliberately fails soft: any error logs a warning and returns [] so callers
can continue ungrounded rather than erroring.
"""

from typing import List

from backend.observability.logger import get_logger

logger = get_logger("rag.retriever")


def retrieve_context(query: str, top_k: int = 3) -> List[dict]:
    """Return the top-k knowledge chunks for a query as {text, source, distance} dicts."""
    if not query or not query.strip():
        return []
    try:
        from backend.rag.embedder import get_embedding
        from backend.rag.store import get_collection

        embedding = get_embedding(query.strip())
        result = get_collection().query(query_embeddings=[embedding], n_results=top_k)

        contexts = []
        for doc, metadata, distance in zip(
            result["documents"][0],
            result["metadatas"][0],
            result["distances"][0],
        ):
            contexts.append({
                "text": doc,
                "source": (metadata or {}).get("source", ""),
                "distance": distance,
            })
        return contexts
    except Exception as e:
        logger.warning(f"RAG retrieval failed ({e}); continuing without grounding")
        return []
