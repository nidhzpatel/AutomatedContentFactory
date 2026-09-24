import asyncio

import httpx
import pytest

from backend.crews.research_crew import ResearchCrew
from backend.crews.content_crew import ContentCrew
from backend.flows.main_flow import MainContentFlow
from backend.models.research import ResearchOutput


@pytest.fixture(autouse=True)
def no_direct_ollama_calls(monkeypatch):
    """Force the direct fallback path to its canned content (no live LLM)."""
    async def fake_query(client, prompt, system_prompt="", max_tokens=1500):
        return ""

    monkeypatch.setattr("backend.flows.main_flow.async_query_ollama", fake_query)


def _research_output():
    return ResearchOutput(topic="AI Safety", summary="crew-provided summary")


def test_flow_uses_research_crew_result(monkeypatch):
    monkeypatch.setattr(ResearchCrew, "run", lambda self: _research_output())

    async def run():
        flow = MainContentFlow(topic="AI Safety")
        async with httpx.AsyncClient() as client:
            return await flow.run_researcher(client)

    result = asyncio.run(run())
    assert result.summary == "crew-provided summary"


def test_flow_falls_back_when_research_crew_fails(monkeypatch):
    def boom(self):
        raise RuntimeError("ollama down")

    monkeypatch.setattr(ResearchCrew, "run", boom)

    async def run():
        flow = MainContentFlow(topic="AI Safety")
        async with httpx.AsyncClient() as client:
            return await flow.run_researcher(client)

    result = asyncio.run(run())
    # direct path: Ollama unreachable -> canned fallback summary
    assert result.summary.startswith("Comprehensive research summary")


def test_flow_uses_content_crew_result(monkeypatch):
    from backend.models.draft import DraftContent
    crew_draft = DraftContent(title="Crew Title", body="# Crew Title\n\nbody content here", word_count=6)
    monkeypatch.setattr(ContentCrew, "run", lambda self: crew_draft)

    async def run():
        flow = MainContentFlow(topic="AI Safety")
        async with httpx.AsyncClient() as client:
            return await flow.run_writer(client, _research_output())

    result = asyncio.run(run())
    assert result.title == "Crew Title"


def test_flow_falls_back_when_content_crew_fails(monkeypatch):
    def boom(self):
        raise RuntimeError("crew exploded")

    monkeypatch.setattr(ContentCrew, "run", boom)

    async def run():
        flow = MainContentFlow(topic="AI Safety")
        async with httpx.AsyncClient() as client:
            return await flow.run_writer(client, _research_output())

    result = asyncio.run(run())
    # direct path canned fallback draft
    assert "Mastering AI Safety" in result.title
