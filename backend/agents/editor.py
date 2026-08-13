from typing import Dict, Any


class EditorAgent:
    """Editor Agent responsible for refining content based on critique and revision feedback."""

    def __init__(self):
        self.role = "Executive Revision Editor"
        self.goal = "Refine, polish, and revise drafts based on critic feedback and factual audit reports."
        self.backstory = (
            "A precise line editor who excels at rewriting text to fix factual errors, "
            "improve readability, and eliminate hallucinated statements while maintaining voice."
        )

    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": True,
            "allow_delegation": False,
        }


def create_editor_agent() -> Dict[str, Any]:
    return EditorAgent().get_agent_config()
