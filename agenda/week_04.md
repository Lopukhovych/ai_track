# Week 4: Production RAG Architecture

**Month:** 2 (Quality & Safety) | **Duration:** 8-10 hours

---

## Overview

Last week you learned embeddings. This week you'll build a **production-grade RAG system** using:
- **Chunking**: Split large documents into searchable pieces
- **Vector Database**: Store and search millions of embeddings (Qdrant)
- **Citations**: Show users where answers come from

**⚠️ Study Tip:** This is a dense week. Consider:
- Day 1: Chunking + Vector DB setup (Tasks 1-3)
- Day 2: Citations + Complete integration (Tasks 4-6)

---

## Learning Objectives

By the end of this week, you will:
- Understand why chunking matters and how to do it well
- Set up and use Qdrant vector database
- Store and retrieve documents efficiently
- Build RAG with proper citations
- Handle large document collections

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| RAG chat / generation | `gpt-5-mini` | `llama3.1:8b` |
| Embeddings | `text-embedding-3-small` | `nomic-embed-text` |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

```python
from scripts.model_config import get_client, CHAT_MODEL, EMBED_MODEL
```

> Note: Qdrant is provider-agnostic — it stores vectors regardless of which model generates them.

---

## Theory (2 hours)

### 1. The Chunking Problem (30 min)

**Problem:** Documents are too long for embedding models (8k token limit) and LLM context.

**Solution:** Split documents into chunks.

```
┌─────────────────────────────────┐
│      Full Document (50 pages)   │
└─────────────────────────────────┘
                ↓ chunk
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Chunk 1 │ │ Chunk 2 │ │ Chunk 3 │  ... (50 chunks)
│ 500 tok │ │ 500 tok │ │ 500 tok │
└─────────┘ └─────────┘ └─────────┘
                ↓ embed each
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Vector1 │ │ Vector2 │ │ Vector3 │  ...
└─────────┘ └─────────┘ └─────────┘
```

**Chunking parameters:**
| Parameter | Good Default | Description |
|-----------|--------------|-------------|
| `chunk_size` | 500-1000 | Characters per chunk |
| `chunk_overlap` | 100-200 | Overlap between chunks |

**Why overlap?** Prevents cutting ideas in the middle.

### 2. Vector Databases (30 min)

**Why not just use a Python list?**

| Python List | Vector Database |
|-------------|-----------------|
| Slow for >10k docs | Fast at any scale |
| No persistence | Data survives restarts |
| No indexing | Optimized search algorithms |
| Memory-only | Disk-based storage |

**Popular vector databases:**
- **Qdrant** — Easy, Python-first (we'll use this)
- **Pinecone** — Managed service, easy scaling
- **Chroma** — Lightweight, good for prototypes
- **Weaviate** — GraphQL API, hybrid search

### 3. Qdrant Basics (30 min)

```python
# Qdrant concepts
Collection = "Table" (holds vectors)
Point = "Row" (one vector + metadata)
Payload = "Columns" (metadata like filename, page number)

# Example point
{
    "id": 1,
    "vector": [0.23, 0.45, ...],  # embedding
    "payload": {
        "text": "Our vacation policy...",
        "filename": "hr-policy.pdf",
        "page": 12
    }
}
```

### 4. Citation Strategy (30 min)

**Users need to verify AI answers.** Always cite sources!

```
Answer: Employees get 20 days of PTO after 2 years.
Sources:
- hr-policy.pdf, page 12 (relevance: 0.92)
- employee-handbook.pdf, page 45 (relevance: 0.87)
```

### 5. Document Processing (30 min)

**Real documents aren't plain text.** You need to extract text from:

| Format | Tool | Notes |
|--------|------|-------|
| **PDF** | `pypdf`, `pdfplumber` | Handle tables, images |
| **HTML** | `beautifulsoup4` | Strip tags, extract content |
| **Word** | `python-docx` | Preserve formatting info |
| **OCR** | `pytesseract`, Azure AI | For scanned documents |

```python
# PDF extraction example
from pypdf import PdfReader

def extract_pdf(path: str) -> list[dict]:
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        pages.append({
            "text": page.extract_text(),
            "page": i + 1,
            "source": path
        })
    return pages
```

**Document processing pipeline:**
```
Raw Files → [Parser] → [Text Extraction] → [Chunking] → [Embedding] → Vector DB
    PDF         ↓            ↓
    HTML    pypdf       Clean text
    DOCX    bs4         Remove noise
```

### 6. Re-ranking (30 min)

**Problem:** Vector search finds *similar*, not *best* results.

**Solution:** Re-rank retrieved results for relevance.

```
Query → Vector Search (fast, top 20) → Re-ranker (accurate, top 3) → LLM
```

**Re-ranking methods:**
| Method | Speed | Quality | Cost |
|--------|-------|---------|------|
| Cross-encoder | Slow | Best | High compute |
| Cohere Rerank API | Fast | Excellent | API cost |
| LLM-based scoring | Slow | Very good | API cost |
| BM25 fusion | Fast | Good | Free |

```python
# Simple LLM-based re-ranking
def rerank_with_llm(query: str, results: list[str], top_k: int = 3) -> list[str]:
    prompt = f"""Score each result 1-10 for relevance to: "{query}"
    
Results:
{chr(10).join(f'{i+1}. {r}' for i, r in enumerate(results))}

Return JSON: {{"scores": [score1, score2, ...]}}"""
    
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    scores = json.loads(response.choices[0].message.content)["scores"]
    ranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
    return [r for r, s in ranked[:top_k]]
```

### 7. Hybrid Search (30 min)

**Combine keyword search + semantic search** for better results.

| Search Type | Good For | Weakness |
|-------------|----------|----------|
| **Keyword (BM25)** | Exact terms, names, codes | Misses synonyms |
| **Semantic (Vector)** | Meaning, concepts | Misses exact matches |
| **Hybrid** | Both! | More complex |

```python
from rank_bm25 import BM25Okapi

def hybrid_search(query: str, documents: list[str], vector_results: list, alpha=0.5):
    # Keyword search
    tokenized = [doc.lower().split() for doc in documents]
    bm25 = BM25Okapi(tokenized)
    keyword_scores = bm25.get_scores(query.lower().split())
    
    # Combine scores: alpha * semantic + (1-alpha) * keyword
    # ... normalize and merge
```

**When to use hybrid:**
- Product search (SKUs + descriptions)
- Legal documents (case numbers + concepts)
- Technical docs (error codes + explanations)

---

## Hands-On Practice (4-6 hours)

### Task 1: Install Qdrant (15 min)

```bash
pip install qdrant-client
```

For local development, use in-memory mode (no server needed).
For production, use Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Task 2: Text Chunking (45 min)

```python
# chunker.py
from typing import List
from dataclasses import dataclass

@dataclass
class Chunk:
    text: str
    start_index: int
    end_index: int
    metadata: dict = None

def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Chunk]:
    """Split text into overlapping chunks."""
    
    if len(text) <= chunk_size:
        return [Chunk(text=text, start_index=0, end_index=len(text))]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to end at a sentence boundary
        if end < len(text):
            # Look for period, newline in last 20% of chunk
            lookback = int(chunk_size * 0.2)
            for i in range(end, end - lookback, -1):
                if text[i] in '.!?\n':
                    end = i + 1
                    break
        
        chunk_text_str = text[start:end].strip()
        if chunk_text_str:
            chunks.append(Chunk(
                text=chunk_text_str,
                start_index=start,
                end_index=end
            ))
        
        start = end - chunk_overlap
    
    return chunks

# Test
if __name__ == "__main__":
    test_text = """
    Python is a high-level programming language known for its readability. 
    It was created by Guido van Rossum and first released in 1991. Python supports 
    multiple programming paradigms, including procedural, object-oriented, and functional.
    
    The language emphasizes code readability with its notable use of significant indentation. 
    Its language constructs aim to help programmers write clear, logical code.
    """
    
    chunks = chunk_text(test_text, chunk_size=200, chunk_overlap=50)
    
    print(f"Original length: {len(test_text)} chars")
    print(f"Number of chunks: {len(chunks)}\n")
    
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: '{chunk.text[:60]}...'\n")
```

### Task 3: Qdrant Vector Store (60 min)

```python
# qdrant_store.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
import uuid

load_dotenv()

class VectorStore:
    """Simple vector store using Qdrant."""
    
    def __init__(self, collection_name: str = "documents"):
        # Use in-memory Qdrant (no server needed)
        self.client = QdrantClient(":memory:")
        self.openai = OpenAI()
        self.collection_name = collection_name
        
        # Create collection
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1536,  # OpenAI embedding size
                distance=Distance.COSINE
            )
        )
        print(f"Created collection: {collection_name}")
    
    def _get_embedding(self, text: str) -> List[float]:
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def add_documents(self, documents: List[dict]):
        """Add multiple documents efficiently."""
        points = []
        
        # Get all embeddings in batch
        texts = [doc["text"] for doc in documents]
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        
        for i, doc in enumerate(documents):
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=response.data[i].embedding,
                payload=doc
            ))
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        print(f"Added {len(documents)} documents")
    
    def search(self, query: str, top_k: int = 3) -> List[dict]:
        """Search for similar documents."""
        query_embedding = self._get_embedding(query)
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k
        )
        
        return [
            {
                "text": hit.payload["text"],
                "score": hit.score,
                **{k: v for k, v in hit.payload.items() if k != "text"}
            }
            for hit in results
        ]

# Test
if __name__ == "__main__":
    store = VectorStore()
    
    docs = [
        {"text": "Python is great for machine learning", "source": "article1"},
        {"text": "JavaScript is used for web development", "source": "article2"},
        {"text": "TensorFlow is a popular ML framework", "source": "article3"},
    ]
    
    store.add_documents(docs)
    
    results = store.search("deep learning frameworks")
    print("\nSearch: 'deep learning frameworks'")
    for r in results:
        print(f"  [{r['score']:.4f}] {r['text']}")
```

### Task 4: Full RAG Pipeline (60 min)

```python
# production_rag.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from typing import List
from dataclasses import dataclass
import uuid

load_dotenv()

@dataclass
class SearchResult:
    text: str
    score: float
    filename: str
    chunk_index: int

@dataclass
class RAGResponse:
    answer: str
    sources: List[SearchResult]

class ProductionRAG:
    """Production-ready RAG system."""
    
    def __init__(self, collection_name: str = "rag_docs"):
        self.qdrant = QdrantClient(":memory:")
        self.openai = OpenAI()
        self.collection = collection_name
        
        self.qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Simple chunking."""
        chunks = []
        for i in range(0, len(text), chunk_size - 100):
            chunks.append(text[i:i + chunk_size])
        return chunks
    
    def index_folder(self, folder: str, chunk_size: int = 500):
        """Index all text files in a folder."""
        folder_path = Path(folder)
        all_points = []
        
        for file in folder_path.glob("*.txt"):
            content = file.read_text()
            chunks = self._chunk_text(content, chunk_size)
            
            # Get embeddings for all chunks
            response = self.openai.embeddings.create(
                model="text-embedding-3-small",
                input=chunks
            )
            
            for i, chunk in enumerate(chunks):
                all_points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=response.data[i].embedding,
                    payload={
                        "text": chunk,
                        "filename": file.name,
                        "chunk_index": i
                    }
                ))
            
            print(f"Indexed: {file.name} ({len(chunks)} chunks)")
        
        self.qdrant.upsert(collection_name=self.collection, points=all_points)
    
    def ask(self, question: str, top_k: int = 3) -> RAGResponse:
        """Ask a question, get answer with citations."""
        
        # Search
        query_emb = self.openai.embeddings.create(
            model="text-embedding-3-small", input=question
        ).data[0].embedding
        
        results = self.qdrant.search(
            collection_name=self.collection,
            query_vector=query_emb,
            limit=top_k
        )
        
        search_results = [
            SearchResult(
                text=hit.payload["text"],
                score=hit.score,
                filename=hit.payload["filename"],
                chunk_index=hit.payload["chunk_index"]
            )
            for hit in results
        ]
        
        # Build context
        context = "\n\n".join([
            f"[{r.filename}]: {r.text}" for r in search_results
        ])
        
        # Generate answer
        response = self.openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "Answer based on context. Cite sources."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        )
        
        return RAGResponse(
            answer=response.choices[0].message.content,
            sources=search_results
        )

# Test
if __name__ == "__main__":
    rag = ProductionRAG()
    rag.index_folder("docs")
    
    response = rag.ask("What's the vacation policy?")
    print(f"A: {response.answer}")
    print(f"\nSources: {[s.filename for s in response.sources]}")
```

### Task 5: PDF Document Processing (45 min)

```python
# pdf_processing.py
from pypdf import PdfReader
from typing import List
from dataclasses import dataclass
import re

@dataclass
class DocumentChunk:
    text: str
    source: str
    page: int
    chunk_index: int

def extract_pdf(path: str) -> List[dict]:
    """Extract text from PDF with page tracking."""
    reader = PdfReader(path)
    pages = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        # Clean up common PDF extraction issues
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        if text:
            pages.append({
                "text": text,
                "page": i + 1,
                "source": path
            })
    
    return pages

def chunk_pdf(path: str, chunk_size: int = 500, overlap: int = 100) -> List[DocumentChunk]:
    """Extract and chunk a PDF file."""
    pages = extract_pdf(path)
    chunks = []
    chunk_idx = 0
    
    for page_data in pages:
        text = page_data["text"]
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append(DocumentChunk(
                    text=chunk_text,
                    source=path,
                    page=page_data["page"],
                    chunk_index=chunk_idx
                ))
                chunk_idx += 1
            
            start = end - overlap
    
    return chunks

# Test
if __name__ == "__main__":
    # pip install pypdf
    chunks = chunk_pdf("sample.pdf")
    print(f"Extracted {len(chunks)} chunks")
    for chunk in chunks[:3]:
        print(f"  Page {chunk.page}: {chunk.text[:80]}...")
```

### Task 6: Re-ranking Implementation (45 min)

```python
# reranking.py
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

def rerank_results(
    query: str, 
    results: list[dict], 
    top_k: int = 3
) -> list[dict]:
    """Re-rank search results using LLM scoring."""
    
    # Format results for scoring
    results_text = "\n".join([
        f"{i+1}. {r['text'][:300]}..." 
        for i, r in enumerate(results)
    ])
    
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{
            "role": "user",
            "content": f"""Score each search result 1-10 for relevance to the query.

Query: "{query}"

Results:
{results_text}

Return JSON: {{"scores": [score1, score2, ...], "reasoning": ["reason1", ...]}}"""
        }],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    scores = data["scores"]
    
    # Add scores and sort
    for i, result in enumerate(results):
        result["rerank_score"] = scores[i] if i < len(scores) else 0
    
    ranked = sorted(results, key=lambda x: x["rerank_score"], reverse=True)
    return ranked[:top_k]

# Test with mock results
if __name__ == "__main__":
    query = "How to reset password"
    results = [
        {"text": "Our company picnic will be held on Saturday.", "score": 0.85},
        {"text": "To reset your password, go to Settings > Security > Reset Password.", "score": 0.82},
        {"text": "Password requirements: 8 characters, 1 uppercase, 1 number.", "score": 0.80},
    ]
    
    reranked = rerank_results(query, results)
    print(f"Query: {query}\n")
    for r in reranked:
        print(f"Score {r['rerank_score']}/10: {r['text'][:60]}...")
```

---

## 🎯 Optional Challenges

*Push your RAG skills further with these advanced exercises.*

### Challenge 1: Metadata Filtering
Add metadata to your documents (category, date, author). Implement filtered search:
```python
# Search only in "engineering" documents from 2024
results = search(query, filters={"category": "engineering", "year": 2024})
```

### Challenge 2: Document Updates
What happens when a document is updated? Build a system that:
1. Detects when a document changed
2. Removes old chunks from vector DB
3. Re-indexes new version
4. Handles versioning (optionally keep old versions)

### Challenge 3: Embedding Cache
Embeddings are expensive. Build a caching layer:
```python
def get_embedding_cached(text: str) -> list:
    cache_key = hash(text)
    if cache_key in cache:
        return cache[cache_key]
    embedding = get_embedding(text)
    cache[cache_key] = embedding
    return embedding
```
Measure: How much do you save? (track API calls before/after)

### Challenge 4: RAG Evaluation Harness
Create 20 question-answer pairs for your documents. Build an automatic evaluator:
```python
test_cases = [
    {"question": "What is PTO?", "expected": "15 days", "source": "hr_policy.txt"},
    ...
]

for test in test_cases:
    result = ask(test["question"])
    # Check: Is answer correct? Is source right?
```

### Challenge 5: Hybrid Search Implementation
Combine BM25 (keyword) with semantic search. Implement this fusion:
```python
def hybrid_search(query: str, alpha: float = 0.5):
    keyword_results = bm25_search(query)  # Scores 0-10
    semantic_results = vector_search(query)  # Scores 0-1
    
    # Normalize and combine with alpha weighting
    # Return fused ranking
```

### Challenge 6: Multi-Modal RAG
Add images to your document store. Use GPT-4V to describe images, embed the descriptions, and include them in search results.

---

## Knowledge Checklist

- [ ] I understand why chunking is necessary
- [ ] I can split documents into overlapping chunks
- [ ] I can set up Qdrant (in-memory and persistent)
- [ ] I can store and search embeddings efficiently
- [ ] I can build RAG with proper citations
- [ ] I can extract text from PDFs and other documents
- [ ] I understand re-ranking and when to use it
- [ ] I know the difference between keyword, semantic, and hybrid search

---

## Deliverables

1. `chunker.py` — Text chunking with overlap
2. `qdrant_store.py` — Basic Qdrant operations
3. `production_rag.py` — Full RAG pipeline
4. `pdf_processing.py` — PDF extraction and chunking
5. `reranking.py` — LLM-based re-ranking

---

## What's Next?

Next week you'll learn to **evaluate** your RAG system:
- How do you know if answers are correct?
- How do you measure quality?

---

## Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Chunking Strategies](https://www.pinecone.io/learn/chunking-strategies/)
