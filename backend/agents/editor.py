from crewai import Agent

from backend.llm.factory import get_llm

EDITOR_ROLE = "Executive Revision Editor"
EDITOR_GOAL = "Refine, polish, and revise drafts based on critic feedback and factual audit reports."
EDITOR_BACKSTORY = (
    "A precise line editor who excels at rewriting text to fix factual errors, "
    "improve readability, and eliminate hallucinated statements while maintaining voice."
)


def create_editor_agent() -> Agent:
    """Build the CrewAI editor agent (LLM routed via the factory)."""
    return Agent(
        role=EDITOR_ROLE,
        goal=EDITOR_GOAL,
        backstory=EDITOR_BACKSTORY,
        llm=get_llm("editor"),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
