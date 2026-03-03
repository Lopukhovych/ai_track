# Portfolio Project #1: RAG Q&A System

**Weeks 4-8 Milestone Project**

Build a production-ready Q&A system that answers questions from your own documents.

---

## Requirements

### Core Features
- [ ] Document ingestion (PDF, TXT, MD support)
- [ ] Text chunking with overlap
- [ ] Embedding generation and storage
- [ ] Semantic search retrieval
- [ ] Answer generation with citations

### Production Quality
- [ ] Input validation
- [ ] Error handling
- [ ] Basic prompt injection protection
- [ ] Response caching

### Evaluation
- [ ] At least 20 test questions with expected answers
- [ ] Retrieval metrics: Precision@k, Recall@k
- [ ] Generation quality checks

---

## Suggested Structure

```
01_rag_qa_system/
├── README.md
├── requirements.txt
├── .env
├── src/
│   ├── __init__.py
│   ├── ingestion.py      # Document loading & chunking
│   ├── embeddings.py     # Embedding generation
│   ├── retrieval.py      # Vector search
│   ├── generation.py     # Answer generation
│   └── main.py           # CLI or API entry point
├── data/
│   └── documents/        # Your source documents
├── tests/
│   ├── test_retrieval.py
│   └── golden_qa.json    # Test questions & answers
└── notebooks/
    └── exploration.ipynb
```

---

## Getting Started

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 4. Add documents to data/documents/

# 5. Run ingestion
python src/main.py ingest

# 6. Ask questions
python src/main.py query "What is...?"
```

---

## Interview Talking Points

When presenting this project, be ready to discuss:

1. **Chunking strategy** - Why did you choose your chunk size/overlap?
2. **Embedding model** - Why text-embedding-3-small vs large?
3. **Retrieval** - How many chunks do you retrieve? Why?
4. **Hallucination prevention** - How do you ensure grounded answers?
5. **Evaluation** - How do you measure quality?
6. **Scaling** - What would change at 1M documents?
