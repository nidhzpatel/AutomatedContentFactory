"""Real Tavily web search — tool for the CrewAI researcher agent.

Requires TAVILY_API_KEY in .env; without it the agent simply runs without
web search (parametric knowledge only).
"""

from typing import List, Optional

from backend.config import settings
from backend.observability.logger import get_logger

logger = get_logger("tools.tavily_search")


def create_tavily_search_tool() -> Optional["object"]:
    """Build a CrewAI-compatible Tavily search tool, or None if unconfigured."""
    if not settings.TAVILY_API_KEY:
        logger.info("TAVILY_API_KEY not set; researcher agent runs without web search")
        return None
    from crewai_tools import TavilySearchTool

    return TavilySearchTool(api_key=settings.TAVILY_API_KEY)


def tavily_search_tool(query: str) -> List[dict]:
    """Direct Tavily search for non-agent callers; [] when unconfigured or on error."""
    if not settings.TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY not set; search skipped")
        return []
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        response = client.search(query=query, max_results=5)
        return response.get("results", [])
    except Exception as e:
        logger.error(f"Tavily search failed: {e}")
        return []
