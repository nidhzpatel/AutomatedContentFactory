def export_article_to_markdown(title: str, body: str) -> str:
    """Formats article into Markdown export standard."""
    return f"# {title}\n\n{body}\n"
