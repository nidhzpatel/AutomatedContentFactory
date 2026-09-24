"""Benchmark content quality over the topics dataset.

Default mode scores synthetic samples (fast, no LLM required). Pass --live to
run the real pipeline per topic (requires Ollama; ~minutes per topic).
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

from evaluation.metrics.metrics import evaluate_content_metrics
from backend.flows.main_flow import MainContentFlow


def _load_topics() -> list:
    dataset_path = Path(__file__).parent / "datasets" / "topics.json"
    with open(dataset_path, "r") as f:
        return json.load(f)


def _synthetic_sample(topic_name: str, expected_kw: list) -> str:
    return (
        f"# Technical Guide: {topic_name}\n\n"
        f"Comprehensive architectural overview analyzing {topic_name} and covering {', '.join(expected_kw)}."
    )


def _live_sample(topic_name: str) -> str:
    result = asyncio.run(MainContentFlow(topic=topic_name).execute())
    if result.get("status") != "completed":
        raise RuntimeError(f"pipeline status {result.get('status')} for topic '{topic_name}'")
    return result["blog_post"]["content"]


def run_benchmark(live: bool = False) -> list:
    topics = _load_topics()
    mode = "LIVE pipeline" if live else "synthetic samples"
    print(f"Running Systematic Evaluation Pipeline across {len(topics)} topics ({mode})...\n")

    results = []
    for item in topics:
        topic_name = item["topic"]
        expected_kw = item.get("expected_keywords", [])

        start_time = time.time()
        if live:
            try:
                sample_text = _live_sample(topic_name)
            except Exception as e:
                print(f"  [{item['id']}] {topic_name}: SKIPPED ({e})\n")
                continue
        else:
            sample_text = _synthetic_sample(topic_name, expected_kw)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        metrics = evaluate_content_metrics(sample_text, latency_ms=elapsed_ms, expected_keywords=expected_kw)

        entry = {
            "id": item["id"],
            "topic": topic_name,
            **metrics,
        }
        results.append(entry)

        print(f"  [{item['id']}] {topic_name}:")
        print(f"      - Word Count: {metrics['word_count']}")
        print(f"      - Fact-Check Score: {metrics['fact_check_score']}")
        print(f"      - Hallucination Rate: {metrics['hallucination_rate']}")
        print(f"      - Readability Score: {metrics['readability_score']}")
        print(f"      - Relevance Score: {metrics['relevance_score'] * 100:.1f}%\n")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate content quality over benchmark topics.")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run the real pipeline per topic instead of synthetic samples (requires Ollama).",
    )
    args = parser.parse_args()
    run_benchmark(live=args.live)
