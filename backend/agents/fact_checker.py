from typing import Dict, Any


class FactCheckerAgent:
    """Fact-Checker Agent responsible for verifying claims, calculating trust scores, and detecting hallucinations."""

    def __init__(self):
        self.role = "Verification & Hallucination Auditor"
        self.goal = "Cross-examine every statistic, claim, and reference link against authoritative ground truth."
        self.backstory = (
            "An obsessive technical fact-checker specializing in auditing AI outputs for hallucinated claims, "
            "fake citations, or unverified technical assertions."
        )

    def get_agent_config(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "verbose": True,
            "allow_delegation": False,
        }


def create_fact_checker_agent() -> Dict[str, Any]:
    return FactCheckerAgent().get_agent_config()
