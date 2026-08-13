def tavily_search_tool(query: str) -> list:
    """Executes search query using Tavily API."""
    return [
        {"title": f"Search Result for {query}", "url": "https://example.com", "snippet": "Relevant article snippet..."}
    ]
