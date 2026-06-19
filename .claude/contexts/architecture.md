# ai_track Architecture Context

This file is imported by CLAUDE.md with `@.claude/contexts/architecture.md`.
It provides Claude with project structure context on every session.

## Repository Layout

```
ai_track/
├── agenda/           # Theory markdown files (week_XX.md)
├── labs/             # Jupyter notebooks (week_XX_*.ipynb)
├── projects/
│   ├── 01_rag_qa_system/    # Portfolio #1 (Weeks 5-8)
│   ├── 02_ai_agent/         # Portfolio #2 (Weeks 9-12)
│   └── 03_capstone/         # Portfolio #3 (Weeks 13-16)
├── scripts/
│   └── model_config.py      # Unified OpenAI/Ollama client
├── .claude/          # Claude Code configuration (this directory)
├── pyproject.toml    # Dependencies (managed by uv)
├── uv.lock           # Lockfile — always commit this
└── .env              # API keys (gitignored — copy from .env.example)
```

## Curriculum Progression

| Weeks | Theme | Portfolio |
|-------|-------|-----------|
| 1-4   | API basics, chatbot memory, structured output, basic RAG | — |
| 5-8   | Embeddings pipeline, production RAG, evaluations, security | #1 RAG Q&A |
| 9-12  | Tool calling, ReAct agents, LangGraph, data engineering | #2 AI Agent |
| 13-16 | MCP, observability, production hardening, deployment | #3 Capstone |

## Key Technical Decisions

- **Package manager:** uv exclusively — never pip
- **Default model:** `gpt-4o-mini` in all labs (cheap, fast, good enough for learning)
- **Local models:** Set `AI_PROVIDER=ollama` in `.env` to switch to Ollama
- **Vector DB:** Qdrant (cloud) or Chroma (local) — both supported
- **Testing:** pytest under `projects/01_rag_qa_system/tests/`
- **Env loading in notebooks:** Parent directory pattern (labs run one level below root)
