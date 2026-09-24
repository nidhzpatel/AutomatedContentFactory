from crewai import Task

from backend.agents.researcher import create_researcher_agent
from backend.rag.retriever import retrieve_context


def create_research_task(topic: str) -> Task:
    """Task for the researcher agent: produce a structured research brief.

    Prepends grounding from the local RAG knowledge base when available.
    """
    grounding = retrieve_context(topic, top_k=2)
    grounding_block = ""
    if grounding:
        snippets = "\n".join(f"- {c['text']}" for c in grounding)
        grounding_block = f"Relevant internal knowledge (use as grounding):\n{snippets}\n\n"

    return Task(
        description=(
            f"Gather detailed research analysis and findings for '{topic}'.\n"
            f"{grounding_block}"
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
