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
├── docs/               # System documentation, security guides & architecture
│   └── architecture.md # Complete system architecture & technical deep-dive
└── scripts/            # Helper scripts
```

For a detailed technical breakdown, system component diagrams, and data flow sequences, see **[Architecture Documentation](file:///Users/nidhirajkotiya/Projects/AutomatedContentCreation/docs/architecture.md)**.

## 🚦 Getting Started

1. Copy `.env.example` to `.env` and supply your API keys:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Run the development server:
   ```bash
   ./scripts/run.sh
   ```
