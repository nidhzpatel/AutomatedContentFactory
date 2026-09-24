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

The critic and fact-checker gate a **revision loop** (up to `max_revisions = 3`): the editor revises until both approve or the cap is hit.

## Output Formats

One `POST /api/generate` call with `{"topic": "..."}` returns:

- `blog_post` — long-form article (markdown)
- `linkedin_post` — LinkedIn-formatted post
- `x_post` — X/Twitter-formatted post
- `detailed_overview` — extended summary
- `metrics` — latency, revision-loop count, fact-check %, hallucination %, word count

## Safety & Quality Guardrails

- **Input screening** — prompt-injection / jailbreak detection (11 regex patterns: instruction overrides, DAN mode, `rm -rf`, `eval(`, etc.); violating requests are rejected before any generation with `status: failed_security_guardrail`.
- **Hallucination check** — deterministic scan of generated text for flagged phrases; produces `hallucination_rate` and `trust_score`.
- **Input validation** — empty topics rejected with HTTP 400.

## Metrics & Evaluation

- Runtime metrics returned with every generation (see above).
- `evaluation/metrics/metrics.py`: readability score, keyword-relevance score, word count, hallucination scan.
- `evaluation/run_evaluation.py` — benchmark over `evaluation/datasets/topics.json` topics with expected keywords. Run: `python -m evaluation.run_evaluation` (from repo root, as a module).

## Model Runtime

- LLM: **local Ollama** (default model `llama3:latest`, configurable via `OLLAMA_BASE_URL` / `OLLAMA_MODEL` in `.env`) — private, zero per-call API cost.
- Graceful degradation: if Ollama is unreachable, the pipeline returns canned fallback content instead of erroring.

## API Surface

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/generate` | Run the full pipeline for a topic |
| GET | `/health` | Liveness check |
| GET | `/` | Status banner |

## Scaffolding (defined, not yet live)

CrewAI-shaped stubs exist for future extension and are **not wired into the pipeline**: sub-crews (`backend/crews/`), task definitions (`backend/tasks/`), RAG ingestion/embed/retrieve (`backend/rag/`), Tavily search tool, output-content guardrail, execution tracer, and the `SocialMediaCampaign` model.
