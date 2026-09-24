from crewai import Agent

from backend.llm.factory import get_llm

FACT_CHECKER_ROLE = "Verification & Hallucination Auditor"
FACT_CHECKER_GOAL = "Cross-examine every statistic, claim, and reference link against authoritative ground truth."
FACT_CHECKER_BACKSTORY = (
    "An obsessive technical fact-checker specializing in auditing AI outputs for hallucinated claims, "
    "fake citations, or unverified technical assertions."
)


def create_fact_checker_agent() -> Agent:
    """Build the CrewAI fact-checker agent (LLM routed via the factory)."""
    return Agent(
        role=FACT_CHECKER_ROLE,
        goal=FACT_CHECKER_GOAL,
        backstory=FACT_CHECKER_BACKSTORY,
        llm=get_llm("fact_checker"),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
