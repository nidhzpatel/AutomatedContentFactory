from typing import Tuple


def check_hallucination(generated_text: str, context_sources: list) -> Tuple[float, float, bool]:
    """
    Calculates Hallucination Rate and Fact-Check Trust Score.
    Returns: (hallucination_rate, fact_check_score, passed)
    """
    if not generated_text:
        return 1.0, 0.0, False

    # Check for ungrounded extreme claims or bogus citations
    flagged_phrases = ["1000% proven", "fake source", "guaranteed 100x return"]
    lowered = generated_text.lower()
    
    matches = sum(1 for phrase in flagged_phrases if phrase in lowered)
    
    # Calculate score metrics
    hallucination_rate = round(min(1.0, matches * 0.25), 2)
    fact_check_score = round(max(0.0, 1.0 - hallucination_rate), 2)
    
    passed = hallucination_rate <= 0.1 and fact_check_score >= 0.85
    return hallucination_rate, fact_check_score, passed
