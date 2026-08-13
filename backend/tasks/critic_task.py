def create_critic_task():
    """Returns the task for content critique."""
    return {
        "description": "Critique the provided draft for structure, argument quality, tone, and readability.",
        "expected_output": "Constructive critique with numerical scores and actionable improvement suggestions.",
    }
