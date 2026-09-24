# Automated Content Factory

An autonomous multi-agent content generation workflow built with CrewAI, FastAPI, and React — powered by a local Ollama LLM with automatic cloud fallback, private by default with zero per-call API cost.

## 🚀 Features

- **Multi-Agent Pipeline**: CrewAI-powered research, drafting, critique, fact-check, and edit stages with a self-correcting revision loop.
- **Resilient LLM Routing**: Local Ollama primary with automatic cloud fallback (OpenAI/Anthropic) behind a circuit breaker.
- **RAG Knowledge Base**: Ingest domain documents via `POST /api/ingest`; research and fact-check stages are grounded with local embeddings (Ollama + chromadb).
- **Web Search**: The researcher agent searches the live web via Tavily when an API key is configured.
- **Guardrails**: Input validation, output verification, and hallucination checks.
- **Observability**: Built-in logging and execution tracing.
- **Web UI**: Modern React frontend for triggering workflows and reviewing generated content.

## 🛠️ Project Structure

```
automated-content-factory/
├── backend/            # FastAPI backend: CrewAI crews & flows, guardrails, RAG knowledge base
├── frontend/           # React user interface
├── tests/              # Unit, integration, and security tests
├── evaluation/         # Benchmark topics and metric evaluation scripts
├── scripts/            # Helper scripts
├── Dockerfile          # Backend container image
└── docker-compose.yml  # Backend + Redis orchestration
```

## 🚦 Getting Started

Requires **Python 3.10–3.13** (CrewAI is not yet compatible with Python 3.14).

1. Copy `.env.example` to `.env` and adjust as needed. The only hard requirement is a running local Ollama (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`); the listed API keys power the optional cloud fallback and future integrations:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Run the backend development server:
   ```bash
   ./scripts/run.sh
   ```
   The API will be available at `http://localhost:8000`.
4. In a separate terminal, start the React frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```
   The UI will be available at `http://localhost:3000` and proxies API requests to the backend.

## 🐳 Docker

Alternatively, run the backend and Redis together with Docker:

```bash
docker-compose up --build
```

This starts the backend on `http://localhost:8000` and a Redis instance on port `6379`.
