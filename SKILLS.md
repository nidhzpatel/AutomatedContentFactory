# SKILLS.md

Capability catalog of the Automated Content Factory pipeline — what the system can do, as implemented.

## Pipeline Stages (5 Agent Roles)

| # | Stage | Role | Responsibility |
|---|---|---|---|
| 1 | Research | Senior Technical Research Analyst | Gather up-to-date research data, statistics, and domain context for the topic |
| 2 | Draft | Lead Technical Content Strategist & Writer | Write the long-form blog draft from the research |
| 3 | Critique | Senior Editorial Critic | Score the draft (clarity / engagement, 0–10), list suggestions, approve or reject |
| 4 | Fact-Check | Verification & Hallucination Auditor | Verify claims, produce a fact-check report with pass/fail |
| 5 | Edit | Executive Revision Editor | Revise the draft against critique + fact-check feedback; re-enter the check loop |

The critic and fact-checker gate a **revision loop** (up to `max_revisions = 3`): the editor revises until both approve or the cap is hit. All stages execute through CrewAI crews orchestrated by `ContentFactoryFlow`'s router-driven loop, with a direct-Ollama fallback if the CrewAI flow fails.

## Output Formats

One `POST /api/generate` call with `{"topic": "..."}` returns:

- `blog_post` — long-form article (markdown)
- `linkedin_post` — LinkedIn-formatted post
- `x_post` — X/Twitter-formatted post
- `detailed_overview` — extended summary
- `metrics` — `latency_ms`, `revision_count`, `fact_check_score`, `hallucination_rate` (0–1), `word_count`

## Safety & Quality Guardrails

- **Input screening** — prompt-injection / jailbreak detection (11 regex patterns: instruction overrides, DAN mode, `rm -rf`, `eval(`, etc.); violating requests are rejected before any generation with `status: failed_security_guardrail`.
- **Fact-check audit** — each draft is audited against the research context (LLM claim verification producing a `VERDICT` and per-claim `[VERIFIED]` / `[UNVERIFIED]` items) combined with a deterministic hallucination scan; produces `hallucination_rate` and `trust_score`, and a failing audit gates the revision loop.
- **Output validation** — the final article must pass a non-empty output check; failure returns `status: failed_output_guardrail`.
- **Input validation** — empty topics rejected with HTTP 400.

## Metrics & Evaluation

- Runtime metrics returned with every generation (see above).
- `evaluation/metrics/metrics.py`: readability score, keyword-relevance score, word count, hallucination scan.
- `evaluation/run_evaluation.py` — benchmark over `evaluation/datasets/topics.json` topics with expected keywords. Note: it scores synthetic sample text built from each topic + keywords, not live pipeline output (`MainContentFlow` is imported but unused). Run: `python -m evaluation.run_evaluation` (from repo root, as a module).

## Model Runtime

- LLM: **local Ollama** (default model `llama3:latest`, configurable via `OLLAMA_BASE_URL` / `OLLAMA_MODEL` in `.env`) — private, zero per-call API cost.
- **Fallback chain:** if Ollama fails a health probe, a circuit breaker routes to OpenAI (`gpt-4o-mini`) then Anthropic (`claude-3-5-haiku-latest`) — only when `LLM_CLOUD_ENABLED=true` and the matching API key is configured.
- Graceful degradation: if no backend is usable, the pipeline returns canned fallback content instead of erroring.

## Knowledge & Grounding

- **`POST /api/ingest`** — chunk, embed (Ollama `OLLAMA_EMBED_MODEL`, default `nomic-embed-text`), and store a document in the local chromadb collection (`CHROMA_PERSIST_DIR`, default `./chroma_db`, gitignored).
- Research tasks are prepended with retrieved internal knowledge (`retrieve_context(topic)`), and the fact-checker receives grounding chunks with the draft audit.
- Retrieval fails soft: any error returns `[]` and the stage continues ungrounded.

## API Surface

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/generate` | Run the full pipeline for a topic |
| POST | `/api/ingest` | Add a document to the RAG knowledge base |
| GET | `/health` | Liveness check |
| GET | `/` | Status banner |

## Scaffolding (not yet live — Phase 4)

The pipeline is fully wired through CrewAI (`ResearchCrew`, `ContentCrew`, `QualityCrew` under `ContentFactoryFlow`) with RAG grounding and optional Tavily web search; a direct-Ollama fallback covers any CrewAI failure. Not yet wired: the social-media task factory (`backend/tasks/social_task.py` — social generation currently lives in the flow's `generate_social_media`).
