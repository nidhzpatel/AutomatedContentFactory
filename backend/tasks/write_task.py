def create_write_task(topic: str):
    """Returns the task for content writing."""
    return {
        "description": f"Write an initial draft article for topic: '{topic}'",
        "expected_output": "Comprehensive article draft formatted with clear sections and headings.",
    }
