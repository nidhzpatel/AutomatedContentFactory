# Automated Content Factory

An autonomous multi-agent content generation workflow built using CrewAI, FastAPI, and React.

## 🚀 Features

- **Multi-Agent Pipeline**: Research, Draft, Critique, Edit, and Fact-Check content autonomously.
- **RAG Support**: Ingest and retrieve contextual domain knowledge.
- **Guardrails**: Input validation, output verification, and hallucination checks.
- **Observability**: Built-in logging and execution tracing.
- **Web UI**: Modern React frontend for triggering workflows and reviewing generated content.

## 🛠️ Project Structure

```
automated-content-factory/
├── backend/            # FastAPI backend, CrewAI agents, crews & flows
├── frontend/           # React user interface
├── tests/              # Unit, integration, and security tests
├── evaluation/         # Benchmark topics and metric evaluation scripts
├── scripts/            # Helper scripts
├── Dockerfile          # Backend container image
└── docker-compose.yml  # Backend + Redis orchestration
```

## 🚦 Getting Started

1. Copy `.env.example` to `.env` and supply your API keys:
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
