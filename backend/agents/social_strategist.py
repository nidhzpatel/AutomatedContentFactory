from crewai import Agent

from backend.llm.factory import get_llm

SOCIAL_STRATEGIST_ROLE = "Platform-Native Social Content Strategist"
SOCIAL_STRATEGIST_GOAL = (
    "Distill long-form technical articles into high-engagement, platform-native "
    "social content for LinkedIn and X/Twitter."
)
SOCIAL_STRATEGIST_BACKSTORY = (
    "A growth-minded content strategist who knows each platform's voice intimately: "
    "hook-driven storytelling and hashtags on X, professional takeaways with discussion "
    "prompts on LinkedIn. Never uses raw markdown in social copy."
)


def create_social_strategist_agent() -> Agent:
    """Build the CrewAI social strategist agent (LLM routed via the factory)."""
    return Agent(
        role=SOCIAL_STRATEGIST_ROLE,
        goal=SOCIAL_STRATEGIST_GOAL,
        backstory=SOCIAL_STRATEGIST_BACKSTORY,
        llm=get_llm("social_strategist"),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
