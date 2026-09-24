from crewai import Agent

from backend.llm.factory import get_llm

WRITER_ROLE = "Lead Technical Content Strategist & Writer"
WRITER_GOAL = "Synthesize research data into structured, engaging, and high-impact article drafts."
WRITER_BACKSTORY = (
    "A master wordsmith and technical communicator skilled at translating complex concepts "
    "into clear, well-structured Markdown articles tailored for professional audiences."
)


def create_writer_agent() -> Agent:
    """Build the CrewAI writer agent (LLM routed via the factory)."""
    return Agent(
        role=WRITER_ROLE,
        goal=WRITER_GOAL,
        backstory=WRITER_BACKSTORY,
        llm=get_llm("writer"),
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
