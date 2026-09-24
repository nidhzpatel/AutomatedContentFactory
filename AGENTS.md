# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project Overview

Automated Content Factory: a multi-stage content generation pipeline (research → draft → critique → fact-check → edit → social formats) behind a FastAPI backend, with a React SPA frontend.

**Real runtime stack:** FastAPI + CrewAI (crews & Flow) → local Ollama via `backend/llm` routing (cloud fallback ready). React 18 (CRA) frontend.

**Runtime:** CrewAI (1.x) powers the full pipeline: `ContentFactoryFlow` (a real CrewAI `Flow` in `backend/flows/crew_flow.py`) orchestrates `ResearchCrew` → `ContentCrew` → `QualityCrew` with a `@router`-driven revision loop. `MainContentFlow` tries the CrewAI flow first and falls back to the hand-rolled direct-Ollama path on any failure. Research tasks are grounded from the local RAG knowledge base (`backend/rag/`, chromadb + Ollama embeddings) and the researcher agent gets a real Tavily web-search tool when `TAVILY_API_KEY` is set. Still unwired (Phase 4): the social task factory. LangChain is present only as a CrewAI dependency — do not import it directly.

**Python:** requires `>=3.10,<3.14` — CrewAI has no Python 3.14-compatible release, so the venv runs Python 3.12.

## Quick Commands

| Task | Command |
|---|---|
| Setup | `pip install -e .`, then `cp .env.example .env` and fill in keys |
| Backend (dev) | `./scripts/run.sh` — uvicorn `backend.main:app` on `:8000` (uses `venv/bin/uvicorn` if present) |
| Frontend (dev) | `cd frontend && npm install && npm start` — on `:3000`, proxies `/api` to `:8000` |
| Docker | `docker-compose up --build` — backend + redis (redis is declared but **unused** by code) |
| Tests (fast) | `venv/bin/python -m pytest tests/unit tests/security -q` (44 tests) |
| Lint (unenforced) | `black .`, `flake8 .` |
| Evaluation | `venv/bin/python -m evaluation.run_evaluation` — **must be run as a module from repo root**; `python evaluation/run_evaluation.py` fails (`ModuleNotFoundError: No module named 'evaluation'`) |

**Integration tests** (`tests/integration/test_flows.py`) call Ollama at `localhost:11434`. A down Ollama fails fast (connection refused → canned fallbacks), so the test still passes quickly; the 90 s httpx timeout only bites when Ollama accepts connections but hangs. With Ollama up, the test runs the full real pipeline (~4 min). Run it only with Ollama up.

## Architecture (as implemented)

- **Entry point:** `POST /api/generate` with body `{"topic": str}` → `MainContentFlow(topic).execute()` (`backend/flows/main_flow.py`). Also `GET /` and `GET /health`. Responses include a `meta` block (`project`, `environment`) injected by the route via `get_settings()`.
- **Pipeline:** input guardrail → researcher → writer → critic → fact-checker → revision loop (`max_revisions=3`) → output guardrail → social-format generation. Returns `blog_post`, `linkedin_post`, `x_post`, `detailed_overview`, `metrics`, `status`.
- **Two execution paths, one contract:** `execute()` first runs the CrewAI `ContentFactoryFlow` (`backend/flows/crew_flow.py`): input guardrail (raises `InputGuardrailRejected` → guardrail-failure payload) → `ResearchCrew` → `ContentCrew` → `QualityCrew.review()` → `@router` quality gate → edit/re-review loop (cap `max_revisions`) → accept. Social generation, the output guardrail, and response assembly are shared via `_assemble_result()`. Any CrewAI-flow failure falls back to the direct path: the same stages run as flow methods over `async_query_ollama`, with parsing via the shared helpers in `backend/parsing.py` (`parse_critique`, `parse_fact_check_response`). Unparseable responses fall back to lenient pre-approved values so the pipeline completes even with a misbehaving model.
- **LLM calls (direct fallback path):** `async_query_ollama()` in `main_flow.py` POSTs to `{settings.OLLAMA_BASE_URL}/api/generate` (90 s timeout, temp 0.7). **It swallows all exceptions and returns `""`**; every caller has canned fallback content. Preserve this pattern — letting exceptions propagate will turn Ollama downtime into API 500s.
- **LLM routing (`backend/llm/factory.py`):** the CrewAI crews get their LLM from `get_llm()` — it probes Ollama (`/api/tags`, 2 s budget) and returns a CrewAI `LLM`; on repeated failure a circuit breaker (`LLM_CIRCUIT_FAILURE_THRESHOLD` / `LLM_CIRCUIT_RECOVERY_SECONDS`) routes to the cloud fallback (OpenAI, then Anthropic) only when `LLM_CLOUD_ENABLED` and the key are set. `get_llm()` returns None if crewai isn't installed — callers must handle that.
- **CrewAI wiring:** `crew.kickoff()` and `flow.kickoff()` are blocking — never call from async code without `asyncio.to_thread` (the CrewAI Flow itself runs inside `to_thread` from `execute()`). Crews and agents set `memory=False` so CrewAI never tries to call OpenAI embeddings behind your back.
- **RAG (`backend/rag/`):** `store.py` holds a lazily-created chromadb `PersistentClient` (`settings.CHROMA_PERSIST_DIR`, gitignored); `embedder.py` calls Ollama `/api/embed` (batched `embed_documents` for ingestion); `ingestion.py` chunks (~500 chars, 50 overlap) and stores; `retriever.py` fails soft to `[]`. Grounding is wired into the research task (topic retrieval) and the fact-check task (draft excerpt retrieval) — both degrade to ungrounded when retrieval fails. `ingest_document()` is blocking: the `/api/ingest` route wraps it in `asyncio.to_thread`.
- **Web search (`backend/tools/tavily_search.py`):** `create_tavily_search_tool()` returns a crewai `TavilySearchTool` when `TAVILY_API_KEY` is set, else `None` — the researcher agent attaches `tools=[tool] if tool else []`. The standalone `tavily_search_tool(query)` is for non-agent callers.
- **CrewAI Flow gotchas (verified on crewai 1.15):** flow state is hydrated with `kickoff(inputs={...})` — `state=` at construction is silently ignored; state models used with `Flow[State]` need defaults on every field because the flow projection re-validates them (hence `FlowState.topic = ""`). Revision loops need **two routers** (`@router(review)` + `@router(re_review)`) — a single router behind an `or_()` listener does not re-fire after the first pass. Flow methods can only `@listen` to methods defined *above* them in the class body, and a handler can't listen to a route key equal to its own name.
- **"Agents":** `backend/agents/*.py` build real CrewAI `Agent` objects (role/goal/backstory preserved verbatim) with `llm=get_llm(...)` and `memory=False`. The direct fallback path implements equivalent behavior as flow methods with hand-built system prompts.
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

- `backend/tasks/social_task.py` — stub awaiting Phase 4 (social generation is currently the flow's `generate_social_media`, not a CrewAI task).
- redis in `docker-compose.yml` + `REDIS_URL` / `VECTOR_DB_URL` in config — reserved for future caching needs; the RAG layer uses chromadb directly, not redis.
