from backend.agents.researcher import create_researcher_agent
from backend.agents.writer import create_writer_agent


def test_researcher_agent_creation(monkeypatch):
    monkeypatch.setattr("backend.llm.factory._probe_ollama", lambda: True)
    agent = create_researcher_agent()
    assert "Research Analyst" in agent.role


def test_writer_agent_creation(monkeypatch):
    monkeypatch.setattr("backend.llm.factory._probe_ollama", lambda: True)
    agent = create_writer_agent()
    assert "Writer" in agent.role
