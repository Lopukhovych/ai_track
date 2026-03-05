# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A 16-week AI engineering curriculum. The repo contains:
- `agenda/week_XX.md` — Theory and concepts for each week (read-first material)
- `labs/week_XX_*.ipynb` — Jupyter notebooks with hands-on exercises, hints, and solutions
- `projects/` — Three portfolio project scaffolds (RAG system, AI agent, capstone)
- `knowledges.md` — Quick-reference cheat sheet for all concepts

## Environment Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies (creates .venv automatically)
uv sync

# Run any script inside the managed environment
uv run python script.py
uv run pytest
uv run jupyter lab

# Add a new dependency
uv add some-package

# Copy and fill in API keys
cp .env.example .env
```

The lockfile is `uv.lock` — commit it. Dependencies are declared in `pyproject.toml`.

Required env var: `OPENAI_API_KEY`. Optional: `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`, `OLLAMA_BASE_URL`.

The `.env` file lives at the repo root. Lab notebooks load it from their parent directory via `load_dotenv(os.path.join(os.path.dirname(os.getcwd()), ".env"))`.

## Running Labs

Labs are Jupyter notebooks. Open them in VS Code (with the Jupyter extension) or JupyterLab:

```bash
uv run jupyter lab labs/week_01_first_api_call.ipynb
```

Run cells top-to-bottom — later cells depend on earlier ones. Default model throughout is `gpt-4o-mini`.

## Running Tests

```bash
uv run pytest
```

Project test files live under `projects/01_rag_qa_system/tests/` following the suggested structure in that project's README.

## Curriculum Architecture

The course builds a single evolving project across 4 months:

- **Weeks 1-4:** API basics, chatbot with memory, structured output (Pydantic), basic RAG
- **Weeks 5-8:** Embeddings pipeline, production RAG with vector DBs (Qdrant/Chroma), evaluations, security/guardrails → **Portfolio #1: RAG Q&A System**
- **Weeks 9-12:** Tool calling, ReAct agents, LangGraph/CrewAI frameworks, data engineering → **Portfolio #2: AI Agent**
- **Weeks 13-16:** MCP, observability, production hardening (caching, rate limiting, RBAC), deployment → **Portfolio #3: Capstone**

## Lab Exercise Format

Each notebook follows this pattern: code cells with `# TODO` comments, followed by collapsed `<details>` HTML blocks containing hints and solutions. Don't remove or reorganize these — the collapsible structure is intentional for the learning workflow.

## Key Dependencies by Week

- Weeks 1-4: `openai`, `python-dotenv`, `pydantic`
- Weeks 5-6: `qdrant-client` or `chromadb` (vector DBs)
- Week 11: `langchain`, `langchain-openai`, `llama-index`
- Week 15: `fastapi`, `uvicorn`
