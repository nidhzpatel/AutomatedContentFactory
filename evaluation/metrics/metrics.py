def calculate_readability_score(text: str) -> float:
    """Calculates Flesch-Kincaid style readability proxy score."""
    words = text.split()
    if not words:
        return 0.0
    avg_len = sum(len(w) for w in words) / len(words)
    return round(max(0.0, min(100.0, 100.0 - (avg_len * 10))), 2)


def calculate_relevance_score(text: str, expected_keywords: list) -> float:
    """Calculates percentage of expected keywords found in text."""
    if not expected_keywords:
        return 1.0
    text_lower = text.lower()
    matches = sum(1 for kw in expected_keywords if kw.lower() in text_lower)
    return round(matches / len(expected_keywords), 2)


def evaluate_content_metrics(text: str, latency_ms: float = 0.0, expected_keywords: list = None) -> dict:
    """Evaluates comprehensive content generation metrics."""
    word_count = len(text.split())
    readability = calculate_readability_score(text)
    relevance = calculate_relevance_score(text, expected_keywords or [])
    
    # Calculate hallucination rate & fact check score
    flagged = sum(1 for phrase in ["unverified claim", "1000% safe"] if phrase in text.lower())
    hallucination_rate = round(min(1.0, flagged * 0.2), 2)
    fact_check_score = round(max(0.0, 1.0 - hallucination_rate), 2)

    return {
        "word_count": word_count,
        "readability_score": readability,
        "relevance_score": relevance,
        "fact_check_score": fact_check_score,
        "hallucination_rate": hallucination_rate,
        "latency_ms": latency_ms,
    }
