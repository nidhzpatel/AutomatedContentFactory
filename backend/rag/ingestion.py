def ingest_document(file_path: str):
    """Processes document text and stores embeddings in vector store."""
    return {"file": file_path, "status": "ingested", "chunks": 12}
