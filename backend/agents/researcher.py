from crewai import Agent

from backend.llm.factory import get_llm
from backend.tools.tavily_search import create_tavily_search_tool

RESEARCHER_ROLE = "Senior Technical Research Analyst"
RESEARCHER_GOAL = "Gather up-to-date, empirical research data, statistics, and domain context."
RESEARCHER_BACKSTORY = (
    "A seasoned research analyst specializing in AI, cloud architecture, and cybersecurity. "
    "Expert in extracting high-confidence facts from authoritative technical documents and search engines."
)


def create_researcher_agent() -> Agent:
    """Build the CrewAI researcher agent (LLM routed via the factory).

    Attaches real Tavily web search when TAVILY_API_KEY is configured;
    otherwise the agent works from its own knowledge plus RAG grounding.
    """
    search_tool = create_tavily_search_tool()
    return Agent(
        role=RESEARCHER_ROLE,
        goal=RESEARCHER_GOAL,
        backstory=RESEARCHER_BACKSTORY,
        llm=get_llm("researcher"),
        tools=[search_tool] if search_tool else [],
        verbose=True,
        allow_delegation=False,
        memory=False,
    )
