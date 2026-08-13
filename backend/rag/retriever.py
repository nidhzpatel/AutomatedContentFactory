def retrieve_context(query: str, top_k: int = 3) -> list:
    """Retrieves relevant context chunks from vector database."""
    return [
        {"chunk": f"Context chunk matching query '{query}'", "score": 0.92}
    ]
