import asyncio
import json

import httpx
import pytest

from backend.crews.social_crew import SocialCrew
from backend.flows.main_flow import MainContentFlow
from backend.observability.tracer import trace_execution


@pytest.fixture(autouse=True)
def no_direct_ollama_calls(monkeypatch):
    async def fake_query(client, prompt, system_prompt="", max_tokens=1500):
        return ""

    monkeypatch.setattr("backend.flows.main_flow.async_query_ollama", fake_query)


def test_flow_uses_social_crew_result(monkeypatch):
    crew_output = {
        "linkedin": "LinkedIn post from crew " + "x" * 30,
        "x_post": "X post from crew " + "x" * 30,
        "overview": "Overview from crew " + "x" * 30,
    }
    monkeypatch.setattr(SocialCrew, "run", lambda self: crew_output)

    async def run():
        flow = MainContentFlow(topic="AI Safety")
        async with httpx.AsyncClient() as client:
            return await flow.generate_social_media(client)

    result = asyncio.run(run())
    assert result["linkedin"] == crew_output["linkedin"]
    assert result["x_post"] == crew_output["x_post"]
    assert result["overview"] == crew_output["overview"]
    assert [p.platform for p in result["campaign"].posts] == ["linkedin", "x", "overview"]


def test_flow_falls_back_when_social_crew_fails(monkeypatch):
    def boom(self):
        raise RuntimeError("crew exploded")

    monkeypatch.setattr(SocialCrew, "run", boom)

    async def run():
        flow = MainContentFlow(topic="AI Safety")
        async with httpx.AsyncClient() as client:
            return await flow.generate_social_media(client)

    result = asyncio.run(run())
    # direct fallback path: canned content (Ollama faked to "")
    assert "AI Safety" in result["linkedin"]
    assert "Detailed Technical Overview" in result["overview"]


def test_trace_execution_emits_json_lines(capsys):
    trace_execution("test_step", {"key": "value"})
    out = capsys.readouterr().out.strip()
    assert out.startswith("[TRACE] ")
    event = json.loads(out[len("[TRACE] "):])
    assert event["step"] == "test_step"
    assert event["payload"] == {"key": "value"}
    assert isinstance(event["ts"], float)
