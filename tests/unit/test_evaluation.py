from evaluation.run_evaluation import run_benchmark


def test_synthetic_benchmark_returns_results():
    results = run_benchmark(live=False)
    assert len(results) == 2
    for entry in results:
        assert "word_count" in entry
        assert "relevance_score" in entry
        assert "latency_ms" in entry


def test_live_benchmark_uses_pipeline(monkeypatch):
    canned = {
        "status": "completed",
        "blog_post": {
            "title": "Live Title",
            "content": "Quantum computing leverages superposition and entanglement for generative AI healthcare scalability.",
        },
    }

    async def fake_execute(self):
        return canned

    monkeypatch.setattr("evaluation.run_evaluation.MainContentFlow.execute", fake_execute)
    results = run_benchmark(live=True)
    assert len(results) == 2
    assert results[0]["word_count"] == len(canned["blog_post"]["content"].split())
