from crewai import Task

from backend.agents.researcher import create_researcher_agent


def create_research_task(topic: str) -> Task:
    """Task for the researcher agent: produce a structured research brief."""
    return Task(
        description=(
            f"Gather detailed research analysis and findings for '{topic}'. "
            "Provide key findings, technical background, and reputable source links."
        ),
        expected_output=(
            "A research brief in EXACTLY this format:\n"
            "SUMMARY: <2-3 paragraph overview>\n"
            "KEY FINDINGS:\n"
            "- <finding>\n"
            "- <finding>\n"
            "SOURCES:\n"
            "- <Title> | <URL>\n"
            "- <Title> | <URL>"
        ),
        agent=create_researcher_agent(),
    )
