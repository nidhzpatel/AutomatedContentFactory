from fastapi.testclient import TestClient

from backend.main import app


def test_ingest_endpoint(monkeypatch):
    monkeypatch.setattr(
        "backend.api.routes.ingest_document",
        lambda text, source="": {"source": source, "status": "ingested", "chunks": 3},
    )
    client = TestClient(app)
    response = client.post("/api/ingest", json={"text": "Some knowledge.", "source": "doc-1"})
    assert response.status_code == 200
    assert response.json() == {"source": "doc-1", "status": "ingested", "chunks": 3}


def test_ingest_endpoint_rejects_empty_text(monkeypatch):
    monkeypatch.setattr(
        "backend.api.routes.ingest_document",
        lambda text, source="": {"source": source, "status": "ingested", "chunks": 1},
    )
    client = TestClient(app)
    response = client.post("/api/ingest", json={"text": "   "})
    assert response.status_code == 400
