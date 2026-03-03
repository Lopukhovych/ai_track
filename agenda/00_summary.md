# Course Summary & Roadmap

**16-Week AI Engineering Curriculum — What You Learn & Build**

---

## Quick Navigation

| Week | Topic | Priority | Interview Relevance |
|------|-------|----------|---------------------|
| 1 | AI Basics & First API Call | 🔴 Must | ⭐⭐⭐ |
| 2 | Chatbot with Memory | 🔴 Must | ⭐⭐⭐ |
| 3 | Structured Output + Human-in-Loop | 🔴 Must | ⭐⭐⭐ |
| 4 | RAG Introduction | 🔴 Must | ⭐⭐⭐⭐⭐ |
| 5 | Embeddings Deep Dive | 🔴 Must | ⭐⭐⭐⭐ |
| 6 | Production RAG + Doc Processing | 🔴 Must | ⭐⭐⭐⭐⭐ |
| 7 | Evaluations + CI/CD | 🔴 Must | ⭐⭐⭐⭐ |
| 8 | Security + Red-Teaming + GDPR | 🔴 Must | ⭐⭐⭐⭐ |
| 9 | Tool Calling | 🔴 Must | ⭐⭐⭐⭐ |
| 10 | Agent Fundamentals | 🔴 Must | ⭐⭐⭐⭐ |
| 11 | Frameworks + Multi-Modal (optional) | 🟡 Recommended | ⭐⭐⭐ |
| 12 | **Data Engineering for AI** | 🟡 Recommended | ⭐⭐⭐⭐ |
| 13 | MCP & Observability | 🔴 Must | ⭐⭐⭐ |
| 14 | Production Hardening + RBAC | 🔴 Must | ⭐⭐⭐⭐ |
| 15 | Deployment + Platform Integration | 🟡 Recommended | ⭐⭐ |
| 16 | Capstone & Interview Prep | 🔴 Must | ⭐⭐⭐⭐⭐ |

**Legend:** 🔴 Must = Core skill, required for most jobs | 🟡 Recommended = Valuable, frequently asked in enterprise

---

## Learning Path Flow

```
MONTH 1: First Steps              MONTH 2: Quality & Safety
┌──────────────────────┐         ┌──────────────────────┐
│ Week 1: API Basics   │────────→│ Week 4: RAG Intro    │
│ Week 2: Chatbot      │         │ Week 5: Embeddings   │
│ Week 3: Structured   │         │ Week 6: Production   │
└──────────────────────┘         │ Week 7: Evaluations  │
         ↓                       │ Week 8: Security     │
    Foundational skills          └──────────────────────┘
                                          ↓
                                    RAG + Testing + Security

MONTH 3: Intelligence             MONTH 4: Production & Career
┌──────────────────────┐         ┌──────────────────────┐
│ Week 9: Tool Calling │────────→│ Week 13: MCP         │
│ Week 10: Agents      │         │ Week 14: Hardening   │
│ Week 11: Frameworks  │         │ Week 15: Deployment  │
│ Week 12: Data Eng.   │         │ Week 16: Capstone    │
└──────────────────────┘         └──────────────────────┘
         ↓                                ↓
    AI takes actions              Production-ready system
```

**Key dependencies:**
- Weeks 1-3 → Foundation for everything
- Week 5 (Embeddings) → Required for Week 6 (Production RAG)
- Week 9 (Tool Calling) → Required for Week 10 (Agents)
- Week 7 (Evaluations) → Security requires testing mindset

---

## What's Essential vs Optional

### 🔴 MUST-KNOW (Asked in 90% of interviews)

| Topic | Why It's Essential |
|-------|-------------------|
| **RAG** (Weeks 4-6) | The #1 most common AI engineering task. Document processing, chunking, vector search. |
| **Evaluations + CI/CD** (Week 7) | "How do you know your AI works?" plus automated testing in pipelines. |
| **Security + GDPR** (Week 8) | Prompt injection, red-teaming, and compliance are production requirements. |
| **Tool Calling** (Week 9) | Core pattern for making AI useful. |
| **Agents** (Week 10) | ReAct pattern, planning, reasoning—frequently asked. |
| **Observability** (Week 13) | Logging, tracing, metrics for production AI. |
| **Production Hardening + RBAC** (Week 14) | Rate limiting, caching, retries, secrets management—enterprise must-haves. |

### 🟡 RECOMMENDED (Frequently asked in enterprise)

| Topic | Why It's Valuable |
|-------|--------------|
| **Data Engineering** (Week 12) | SQL, data pipelines, data quality—enterprise AI engineers need this. |
| **Agent Frameworks** (Week 11) | LangGraph/CrewAI concepts. Multi-Modal as optional deep-dive. |
| **Platform Integration** (Week 15) | Slack/Teams bots, API gateways—enterprise integration patterns. |
| **Human-in-the-Loop** (Week 3) | Confidence-based escalation, approval workflows. |

### ❌ COULD SKIP (If short on time)

| Topic | Why Lower Priority |
|-------|-------------------|
| **LangGraph deep dive** | Understanding state machines matters more than the specific framework. |
| **CrewAI specifics** | Will likely be replaced by something else. Learn the pattern, not the tool. |
| **Fine-tuning hands-on** | Expensive, time-consuming, and rarely the right solution. Reading about it is enough. |
| **DALL-E image generation** | Fun but not an AI engineering interview topic. |

---

## Week-by-Week: What You'll Know & Have

### Week 1: What is AI? First API Call
**You will know:**
- How LLMs work at a high level (tokens, context, completion)
- Difference between AI/ML/LLM
- How to structure API calls

**You will have:**
- Working OpenAI API setup
- First Python script that talks to GPT
- Basic understanding of tokens and costs

**Interview readiness:** Can explain "what is an LLM" and "how does ChatGPT work"

---

### Week 2: Build a Chatbot with Memory
**You will know:**
- System/user/assistant message roles
- How conversation context works
- Memory patterns (sliding window, summarization)

**You will have:**
- `Chatbot` class with conversation history
- Multi-turn conversation handling
- Understanding of context limits

**Interview readiness:** Can explain conversation management and context windows

---

### Week 3: Better Prompts & Structured Output
**You will know:**
- Prompt engineering patterns (few-shot, chain-of-thought)
- JSON mode and response_format
- Pydantic validation for AI outputs

**You will have:**
- Reliable JSON extraction
- Validated AI responses
- Classification and extraction examples

**Interview readiness:** Can discuss prompt engineering techniques and structured output

---

### Week 4: Connect to Your Data (RAG Intro)
**You will know:**
- What RAG is and why it matters
- Basic document loading
- Simple keyword search before vectors

**You will have:**
- Document loader for your files
- Basic Q&A over your documents
- Understanding of RAG's purpose

**Interview readiness:** Can explain "what is RAG and when would you use it"

---

### Week 5: Embeddings Deep Dive
**You will know:**
- How embeddings represent meaning
- Cosine similarity and vector search
- Embedding models comparison

**You will have:**
- Embedding pipeline code
- Semantic search implementation
- Batch embedding processing

**Interview readiness:** Can explain embeddings, similarity search, and when to use them

---

### Week 6: Production RAG Architecture
**You will know:**
- Chunking strategies (size, overlap, recursive)
- Vector databases (Qdrant, Chroma, Pinecone)
- Citation and source tracking

**You will have:**
- Full RAG pipeline with vector DB
- Citaitons in generated answers
- Production-ready document ingestion

**Interview readiness:** Can design a RAG system and discuss architecture decisions

---

### Week 7: Evaluations & Quality Metrics
**You will know:**
- Retrieval metrics (precision, recall)
- Generation metrics (faithfulness, relevance)
- LLM-as-a-judge evaluation

**You will have:**
- Test dataset with expected answers
- Automated evaluation scripts
- Regression testing for AI

**Interview readiness:** Can answer "how do you measure AI quality"—a VERY common question

---

### Week 8: Security & Guardrails + Portfolio #1
**You will know:**
- Prompt injection attacks and defenses
- Content moderation approaches
- PII protection basics

**You will have:**
- Input validation layer
- Content filtering
- **Portfolio Project #1: Secure RAG Q&A System**

**Interview readiness:** Can discuss AI security risks and mitigations

---

### Week 9: Tool Calling & Function Execution
**You will know:**
- How function/tool calling works
- Tool schema design
- Execution and result handling

**You will have:**
- AI that can call functions
- Multiple tools (search, calculate, etc.)
- Error handling for tool calls

**Interview readiness:** Can implement and explain tool calling—core skill

---

### Week 10: Agent Fundamentals
**You will know:**
- ReAct pattern (Reason + Act)
- Planning and multi-step execution
- Memory for agents

**You will have:**
- Custom agent implementation
- Multi-step problem solving
- Agent with tools and memory

**Interview readiness:** Can explain agent patterns—frequently asked topic

---

### Week 11: Agent Frameworks + Multi-Modal (Optional)
**You will know:**
- When to use frameworks vs custom
- LangGraph state machines
- CrewAI multi-agent patterns
- Vision, Whisper, TTS APIs (optional deep-dive)

**You will have:**
- LangGraph workflow
- CrewAI agent team
- Multi-modal assistant example (optional)
- Framework comparison knowledge

**Interview readiness:** Familiar with popular frameworks + can use multi-modal APIs

---

### Week 12: Data Engineering for AI + Portfolio #2
**You will know:**
- SQL for AI data (JOINs, CTEs, window functions)
- ETL/ELT pipelines for documents
- Data quality checks
- Embedding version management

**You will have:**
- SQL query practice for RAG data
- Document processing pipeline
- Data quality checker
- **Portfolio Project #2: AI Agent**

**Interview readiness:** Can discuss data engineering needs for AI systems—enterprise must-have

---

### Week 13: MCP & Observability
**You will know:**
- MCP protocol basics
- Logging and tracing for AI
- Metrics collection

**You will have:**
- Simple MCP server
- AI-specific logging
- Request tracing

**Interview readiness:** Can discuss observability for AI systems (important for production roles)

---

### Week 14: Production Hardening + RBAC
**You will know:**
- Rate limiting strategies
- Caching for AI (exact and semantic)
- Retry patterns and circuit breakers
- Provider failover
- Secrets management (Key Vault, Managed Identity)
- Role-based access control for AI

**You will have:**
- Rate limiter implementation
- Response cache
- Resilient AI client with all patterns
- RBAC implementation for AI services

**Interview readiness:** Can design reliable, secure production AI systems—CRITICAL skill

---

### Week 15: Deployment + Platform Integration
**You will know:**
- Docker for AI apps
- When fine-tuning makes sense
- Fine-tuning process (conceptually)
- Chat bot integration (Slack/Teams)
- API Gateway patterns

**You will have:**
- Dockerized AI application
- Deployment scripts
- Chat bot framework code
- Understanding of fine-tuning trade-offs

**Interview readiness:** Can discuss deployment, platform integration, and when to fine-tune

---

### Week 16: Capstone & Interview Prep
**You will know:**
- System design for AI applications
- Common interview questions
- How to present your work

**You will have:**
- **Portfolio Project #3: Full-Stack AI Research Assistant**
- Complete portfolio (3 projects)
- Interview preparation materials

**Interview readiness:** READY FOR AI ENGINEERING INTERVIEWS

---

## Interview Question Preview

After this course, you can confidently answer:

1. **"Explain RAG and when you would use it"** → Week 4-6
2. **"How do you evaluate AI quality?"** → Week 7
3. **"What are the security risks with LLMs?"** → Week 8
4. **"How does tool calling work?"** → Week 9
5. **"Explain agent patterns"** → Week 10
6. **"Design a production AI system"** → Week 14
7. **"How would you reduce AI costs?"** → Week 14 (caching, model selection)
8. **"Write SQL to analyze RAG performance"** → Week 12
9. **"How do you handle secrets in production?"** → Week 14
10. **"How would you integrate AI with Slack/Teams?"** → Week 15
11. **"Walk me through a project you built"** → Your 3 portfolio projects

---

## Time Optimization

**If you only have 2 months (8 weeks), focus on:**
- Weeks 1-4 (Foundation + RAG basics)
- Week 7 (Evaluations)
- Weeks 9-10 (Tool calling + Agents)
- Week 14 (Production patterns + RBAC)

**If you have 3 months (12 weeks), add:**
- Weeks 5-6 (Deep RAG + Doc Processing)
- Week 8 (Security + Red-Teaming)
- Week 12 (Data Engineering)
- Week 16 (Interview prep)

**Full 4 months:** Complete everything for the deepest understanding.

---

## Final Deliverables

After completing this course, you will have:

| Deliverable | Description |
|-------------|-------------|
| **Portfolio Project #1** | Secure RAG Q&A System with evaluations |
| **Portfolio Project #2** | AI Agent Application with tools |
| **Portfolio Project #3** | Full-Stack Production AI App |
| **Code Repository** | All weekly code exercises |
| **Knowledge Reference** | Quick-reference guide (knowledges.md) |
| **Interview Readiness** | Practiced answers to common questions |
| **Enterprise Skills** | SQL, RBAC, secrets management, platform integration |
