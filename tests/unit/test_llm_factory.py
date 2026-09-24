import pytest

from backend.config import settings
from backend.llm import factory
from backend.llm.factory import get_llm, _reset_circuit


@pytest.fixture(autouse=True)
def reset_circuit():
    _reset_circuit()
    yield
    _reset_circuit()


def test_ollama_healthy_returns_ollama_llm(monkeypatch):
    monkeypatch.setattr(factory, "_probe_ollama", lambda: True)
    llm = get_llm("test")
    assert settings.OLLAMA_MODEL in llm.model


def test_ollama_down_falls_back_to_openai(monkeypatch):
    monkeypatch.setattr(factory, "_probe_ollama", lambda: False)
    monkeypatch.setattr(settings, "LLM_CLOUD_ENABLED", True)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    llm = get_llm("test")
    assert settings.OPENAI_FALLBACK_MODEL in llm.model


def test_ollama_down_falls_back_to_anthropic_when_no_openai_key(monkeypatch):
    monkeypatch.setattr(factory, "_probe_ollama", lambda: False)
    monkeypatch.setattr(settings, "LLM_CLOUD_ENABLED", True)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "sk-ant-test")
    llm = get_llm("test")
    assert settings.ANTHROPIC_FALLBACK_MODEL in llm.model


def test_cloud_disabled_returns_ollama_llm(monkeypatch):
    monkeypatch.setattr(factory, "_probe_ollama", lambda: False)
    monkeypatch.setattr(settings, "LLM_CLOUD_ENABLED", False)
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-test-key")
    llm = get_llm("test")
    assert settings.OLLAMA_MODEL in llm.model


def test_circuit_opens_after_threshold_failures(monkeypatch):
    monkeypatch.setattr(settings, "LLM_CIRCUIT_FAILURE_THRESHOLD", 2)
    monkeypatch.setattr(factory, "_probe_ollama", lambda: False)
    monkeypatch.setattr(settings, "LLM_CLOUD_ENABLED", False)

    get_llm("test")
    assert not factory._circuit_is_open()
    get_llm("test")
    assert factory._circuit_is_open()


def test_circuit_recovers_after_recovery_window(monkeypatch):
    monkeypatch.setattr(settings, "LLM_CIRCUIT_FAILURE_THRESHOLD", 1)
    monkeypatch.setattr(settings, "LLM_CIRCUIT_RECOVERY_SECONDS", 300.0)
    monkeypatch.setattr(factory, "_probe_ollama", lambda: False)
    monkeypatch.setattr(settings, "LLM_CLOUD_ENABLED", False)

    get_llm("test")
    assert factory._circuit_is_open()

    real_time = factory.time.time
    monkeypatch.setattr(factory.time, "time", lambda: real_time() + 301)
    monkeypatch.setattr(factory, "_probe_ollama", lambda: True)
    llm = get_llm("test")
    assert not factory._circuit_is_open()
    assert settings.OLLAMA_MODEL in llm.model


def test_probe_success_resets_failure_count(monkeypatch):
    monkeypatch.setattr(settings, "LLM_CIRCUIT_FAILURE_THRESHOLD", 3)
    probes = iter([False, False, True, False])
    monkeypatch.setattr(factory, "_probe_ollama", lambda: next(probes))
    monkeypatch.setattr(settings, "LLM_CLOUD_ENABLED", False)

    get_llm("test")
    get_llm("test")
    assert not factory._circuit_is_open()  # 2 failures, threshold 3
    get_llm("test")  # success resets counter
    get_llm("test")  # only 1 failure since reset
    assert not factory._circuit_is_open()
