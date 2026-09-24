from backend.config import settings
from backend.tools.tavily_search import create_tavily_search_tool, tavily_search_tool


def test_no_key_returns_no_tool(monkeypatch):
    monkeypatch.setattr(settings, "TAVILY_API_KEY", "")
    assert create_tavily_search_tool() is None
    assert tavily_search_tool("query") == []


def test_with_key_builds_tool(monkeypatch):
    monkeypatch.setattr(settings, "TAVILY_API_KEY", "tvly-test-key")
    tool = create_tavily_search_tool()
    assert tool is not None
    assert tool.name == "Tavily Search"
