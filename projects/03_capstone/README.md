# Portfolio Project #3: Full-Stack AI Research Assistant

**Week 15 Capstone** | Combines all skills from Weeks 1-15

Build a production-ready AI research assistant with RAG, tool-calling agents, multi-modal capabilities, a FastAPI backend, security, and observability.

---

## Project Description

The research assistant:
- Answers questions using RAG over a knowledge base
- Uses agents with tools for multi-step research tasks
- Accepts images for visual analysis
- Exposes a clean REST API with auth and rate limiting
- Is secure, observable, and deployable via Docker

---

## Architecture

```
FastAPI Gateway (auth, rate limiting)
        |
   AI Core Layer
   ├── RAG pipeline (Qdrant vector DB)
   ├── Agent with tools (search, calculate, summarize)
   ├── Multi-modal support (vision)
   └── Conversation memory
        |
   Security Layer (input validation, content filtering)
        |
   Observability (logging, metrics, tracing)
```

---

## Requirements

### Core AI (Weeks 1-8)
- [ ] RAG over uploaded documents with citations
- [ ] Agent with 3+ tools (search knowledge, calculate, summarize)
- [ ] Multi-modal: analyze images via vision model
- [ ] Conversation history per session

### API & Deployment (Week 14-15)
- [ ] FastAPI with `/chat`, `/knowledge`, `/health`, `/metrics` endpoints
- [ ] API key authentication
- [ ] Rate limiting (60 req/min)
- [ ] Dockerfile + health check
- [ ] `docker-compose.yml` (app + Qdrant)

### Security (Week 6)
- [ ] Input validation and injection detection
- [ ] Content moderation
- [ ] Output filtering

### Observability (Week 12-13)
- [ ] Structured request logging
- [ ] Latency and error metrics
- [ ] LangSmith or Langfuse tracing

### Evaluation (Week 5)
- [ ] Ground-truth Q&A test set (20+ questions)
- [ ] Automated quality metrics
- [ ] Regression test script

---

## Suggested Structure

```
03_capstone/
├── README.md
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── core.py             # ResearchAssistant, KnowledgeBase, ToolKit
│   ├── api.py              # FastAPI app
│   ├── security.py         # Input validation, content filter
│   └── observability.py    # Logging, metrics
├── tests/
│   ├── golden_qa.json
│   └── evaluate.py
└── docs/
    └── architecture.md
```

---

## Getting Started

```bash
# 1. Install dependencies
uv sync

# 2. Configure
cp .env.example .env
# Add OPENAI_API_KEY (or AI_PROVIDER=ollama)

# 3. Run with Docker (recommended)
docker-compose up --build

# 4. Or run directly
uv run uvicorn src.api:app --reload

# 5. Run evaluation
uv run python tests/evaluate.py
```

## API Usage

```bash
# Health check
curl http://localhost:8000/health

# Add knowledge
curl -X POST http://localhost:8000/knowledge \
  -H "X-API-Key: sk-test" \
  -H "Content-Type: application/json" \
  -d '{"content": "Python was created by Guido van Rossum in 1991.", "source": "python_facts.txt"}'

# Chat
curl -X POST http://localhost:8000/chat \
  -H "X-API-Key: sk-test" \
  -H "Content-Type: application/json" \
  -d '{"message": "Who created Python?", "session_id": "user_1"}'
```

---

## Model Options

| Feature | OpenAI                   | Ollama |
|---------|--------------------------|--------|
| Chat / RAG / Tools | `gpt-5-mini`             | `llama3.1:8b` |
| Embeddings | `text-embedding-3-small` | `nomic-embed-text` |
| Vision | `gpt-5`                  | `llama3.2-vision:11b` |

```bash
# Local setup
ollama pull llama3.1:8b && ollama pull nomic-embed-text
export AI_PROVIDER=ollama
```

---

## Deliverables Checklist

### Code
- [ ] Core functionality (`core.py`)
- [ ] API layer (`api.py`) with all endpoints
- [ ] Security and observability modules
- [ ] Unit and integration tests

### Documentation
- [ ] README with setup instructions
- [ ] Architecture diagram
- [ ] API documentation (FastAPI auto-docs at `/docs`)
- [ ] Notes on design decisions

### Deployment
- [ ] Dockerfile
- [ ] docker-compose.yml (app + vector DB)
- [ ] Health check endpoint
- [ ] `.env.example` with all required variables

---

## Evaluation Rubric

| Criteria | Weight | Description |
|----------|--------|-------------|
| Functionality | 30% | Does it work? Does it solve the problem? |
| Code Quality | 20% | Clean, maintainable, well-structured |
| Production Ready | 20% | Error handling, security, deployment |
| Documentation | 15% | Clear setup, architecture, API docs |
| Innovation | 15% | Creative solutions, above and beyond |

---

## Interview Presentation Guide

1. **Problem Statement** (30 sec) — What research problem does this solve?
2. **Architecture** (1 min) — Walk through the diagram, explain each layer
3. **Demo** (2 min) — Show a multi-step query using RAG + tools
4. **Technical Deep Dive** (1 min) — Pick one challenge: security, observability, or multi-modal
5. **What I Learned** (30 sec) — Key takeaways and what you'd do differently

---

## Interview Talking Points

1. **System design** — How does a request flow from API to response?
2. **RAG vs fine-tuning** — When did you choose RAG and why?
3. **Agent architecture** — Tool-calling loop, error handling, max iterations
4. **Production hardening** — Rate limiting, retries, circuit breakers
5. **Observability** — What do you log? How do you debug issues?
6. **Cost control** — How would you reduce API costs at scale?
