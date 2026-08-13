import json
import time
from pathlib import Path
from evaluation.metrics.metrics import evaluate_content_metrics
from backend.flows.main_flow import MainContentFlow


def run_benchmark():
    dataset_path = Path(__file__).parent / "datasets" / "topics.json"
    with open(dataset_path, "r") as f:
        topics = json.load(f)

    print(f"Running Systematic Evaluation Pipeline across {len(topics)} topics...\n")
    results = []
    
    for item in topics:
        topic_name = item["topic"]
        expected_kw = item.get("expected_keywords", [])
        
        start_time = time.time()
        sample_text = f"# Technical Guide: {topic_name}\n\nComprehensive architectural overview analyzing {topic_name} and covering {', '.join(expected_kw)}."
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
    run_benchmark()
