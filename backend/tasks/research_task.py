def create_research_task(topic: str):
    """Returns the task for research generation."""
    return {
        "description": f"Gather research data and key findings for topic: '{topic}'",
        "expected_output": "Structured research summary with verified sources and key takeaways.",
    }
