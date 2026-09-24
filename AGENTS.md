# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Overview

Automated Content Factory: a multi-stage content generation pipeline (research → draft → critique → fact-check → edit → social formats) behind a FastAPI backend, with a React SPA frontend.

**Real runtime stack:** FastAPI + httpx → local Ollama (default `llama3:latest`). React 18 (CRA) frontend.

**Runtime:** CrewAI (1.x) is installed and powers the research and drafting stages via `ResearchCrew` / `ContentCrew`, wired into the flow with a direct-Ollama fallback. Still-unwired CrewAI-shaped scaffolding: `quality_crew.py`, the critic/fact-check/edit/social task factories, and all of `backend/rag/` (migration Phases 2–3). LangChain is present only as a CrewAI dependency — do not import it directly.

**Python:** requires `>=3.10,<3.14` — CrewAI has no Python 3.14-compatible release, so the venv runs Python 3.12.

## Quick Commands

| Task | Command |
|---|---|
| Setup | `pip install -e .`, then `cp .env.example .env` and fill in keys |
| Backend (dev) | `./scripts/run.sh` — uvicorn `backend.main:app` on `:8000` (uses `venv/bin/uvicorn` if present) |
| Frontend (dev) | `cd frontend && npm install && npm start` — on `:3000`, proxies `/api` to `:8000` |
| Docker | `docker-compose up --build` — backend + redis (redis is declared but **unused** by code) |
| Tests (fast) | `venv/bin/python -m pytest tests/unit tests/security -q` (29 tests) |
| Lint (unenforced) | `black .`, `flake8 .` |
| Evaluation | `venv/bin/python -m evaluation.run_evaluation` — **must be run as a module from repo root**; `python evaluation/run_evaluation.py` fails (`ModuleNotFoundError: No module named 'evaluation'`) |

**Integration tests** (`tests/integration/test_flows.py`) call Ollama at `localhost:11434`. A down Ollama fails fast (connection refused → canned fallbacks), so the test still passes quickly; the 90 s httpx timeout only bites when Ollama accepts connections but hangs. With Ollama up, the test runs the full real pipeline (~4 min). Run it only with Ollama up.

## Architecture (as implemented)

- **Entry point:** `POST /api/generate` with body `{"topic": str}` → `MainContentFlow(topic).execute()` (`backend/flows/main_flow.py`). Also `GET /` and `GET /health`. Responses include a `meta` block (`project`, `environment`) injected by the route via `get_settings()`.
- **Pipeline:** input guardrail → researcher → writer → critic → fact-checker → revision loop (`max_revisions=3`) → output guardrail → social-format generation. Returns `blog_post`, `linkedin_post`, `x_post`, `detailed_overview`, `metrics`, `status`.
- **Critic & fact-checker are real:** both call Ollama and parse a strict response format (`CLARITY/ENGAGEMENT/APPROVED/SUGGESTIONS` and `VERDICT/CLAIMS` — see the `_parse_*` helpers in `main_flow.py`). Unparseable or empty responses fall back to lenient pre-approved feedback so the pipeline still completes when Ollama is down. The revision loop re-critiques and re-checks the *edited* content each iteration, so it can converge before hitting the cap.
- **LLM calls:** `async_query_ollama()` in `main_flow.py` POSTs to `{settings.OLLAMA_BASE_URL}/api/generate` (90 s timeout, temp 0.7). **It swallows all exceptions and returns `""`**; every caller has canned fallback content. Preserve this pattern — letting exceptions propagate will turn Ollama downtime into API 500s. The critic/fact-check/edit/social stages still use this directly until Phase 2.
- **LLM routing (`backend/llm/factory.py`):** the CrewAI crews get their LLM from `get_llm()` — it probes Ollama (`/api/tags`, 2 s budget) and returns a CrewAI `LLM`; on repeated failure a circuit breaker (`LLM_CIRCUIT_FAILURE_THRESHOLD` / `LLM_CIRCUIT_RECOVERY_SECONDS`) routes to the cloud fallback (OpenAI, then Anthropic) only when `LLM_CLOUD_ENABLED` and the key are set. `get_llm()` returns None if crewai isn't installed — callers must handle that.
- **CrewAI wiring:** `run_researcher` / `run_writer` try `ResearchCrew` / `ContentCrew` first (via `asyncio.to_thread` — `kickoff()` is blocking) and silently fall back to the direct path on any crew failure. Crews and agents set `memory=False` so CrewAI never tries to call OpenAI embeddings behind your back.
- **"Agents":** classes in `backend/agents/` are plain Python returning `{role, goal, backstory}` config dicts. The live flow implements each agent as a flow method that calls `async_query_ollama` with a system prompt built from the role. There is no agent framework.
- **Config:** single pydantic-settings `Settings` singleton — import as `from backend.config import settings` (`env_file=".env"`, `extra="ignore"`). `OLLAMA_BASE_URL` / `OLLAMA_MODEL` (in `backend/config.py`) are the settings that matter; both are now in `.env.example`.
- **Logging:** `from backend.observability.logger import get_logger`, then `logger = get_logger("<module>")` — INFO to stdout. `settings.LOG_LEVEL` is defined but not wired to the logger.
- **State:** pydantic v2 schemas in `backend/models/`; central `FlowState` in `backend/models/state.py`.

## Guardrails

- `guardrails/input_guardrail.py` — `validate_input_prompt()` regex-scans for 11 jailbreak/injection patterns; wired, blocks the request before generation.
- `guardrails/hallucination_guardrail.py` — `check_hallucination()`, deterministic phrase scan producing `hallucination_rate` / `trust_score`; wired, and its result is a hard floor on the fact-check verdict.
- `guardrails/output_guardrail.py` — `validate_output_content()` non-empty check on the final content; wired, returns `status: failed_output_guardrail` if it trips.

## Conventions & Rules

- **After any code change, check and update the three doc files to keep them in sync:** `README.md` (user-facing setup & features), `AGENTS.md` (agent guidance), `SKILLS.md` (capability catalog). A change isn't done until all three match the code.
- Python ≥ 3.10, pydantic v2, `async`/`await` for I/O.
- Never hardcode secrets — `.env` only (gitignored).
- **`docs/` is intentionally gitignored (local-only). Never commit it.** Durable guidance belongs in this file.
- Frontend is a single 475-line `App.js` (CRA, no router, inline styles) — match that style unless deliberately restructuring.
- CORS is `allow_origins=["*"]` — known-loose, fine for local dev; flag it if you touch deployment/auth (there is no auth).

## Intentional Scaffolding (unwired by design — don't wire or remove without a decision)

- `backend/crews/quality_crew.py` and the critic/fact-check/edit/social factories in `backend/tasks/` — stubs awaiting migration Phase 2 (QualityCrew + revision loop via a CrewAI Flow router). The research/content crews and their tasks are **real and wired**.
- `backend/rag/` — unwired stubs (Phase 3: Ollama embeddings + chromadb, which is already installed).
- `backend/tools/tavily_search.py` — stub returning fake results; Phase 3 wires the real Tavily tool.
- redis in `docker-compose.yml` + `REDIS_URL` / `VECTOR_DB_URL` in config — reserved for the RAG work above.
