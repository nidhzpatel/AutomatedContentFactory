"""CrewAI task factories for social-format generation (the former stub, now real)."""

from crewai import Task

from backend.agents.social_strategist import create_social_strategist_agent

_NO_MARKDOWN = "IMPORTANT: Do NOT use raw markdown headers like ### or **. Use clean plain text."


def create_linkedin_task(topic: str) -> Task:
    return Task(
        description=(
            f"Write a high-converting, professional LinkedIn post about '{topic}'.\n"
            f"Include hook, bulleted takeaways, discussion question, and 3-5 hashtags.\n{_NO_MARKDOWN}"
        ),
        expected_output="A ready-to-post LinkedIn update in plain text.",
        agent=create_social_strategist_agent(),
    )


def create_x_task(topic: str) -> Task:
    return Task(
        description=(
            f"Write a punchy X/Twitter post or thread about '{topic}'.\n"
            f"Include opening line, 2-3 numbered key takeaways, and hashtags.\n{_NO_MARKDOWN}"
        ),
        expected_output="A ready-to-post X/Twitter update or short thread in plain text.",
        agent=create_social_strategist_agent(),
    )


def create_overview_task(topic: str) -> Task:
    return Task(
        description=(
            f"Write a detailed technical reference overview and deep dive on '{topic}'.\n"
            "Include Technical Definition, System Architecture, Core Safeguards, and Reference Links [Title](URL)."
        ),
        expected_output="A markdown deep-dive overview with reference links.",
        agent=create_social_strategist_agent(),
    )
