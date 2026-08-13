from typing import Dict, Any


class WriterAgent:
    """Writer Agent responsible for generating initial article drafts from research."""

    def __init__(self):
        self.role = "Lead Technical Content Strategist & Writer"
        self.goal = "Synthesize research data into structured, engaging, and high-impact article drafts."
        self.backstory = (
            "A master wordsmith and technical communicator skilled at translating complex concepts "
            "into clear, well-structured Markdown articles tailored for professional audiences."
        )

    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": True,
            "allow_delegation": False,
        }


def create_writer_agent() -> Dict[str, Any]:
    return WriterAgent().get_agent_config()
