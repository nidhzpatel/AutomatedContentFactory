from typing import Dict, Any


class CriticAgent:
    """Critic Agent responsible for evaluating drafts for clarity, engagement, and structural integrity."""

    def __init__(self):
        self.role = "Senior Editorial Critic"
        self.goal = "Review content drafts for narrative flow, engagement, clarity, and structural balance."
        self.backstory = (
            "A uncompromising editorial director with decades of publishing experience. "
            "Rigorously evaluates drafts against high publication standards and provides actionable feedback."
        )

    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": True,
            "allow_delegation": False,
        }


def create_critic_agent() -> Dict[str, Any]:
    return CriticAgent().get_agent_config()
