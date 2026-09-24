import threading
import time
from typing import Optional

import httpx

from backend.config import settings
from backend.observability.logger import get_logger

logger = get_logger("llm_factory")

_circuit_lock = threading.Lock()
_consecutive_failures = 0
_circuit_opened_at: Optional[float] = None


def _reset_circuit() -> None:
    """Reset circuit-breaker state (intended for tests)."""
    global _consecutive_failures, _circuit_opened_at
    with _circuit_lock:
        _consecutive_failures = 0
        _circuit_opened_at = None


def _circuit_is_open() -> bool:
    """Open circuits block Ollama probes until the recovery window elapses."""
    if _circuit_opened_at is None:
        return False
    return (time.time() - _circuit_opened_at) < settings.LLM_CIRCUIT_RECOVERY_SECONDS


def _record_ollama_success() -> None:
    global _consecutive_failures, _circuit_opened_at
    with _circuit_lock:
        _consecutive_failures = 0
        _circuit_opened_at = None


def _record_ollama_failure() -> None:
    global _consecutive_failures, _circuit_opened_at
    with _circuit_lock:
        _consecutive_failures += 1
        if _consecutive_failures >= settings.LLM_CIRCUIT_FAILURE_THRESHOLD:
            _circuit_opened_at = time.time()
            logger.warning(
                f"Ollama circuit opened after {_consecutive_failures} consecutive failures; "
                f"cloud fallback active for {settings.LLM_CIRCUIT_RECOVERY_SECONDS}s"
            )


def _probe_ollama() -> bool:
    """Quick health check against Ollama's /api/tags (2 s budget)."""
    try:
        response = httpx.get(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags", timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


def _cloud_llm():
    from crewai import LLM

    if not settings.LLM_CLOUD_ENABLED:
        return None

    candidates = []
    if settings.OPENAI_API_KEY:
        candidates.append(("openai", settings.OPENAI_FALLBACK_MODEL, settings.OPENAI_API_KEY))
    if settings.ANTHROPIC_API_KEY:
        candidates.append(("anthropic", settings.ANTHROPIC_FALLBACK_MODEL, settings.ANTHROPIC_API_KEY))

    for provider, model, api_key in candidates:
        try:
            return LLM(model=f"{provider}/{model}", api_key=api_key)
        except Exception as e:
            logger.warning(f"cloud provider '{provider}' unavailable ({e}); trying next")
    return None


def get_llm(agent_name: str = ""):
    """Return a CrewAI LLM bound to the healthiest available backend.

    Ollama is the primary backend. Cloud models are used only as fallback
    (requires LLM_CLOUD_ENABLED and the relevant API key). A circuit breaker
    stops repeated slow probes against a down Ollama. Returns None if crewai
    is not installed.
    """
    try:
        from crewai import LLM
    except ImportError:
        logger.error("crewai is not installed; cannot construct LLM")
        return None

    ollama_model = f"ollama/{settings.OLLAMA_MODEL}"

    if not _circuit_is_open() and _probe_ollama():
        _record_ollama_success()
        return LLM(model=ollama_model, base_url=settings.OLLAMA_BASE_URL)

    if not _circuit_is_open():
        _record_ollama_failure()

    fallback = _cloud_llm()
    if fallback is not None:
        logger.warning(f"[{agent_name}] Ollama unavailable; using cloud fallback LLM")
        return fallback

    logger.warning(f"[{agent_name}] no healthy LLM backend; returning Ollama LLM as last resort")
    return LLM(model=ollama_model, base_url=settings.OLLAMA_BASE_URL)
