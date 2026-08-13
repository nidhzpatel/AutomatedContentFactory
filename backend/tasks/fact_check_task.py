def create_fact_check_task():
    """Returns the task for fact checking."""
    return {
        "description": "Cross-check all statistics and claims in the article against authoritative sources.",
        "expected_output": "Fact-check verification report with trust rating.",
    }
