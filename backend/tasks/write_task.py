from crewai import Task

from backend.agents.writer import create_writer_agent


def create_write_task(topic: str, research_summary: str) -> Task:
    """Task for the writer agent: draft the article from the research brief."""
    return Task(
        description=(
            f"Write a complete, highly detailed technical article about '{topic}' "
            f"using this research brief:\n{research_summary}\n"
            "Include Title, Introduction, Detailed Sections, and Conclusion."
        ),
        expected_output=(
            "The full article in Markdown. The first line must be the title as a markdown "
            "header (e.g. # My Title), followed by the article body."
        ),
        agent=create_writer_agent(),
    )
