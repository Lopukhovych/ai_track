# Course Summary & Roadmap

**15-Week AI Engineering Curriculum — What You Learn & Build**

---

## Quick Navigation

| Week | Topic | Duration | Priority | Interview Relevance |
|------|-------|----------|----------|---------------------|
| [1](week_01.md) | API Fundamentals, Chatbot & Structured Output | 18-24h | 🔴 Must | ⭐⭐⭐⭐ |
| [2](week_02.md) | Connect to Your Data (RAG Introduction) | 6-8h | 🔴 Must | ⭐⭐⭐⭐⭐ |
| [3](week_03.md) | Embeddings Deep Dive | 6-8h | 🔴 Must | ⭐⭐⭐⭐ |
| [4](week_04.md) | Production RAG Architecture | 8-10h | 🔴 Must | ⭐⭐⭐⭐⭐ |
| [5](week_05.md) | Evaluations & Quality Metrics | 6-8h | 🔴 Must | ⭐⭐⭐⭐ |
| [6](week_06.md) | Security & Guardrails + Portfolio #1 | 8-10h | 🔴 Must | ⭐⭐⭐⭐ |
| [7](week_07.md) | Agent Fundamentals (ReAct) | 6-8h | 🔴 Must | ⭐⭐⭐⭐ |
| [8](week_08.md) | Tool Calling & Function Execution | 6-8h | 🔴 Must | ⭐⭐⭐⭐ |
| [9](week_09.md) | Agent Frameworks — LangGraph Deep Dive & Multi-Modal | 8-12h | 🟡 Recommended | ⭐⭐⭐ |
| [10](week_10.md) | LangGraph in Practice + LangSmith & Langfuse | 8-10h | 🟡 Recommended | ⭐⭐⭐ |
| [11](week_11.md) | Data Engineering for AI + Portfolio #2 | 8-10h | 🟡 Recommended | ⭐⭐⭐⭐ |
| [12](week_12.md) | MCP & Observability | 6-8h | 🔴 Must | ⭐⭐⭐ |
| [13](week_13.md) | Production Hardening | 6-8h | 🔴 Must | ⭐⭐⭐⭐ |
| [14](week_14.md) | Deployment & Fine-Tuning | 8-10h | 🟡 Recommended | ⭐⭐ |
| [15](week_15.md) | Capstone Project & Interview Prep | 8-10h | 🔴 Must | ⭐⭐⭐⭐⭐ |

**Legend:** 🔴 Must = core skill required for most jobs | 🟡 Recommended = valuable, frequently asked in enterprise

---

## Learning Path Flow

```
MONTH 1: First Steps                    MONTH 2: Quality & Safety
┌────────────────────────────┐          ┌────────────────────────────┐
│ Week 1: APIs + Chatbot +   │─────────→│ Week 2: RAG Introduction   │
│         Structured Output  │          │ Week 3: Embeddings         │
│         (18-24h)           │          │ Week 4: Production RAG     │
└────────────────────────────┘          │ Week 5: Evaluations        │
      Foundational skills               │ Week 6: Security  ★ P1     │
                                        └────────────────────────────┘
                                              RAG + Testing + Security

MONTH 3: Intelligence                   MONTH 4: Production & Career
┌────────────────────────────┐          ┌────────────────────────────┐
│ Week 7:  Agent Fundamentals│─────────→│ Week 12: MCP & Observ.    │
│ Week 8:  Tool Calling      │          │ Week 13: Prod. Hardening   │
│ Week 9:  LangGraph + Vision│          │ Week 14: Deployment        │
│ Week 10: LangSmith/Langfuse│          │ Week 15: Capstone  ★ P3   │
│ Week 11: Data Engineering  │          └────────────────────────────┘
│          ★ P2              │                Production-ready system
└────────────────────────────┘
      AI takes actions

★ Portfolio milestones: P1 = Week 6 | P2 = Week 11 | P3 = Week 15
```

**Key dependencies:**
- Week 1 → Foundation for everything (don't skip)
- Week 3 (Embeddings) → Required for Week 4 (Production RAG)
- Week 7 (Agent Fundamentals) → Required for Week 8 (Tool Calling)
- Week 5 (Evaluations) → Testing mindset needed before Security (Week 6)

---

## What's Essential vs Optional

### 🔴 MUST-KNOW (Asked in 90% of AI engineering interviews)

| Topic | Week | Why It's Essential |
|-------|------|--------------------|
| **API basics, chatbot, structured output** | 1 | Baseline for all AI engineering work |
| **RAG** | 2-4 | The #1 most common AI engineering task |
| **Evaluations** | 5 | "How do you know your AI works?" is always asked |
| **Security & Guardrails** | 6 | Prompt injection and content safety are production requirements |
| **Agent Fundamentals (ReAct)** | 7 | Planning, reasoning, multi-step — frequently asked |
| **Tool Calling** | 8 | Core pattern for making AI do useful things |
| **MCP & Observability** | 12 | Tracing, logging, and external integrations for production |
| **Production Hardening** | 13 | Rate limiting, caching, retries, RBAC — enterprise must-haves |

### 🟡 RECOMMENDED (Frequently asked in enterprise roles)

| Topic | Week | Why It's Valuable |
|-------|------|-------------------|
| **LangGraph Deep Dive** | 9 | State machines + orchestration patterns; widely adopted |
| **LangSmith & Langfuse** | 10 | Observable, evaluatable agents are table stakes in production |
| **Data Engineering** | 11 | SQL, pipelines, data quality — enterprise AI requires this |
| **Deployment** | 14 | Docker, fine-tuning trade-offs, platform integrations (Slack/Teams) |

### COULD SKIP (If short on time)

| Topic | Why Lower Priority |
|-------|--------------------|
| Strands Agents deep dive (Week 9) | Learn the multi-agent @tool pattern — the concept matters more than the specific SDK |
| Fine-tuning hands-on (Week 14) | Expensive and rarely the right solution — reading is enough |
| Multi-Modal deep dive (Week 9) | Useful but not a core interview topic |

---

## Week-by-Week: What You'll Know & Have

### Week 1: API Fundamentals, Chatbot & Structured Output *(18-24h)*
**You will know:** How LLMs work (tokens, context, completion), conversation memory patterns, prompt engineering (zero-shot, few-shot, CoT), Pydantic validation for AI outputs, retry logic

**You will have:** Working API setup, `Chatbot` class with conversation history, reliable JSON extraction, validated AI responses

**Interview readiness:** Can explain LLMs, context windows, conversation management, and structured output

---

### Week 2: Connect to Your Data — RAG Introduction *(6-8h)*
**You will know:** What RAG is and why it matters, document loading, basic keyword search before vectors, the full RAG pipeline (retrieve → augment → generate)

**You will have:** Document loader, basic Q&A over your own files

**Interview readiness:** Can explain "what is RAG and when would you use it" — the most common AI interview question

---

### Week 3: Embeddings Deep Dive *(6-8h)*
**You will know:** How embeddings represent meaning as vectors, cosine similarity, embedding model trade-offs (`nomic-embed-text` vs `bge-m3` vs `text-embedding-3-small`)

**You will have:** Embedding pipeline, semantic search implementation, batch processing

**Interview readiness:** Can explain embeddings, semantic search, and when to use them vs keyword search

---

### Week 4: Production RAG Architecture *(8-10h)*
**You will know:** Chunking strategies (size, overlap, recursive), vector databases (Qdrant, Chroma), citation and source tracking, hybrid search (vector + keyword)

**You will have:** Full RAG pipeline with vector DB, citations in generated answers, production-ready document ingestion

**Interview readiness:** Can design and whiteboard a complete production RAG system

---

### Week 5: Evaluations & Quality Metrics *(6-8h)*
**You will know:** Retrieval metrics (precision, recall), generation metrics (faithfulness, relevance), LLM-as-judge evaluation, regression testing for AI

**You will have:** Test dataset with expected answers, automated evaluation scripts, quality dashboard

**Interview readiness:** Can answer "how do you measure AI quality" — asked in nearly every AI engineering interview

---

### Week 6: Security & Guardrails + Portfolio Project #1 *(8-10h)*
**You will know:** Prompt injection attacks and defenses, content moderation approaches, PII protection, input/output filtering

**You will have:** Input validation layer, PII protection, content filtering, red-team test suite, **Portfolio Project #1: Secure HR Q&A Bot**

**Interview readiness:** Can discuss AI security risks, mitigations, and production safety requirements

---

### Week 7: Agent Fundamentals *(6-8h)*
**You will know:** Difference between tool calling and agents, ReAct pattern (Reason + Act), agent loops with planning, error handling and retries

**You will have:** Custom ReAct agent implementation, multi-step problem solver, agent with memory

**Interview readiness:** Can implement and explain agent patterns — frequently asked in senior roles

---

### Week 8: Tool Calling & Function Execution *(6-8h)*
**You will know:** How function/tool calling works end-to-end, tool schema design (JSON Schema), parallel tool calls, chaining multiple tool calls

**You will have:** AI that calls multiple functions, tools for search/calculate/API calls, full tool-call loop with error handling

**Interview readiness:** Can implement tool calling — core skill for any AI engineering role

---

### Week 9: Agent Frameworks — LangGraph Deep Dive & Multi-Modal *(8-12h)*
**You will know:** LangGraph architecture (StateGraph, nodes, edges, reducers), all 5 workflow patterns, checkpointing, human-in-the-loop (`interrupt`), Strands Agents multi-agent (@tool sub-agents, orchestrator pattern), Vision/Audio APIs

**You will have:** LangGraph workflows (chaining, routing, orchestrator-worker, evaluator-optimizer), Strands Agents research team, multi-modal assistant (optional)

**Interview readiness:** Familiar with LangGraph patterns and multi-agent orchestration concepts

---

### Week 10: LangGraph in Practice + LangSmith & Langfuse *(8-10h)*
**You will know:** Building all LangGraph patterns as runnable code, LangSmith auto-tracing and evaluation datasets, Langfuse self-hosted observability with `@observe` and `CallbackHandler`, LLM-as-judge scoring workflows

**You will have:** 4 LangGraph patterns as code, traces visible in LangSmith, Langfuse running locally or in cloud, evaluation datasets with scored results

**Interview readiness:** Can demonstrate observable, evaluatable agent systems — differentiates production-ready candidates

---

### Week 11: Data Engineering for AI + Portfolio Project #2 *(8-10h)*
**You will know:** SQL for AI data (JOINs, CTEs, window functions), ETL/ELT pipeline patterns, data quality checks, embedding version management

**You will have:** SQL query practice for RAG analytics, document processing pipeline, data quality checker, **Portfolio Project #2: AI Agent**

**Interview readiness:** Can discuss data engineering requirements for AI — differentiates enterprise candidates

---

### Week 12: MCP & Observability *(6-8h)*
**You will know:** MCP (Model Context Protocol) for connecting AI to external tools and data sources, logging and tracing patterns, metrics collection

**You will have:** MCP server exposing tools, AI-specific logging, request tracing, basic observability dashboard

**Interview readiness:** Can discuss production observability and standardized external system integration

---

### Week 13: Production Hardening *(6-8h)*
**You will know:** Rate limiting strategies (token bucket, sliding window), caching (exact match, semantic cache), retry with exponential backoff, circuit breakers, provider failover, secrets management (Key Vault, Managed Identity), RBAC for AI services

**You will have:** Rate limiter, response cache, resilient multi-provider AI client, RBAC implementation

**Interview readiness:** Can design reliable, secure production AI systems — critical for senior and lead roles

---

### Week 14: Deployment & Fine-Tuning *(8-10h)*
**You will know:** Docker for AI apps, deployment options (serverless, containers, PaaS), when fine-tuning is worth it (and when RAG is better), fine-tuning data preparation, Slack/Teams bot integration, API gateway patterns

**You will have:** Dockerized AI application, deployment helper scripts, fine-tuning dataset, chat bot framework

**Interview readiness:** Can discuss deployment strategies, platform integration, and fine-tuning trade-offs

---

### Week 15: Capstone Project & Interview Prep *(8-10h)*
**You will know:** System design for AI applications, how to present technical projects, answers to common AI engineering interview questions

**You will have:** **Portfolio Project #3: Full-Stack AI Research Assistant**, complete 3-project portfolio, practiced interview answers

**Interview readiness:** READY FOR AI ENGINEERING INTERVIEWS

---

## Interview Questions You Can Answer After This Course

| Question | Week |
|----------|------|
| "Explain RAG and when you'd use it" | 2-4 |
| "How do you measure AI quality?" | 5 |
| "What are the security risks with LLMs?" | 6 |
| "Explain the ReAct agent pattern" | 7 |
| "How does tool calling work?" | 8 |
| "Design a production AI system" | 13 |
| "How would you reduce AI API costs?" | 13 (caching, model selection) |
| "Write SQL to analyze RAG performance" | 11 |
| "How do you handle secrets in production?" | 13 |
| "How do you trace and observe LLM calls?" | 10, 12 |
| "Walk me through a project you built" | Your 3 portfolio projects |

---

## Time Optimization

**If you only have 2 months (8 weeks), focus on:**
- Weeks 1-5 (Foundation + RAG + Evaluations)
- Weeks 7-8 (Agents + Tool Calling)
- Week 13 (Production patterns)

**If you have 3 months (11 weeks), add:**
- Week 6 (Security + Portfolio #1)
- Weeks 9-10 (LangGraph + LangSmith/Langfuse)
- Week 11 (Data Engineering + Portfolio #2)

**Full 4 months — all 15 weeks** for the deepest understanding and all 3 portfolio projects.

---

## Final Deliverables

| Deliverable | Week | Description |
|-------------|------|-------------|
| **Portfolio #1** | 6 | Secure HR Q&A Bot — RAG + security guardrails + evaluations (`projects/01_rag_qa_system/`) |
| **Portfolio #2** | 11 | AI Agent — ReAct reasoning, tools, step logging, data pipeline (`projects/02_ai_agent/`) |
| **Portfolio #3** | 15 | Full-Stack AI Research Assistant — FastAPI + RAG + agents + Docker (`projects/03_capstone/`) |
| **Code Exercises** | 0-15 | All weekly lab notebooks (`labs/week_XX_*.ipynb`) |
| **Knowledge Reference** | — | `knowledges.md` quick-reference cheat sheet |
| **Interview Readiness** | 15 | Practiced answers, system design templates |
