# AI Engineering Track

**A 15-week curriculum to become a job-ready AI Engineer.**

No prior AI/ML experience required. You start from your first API call and end with a production-ready application and 3 portfolio projects.

---

## Your Journey

```
Week 1:      "I can call LLM APIs, build a chatbot, and get structured output"
Weeks 2-4:   "My AI answers questions from my own documents (RAG)"
Weeks 5-6:   "I can measure quality and protect my system from attacks"
Weeks 7-11:  "My AI can reason, take actions, and use tools autonomously"
Weeks 12-15: "My AI system is production-ready and I'm interview-ready"
```

---

## Curriculum Overview

See [agenda/00_summary.md](agenda/00_summary.md) for the complete roadmap with priorities and interview relevance.

### Month 1: First Steps

| Week | Topic | What You'll Build |
|------|-------|-------------------|
| [Week 1](agenda/week_01.md) | API Basics, Chatbot & Structured Output | First API call, chatbot with memory, validated JSON output |
| [Week 2](agenda/week_02.md) | RAG Introduction | Document Q&A — your chatbot answers from your own files |
| [Week 3](agenda/week_03.md) | Embeddings Deep Dive | Semantic search pipeline, embedding model comparison |
| [Week 4](agenda/week_04.md) | Production RAG Architecture | Full RAG with Qdrant, citations, hybrid search |

### Month 2: Quality & Safety

| Week | Topic | What You'll Build |
|------|-------|-------------------|
| [Week 5](agenda/week_05.md) | Evaluations & Quality Metrics | Test suite, retrieval/generation metrics, LLM-as-judge |
| [Week 6](agenda/week_06.md) | Security & Guardrails | Input validation, PII protection, red-team tests — **Portfolio #1** |

**Portfolio #1:** [Secure HR Q&A Bot](projects/01_rag_qa_system/) — RAG + security guardrails + evaluations

### Month 3: Intelligence

| Week | Topic | What You'll Build |
|------|-------|-------------------|
| [Week 7](agenda/week_07.md) | Agent Fundamentals (ReAct) | Custom ReAct agent, multi-step problem solver |
| [Week 8](agenda/week_08.md) | Tool Calling & Function Execution | AI that calls multiple tools, full tool loop |
| [Week 9](agenda/week_09.md) | Agent Frameworks — LangGraph & Multi-Modal | LangGraph workflows, Strands Agents multi-agent, vision/audio (optional) |
| [Week 10](agenda/week_10.md) | LangGraph in Practice + LangSmith & Langfuse | Observable, evaluatable agents with tracing |
| [Week 11](agenda/week_11.md) | Data Engineering for AI | SQL, ETL pipelines, data quality — **Portfolio #2** |

**Portfolio #2:** [AI Agent](projects/02_ai_agent/) — ReAct reasoning + tools + step logging + data pipeline

### Month 4: Production & Career

| Week | Topic | What You'll Build |
|------|-------|-------------------|
| [Week 12](agenda/week_12.md) | MCP & Observability | MCP server, logging, tracing, metrics dashboard |
| [Week 13](agenda/week_13.md) | Production Hardening | Rate limiting, caching, retries, RBAC, secrets management |
| [Week 14](agenda/week_14.md) | Deployment & Fine-Tuning | Docker, cloud deployment, Slack/Teams bot |
| [Week 15](agenda/week_15.md) | Capstone & Interview Prep | Final project + interview readiness — **Portfolio #3** |

**Portfolio #3:** [Full-Stack AI Research Assistant](projects/03_capstone/) — FastAPI + RAG + agents + Docker

---

## Setup

```bash
# Install dependencies (uses uv)
uv sync

# Copy and fill in your API keys
cp .env.example .env

# Start Jupyter Lab
uv run jupyter lab
```

### Environment Variables (`.env`)

```
OPENAI_API_KEY=sk-...

# Optional — use local Ollama models instead of OpenAI
AI_PROVIDER=ollama          # "openai" (default) or "ollama"
OLLAMA_BASE_URL=http://localhost:11434
```

### Using Local Models (Free, No API Key)

All weeks support [Ollama](https://ollama.com) as a free alternative to OpenAI:

```bash
# Install Ollama, then pull models as needed
ollama pull llama3.1:8b          # General chat
ollama pull nomic-embed-text     # Embeddings
ollama pull deepseek-r1:7b       # ReAct agent reasoning

# Switch provider
export AI_PROVIDER=ollama
```

The unified client in `scripts/model_config.py` handles provider switching automatically.

---

## Labs (Hands-On Practice)

Each week has a companion Jupyter notebook in [labs/](labs/):

| Lab | Topic |
|-----|-------|
| [week_00_getting_started.ipynb](labs/week_00_getting_started.ipynb) | Environment setup verification |
| [week_01_first_api_call.ipynb](labs/week_01_first_api_call.ipynb) | API basics, chatbot, structured output |
| [week_02_rag_intro.ipynb](labs/week_02_rag_intro.ipynb) | RAG pipeline introduction |
| [week_03_embeddings.ipynb](labs/week_03_embeddings.ipynb) | Embeddings and semantic search |
| [week_04_production_rag.ipynb](labs/week_04_production_rag.ipynb) | Production RAG with Qdrant |
| [week_05_evaluations.ipynb](labs/week_05_evaluations.ipynb) | Evaluations and quality metrics |
| [week_06_security.ipynb](labs/week_06_security.ipynb) | Security and guardrails |
| [week_07_agents.ipynb](labs/week_07_agents.ipynb) | Agent fundamentals (ReAct) |
| [week_08_tool_calling.ipynb](labs/week_08_tool_calling.ipynb) | Tool calling and function execution |
| [week_09_frameworks.ipynb](labs/week_09_frameworks.ipynb) | LangGraph and agent frameworks |
| [week_10_frameworks_observability.ipynb](labs/week_10_frameworks_observability.ipynb) | LangSmith and Langfuse |
| [week_11_data_engineering.ipynb](labs/week_11_data_engineering.ipynb) | SQL, ETL pipelines, data quality |
| [week_12_mcp.ipynb](labs/week_12_mcp.ipynb) | MCP and observability |
| [week_13_production.ipynb](labs/week_13_production.ipynb) | Production hardening |
| [week_14_deployment.ipynb](labs/week_14_deployment.ipynb) | Deployment and fine-tuning |
| [week_15_capstone.ipynb](labs/week_15_capstone.ipynb) | Capstone and interview prep |

### How Labs Work

1. Read the agenda first: `agenda/week_XX.md`
2. Open the lab notebook: `labs/week_XX_*.ipynb`
3. Try each exercise yourself — hints and solutions are collapsible inside the notebook

---

## Portfolio Projects

| # | Project | Week | Skills Demonstrated |
|---|---------|------|---------------------|
| 1 | [Secure HR Q&A Bot](projects/01_rag_qa_system/) | 6 | RAG, embeddings, security, evaluations |
| 2 | [AI Agent](projects/02_ai_agent/) | 11 | Tool calling, ReAct, observability, data pipelines |
| 3 | [Full-Stack AI Research Assistant](projects/03_capstone/) | 15 | All of the above + FastAPI + Docker |

---

## Repository Structure

```
ai_track/
├── agenda/              # Week-by-week guides with theory and tasks
│   ├── 00_summary.md    # Full curriculum overview and roadmap
│   └── week_01.md ... week_15.md
├── labs/                # Jupyter notebook exercises (one per week)
│   └── week_00_getting_started.ipynb ... week_15_capstone.ipynb
├── projects/            # Portfolio project templates
│   ├── 01_rag_qa_system/   # Portfolio #1: Secure HR Q&A Bot
│   ├── 02_ai_agent/        # Portfolio #2: AI Agent
│   └── 03_capstone/        # Portfolio #3: Full-Stack Research Assistant
├── scripts/
│   └── model_config.py  # Unified OpenAI/Ollama client
├── knowledges.md        # Quick-reference cheat sheet for all concepts
├── pyproject.toml       # Dependencies (managed with uv)
└── uv.lock
```

---

## Prerequisites

- Basic Python (variables, functions, loops, classes)
- Command line basics
- No AI/ML experience needed

---

## Resources

- [agenda/00_summary.md](agenda/00_summary.md) — Full roadmap with priorities and interview relevance
- [knowledges.md](knowledges.md) — Concept quick-reference cheat sheet
- Each week's agenda includes links to relevant docs and tutorials
