from typing import Dict, Any


class ResearcherAgent:
    """Researcher Agent responsible for gathering verified data and RAG context."""

    def __init__(self):
        self.role = "Senior Technical Research Analyst"
        self.goal = "Gather up-to-date, empirical research data, statistics, and domain context."
        self.backstory = (
            "A seasoned research analyst specializing in AI, cloud architecture, and cybersecurity. "
            "Expert in extracting high-confidence facts from authoritative technical documents and search engines."
        )

    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": True,
            "allow_delegation": False,
        }


def create_researcher_agent() -> Dict[str, Any]:
    return ResearcherAgent().get_agent_config()
