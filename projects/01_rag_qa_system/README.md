# Portfolio Project #1: Secure HR Q&A Bot

**Week 6 Milestone** | Combines skills from Weeks 1-6

Build a production-ready HR assistant that answers questions from company documents, with security guardrails and quality evaluation.

---

## Requirements

### Core Features (Weeks 1-4)
- [ ] Document ingestion (TXT, MD, PDF support)
- [ ] Text chunking with overlap
- [ ] Embedding generation and storage (Qdrant)
- [ ] Semantic search retrieval with citations
- [ ] Answer generation grounded in documents

### Security (Week 6)
- [ ] Input validation — detect prompt injection attempts
- [ ] PII detection and redaction (emails, SSNs, phone numbers)
- [ ] Content moderation (OpenAI API or `granite3.1-guardian`)
- [ ] Hardened system prompt
- [ ] Output filtering — check for leaked instructions or hallucinations

### Evaluation (Week 5)
- [ ] At least 20 test Q&A pairs with expected answers
- [ ] Retrieval metrics: Precision@k, Recall@k
- [ ] Generation quality: faithfulness, relevance
- [ ] Red-team test suite (10+ adversarial prompts)

---

## Suggested Structure

```
01_rag_qa_system/
├── README.md
├── .env.example
├── src/
│   ├── __init__.py
│   ├── app.py              # Main chatbot entry point
│   ├── document_store.py   # Document loading, chunking, Qdrant
│   ├── security.py         # Input validation, PII, output filter
│   ├── evaluator.py        # Quality metrics and test runner
│   └── main.py             # CLI interface
├── data/
│   └── documents/          # HR policy documents (.txt, .md, .pdf)
├── tests/
│   ├── golden_qa.json       # Test Q&A pairs
│   └── red_team.json        # Adversarial test cases
└── notebooks/
    └── exploration.ipynb
```

---

## Getting Started

```bash
# 1. Install dependencies
uv sync

# 2. Set up environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY (or set AI_PROVIDER=ollama)

# 3. Add HR documents to data/documents/

# 4. Ingest documents
uv run python src/main.py ingest

# 5. Ask questions
uv run python src/main.py query "What is the vacation policy?"

# 6. Run evaluation
uv run python src/evaluator.py
```

---

## Model Options

| Task | OpenAI | Ollama |
|------|--------|--------|
| Chat / RAG | `gpt-4o-mini` | `llama3.1:8b` |
| Embeddings | `text-embedding-3-small` | `nomic-embed-text` |
| Safety classifier | Moderation API | `granite3.1-guardian` |

```bash
# Local setup
ollama pull llama3.1:8b && ollama pull nomic-embed-text && ollama pull granite3.1-guardian
export AI_PROVIDER=ollama
```

---

## Interview Talking Points

1. **Chunking strategy** — Why did you choose your chunk size and overlap?
2. **Security layers** — What attacks does your system defend against?
3. **PII handling** — How do you ensure sensitive data isn't leaked to the LLM?
4. **Evaluation** — How do you measure both retrieval and generation quality?
5. **Red-teaming** — What attacks did you test? Which succeeded?
6. **Scaling** — What would change at 1M documents or 1000 users/day?
