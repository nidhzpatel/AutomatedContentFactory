from crewai import Agent

from backend.llm.factory import get_llm

CRITIC_ROLE = "Senior Editorial Critic"
CRITIC_GOAL = "Review content drafts for narrative flow, engagement, clarity, and structural balance."
CRITIC_BACKSTORY = (
    "A uncompromising editorial director with decades of publishing experience. "
    "Rigorously evaluates drafts against high publication standards and provides actionable feedback."
)


def create_critic_agent() -> Agent:
    """Build the CrewAI critic agent (LLM routed via the factory)."""
    return Agent(
        role=CRITIC_ROLE,
        goal=CRITIC_GOAL,
        backstory=CRITIC_BACKSTORY,
        llm=get_llm("critic"),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
