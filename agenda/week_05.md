# Week 5: Embeddings Deep Dive

**Month:** 2 (Quality & Safety) | **Duration:** 6-8 hours

---

## Overview

Last week's keyword search was limited — "vacation" wouldn't find "time off". This week you'll learn **embeddings**: a way to convert text into numbers that capture *meaning*. This is how modern AI search actually works.

---

## Learning Objectives

By the end of this week, you will:
- Understand what embeddings are and why they matter
- Generate embeddings using OpenAI's API
- Calculate similarity between texts
- Build semantic search that understands meaning
- Compare different embedding models

---

## Theory (2 hours)

### 1. What Are Embeddings? (30 min)

**Embeddings convert text → numbers (vectors).**

```
"I love pizza" → [0.23, -0.45, 0.12, ..., 0.67]  # 1536 numbers
"Pizza is great" → [0.21, -0.44, 0.11, ..., 0.65]  # Similar numbers!
"I hate pizza" → [0.23, -0.45, 0.12, ..., -0.32]  # Different at the end
```

**Key insight:** Similar meanings → similar numbers

```
dog ≈ puppy ≈ canine  (close vectors)
dog ≠ pizza ≠ vacation (far apart)
```

### 2. How AI Search Actually Works (30 min)

```
OLD WAY (Keyword Search)
━━━━━━━━━━━━━━━━━━━━━━━━
"vacation policy" → only finds docs with word "vacation"
Misses: "time off", "PTO", "paid leave"

NEW WAY (Semantic Search)
━━━━━━━━━━━━━━━━━━━━━━━━
"vacation policy" → [0.23, 0.45, ...] (meaning vector)
                 ↓
Compare with all document vectors
                 ↓
Finds: "PTO policy", "time off rules", "leave guidelines"
```

### 3. Vector Similarity (30 min)

**How do we measure "similar"?**

**Cosine Similarity:** Angle between vectors
- 1.0 = identical meaning
- 0.0 = unrelated
- -1.0 = opposite meaning

```
"I love dogs"   vs  "I adore puppies"    → 0.95 (very similar!)
"I love dogs"   vs  "The weather is nice" → 0.15 (unrelated)
"I love dogs"   vs  "I hate dogs"        → 0.45 (related but different)
```

### 4. Embedding Models (30 min)

| Model | Dimensions | Best For |
|-------|------------|----------|
| `text-embedding-3-small` | 1536 | General use, cheaper |
| `text-embedding-3-large` | 3072 | Higher accuracy |
| `text-embedding-ada-002` | 1536 | Legacy, still works |

**Cost comparison:**
- `3-small`: $0.02 per 1M tokens
- `3-large`: $0.13 per 1M tokens
- Rule: Start with small, upgrade if needed

---

## Hands-On Practice (4-6 hours)

### Task 1: Generate Your First Embedding (30 min)

```python
# first_embedding.py
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def get_embedding(text: str) -> list[float]:
    """Convert text to an embedding vector."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# Test
text = "I love programming in Python"
embedding = get_embedding(text)

print(f"Text: {text}")
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 5 values: {embedding[:5]}")
print(f"Last 5 values: {embedding[-5:]}")
```

### Task 2: Calculate Similarity (45 min)

**Install numpy first (needed for vector math):**
```bash
pip install numpy
```

```python
# similarity.py
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np

load_dotenv()
client = OpenAI()

def get_embedding(text: str) -> list[float]:
    """Get embedding for text."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Test with different texts
texts = [
    "I love programming in Python",
    "Python is my favorite language for coding",
    "I enjoy writing code in Python",
    "The weather is beautiful today",
    "I hate programming"
]

# Get embedding for the first text
base_text = texts[0]
base_embedding = get_embedding(base_text)

print(f"Comparing everything to: '{base_text}'\n")

for text in texts[1:]:
    embedding = get_embedding(text)
    similarity = cosine_similarity(base_embedding, embedding)
    print(f"Similarity: {similarity:.4f} | '{text}'")
```

### Task 3: Semantic Search (60 min)

```python
# semantic_search.py
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
from typing import List
from dataclasses import dataclass

load_dotenv()
client = OpenAI()

@dataclass
class Document:
    content: str
    embedding: List[float] = None

def get_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(a: List[float], b: List[float]) -> float:
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class SemanticSearch:
    """A simple semantic search engine."""
    
    def __init__(self):
        self.documents: List[Document] = []
    
    def add_document(self, content: str):
        """Add a document and compute its embedding."""
        doc = Document(
            content=content,
            embedding=get_embedding(content)
        )
        self.documents.append(doc)
        print(f"Added: {content[:50]}...")
    
    def search(self, query: str, top_k: int = 3) -> List[tuple]:
        """Find most similar documents to query."""
        query_embedding = get_embedding(query)
        
        # Calculate similarity to all documents
        results = []
        for doc in self.documents:
            sim = cosine_similarity(query_embedding, doc.embedding)
            results.append((doc.content, sim))
        
        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

# Test
if __name__ == "__main__":
    search = SemanticSearch()
    
    # Add documents
    documents = [
        "Employees receive 20 days of paid time off per year",
        "The company 401k plan matches up to 4% of salary",
        "Remote work is allowed on Mondays and Fridays",
        "Health insurance covers medical, dental, and vision",
        "Annual performance reviews happen in December",
        "The office is located in downtown San Francisco",
        "New employees receive a $500 equipment allowance"
    ]
    
    for doc in documents:
        search.add_document(doc)
    
    # Search
    queries = [
        "vacation policy",  # Should find PTO
        "working from home",  # Should find remote work
        "retirement benefits"  # Should find 401k
    ]
    
    for query in queries:
        print(f"\n=== Query: '{query}' ===")
        results = search.search(query, top_k=2)
        for content, score in results:
            print(f"  [{score:.4f}] {content}")
```

### Task 4: Batch Embeddings (45 min)

```python
# batch_embeddings.py
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
import time

load_dotenv()
client = OpenAI()

def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Get embeddings for multiple texts in one API call."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [item.embedding for item in response.data]

# Compare single vs batch
documents = [
    "Python is a programming language",
    "Machine learning uses algorithms",
    "Neural networks are inspired by brains",
    "Data science analyzes large datasets",
    "Natural language processing handles text"
]

# Batch method (faster!)
print("Batch method:")
start = time.time()
embeddings = get_embeddings_batch(documents)
batch_time = time.time() - start
print(f"  Time: {batch_time:.3f}s for {len(documents)} documents")
print(f"  Got {len(embeddings)} embeddings of dimension {len(embeddings[0])}")

# Single method (slower)
print("\nSingle method:")
start = time.time()
single_embeddings = []
for doc in documents:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=doc
    )
    single_embeddings.append(response.data[0].embedding)
single_time = time.time() - start
print(f"  Time: {single_time:.3f}s for {len(documents)} documents")

print(f"\nBatch is {single_time/batch_time:.1f}x faster!")
```

### Task 5: Upgrade Your RAG (60 min)

Replace keyword search with semantic search:

```python
# semantic_rag.py
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
from typing import List
from dataclasses import dataclass

load_dotenv()
client = OpenAI()

@dataclass
class Document:
    content: str
    filename: str
    embedding: List[float]

def get_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(a: List[float], b: List[float]) -> float:
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

class SemanticRAG:
    """RAG with semantic search instead of keyword search."""
    
    def __init__(self, docs_folder: str):
        self.documents = []
        self._load_documents(docs_folder)
    
    def _load_documents(self, folder: str):
        """Load and embed all documents."""
        folder_path = Path(folder)
        
        for file in folder_path.glob("*.txt"):
            content = file.read_text()
            embedding = get_embedding(content)
            
            doc = Document(
                content=content,
                filename=file.name,
                embedding=embedding
            )
            self.documents.append(doc)
            print(f"Embedded: {file.name}")
    
    def search(self, query: str, top_k: int = 2) -> List[Document]:
        """Find most relevant documents using semantic search."""
        query_embedding = get_embedding(query)
        
        # Calculate similarities
        scored = []
        for doc in self.documents:
            score = cosine_similarity(query_embedding, doc.embedding)
            scored.append((doc, score))
        
        # Sort by similarity
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [doc for doc, score in scored[:top_k]]
    
    def ask(self, question: str) -> str:
        """Ask a question, get answer from documents."""
        
        # Semantic search
        relevant_docs = self.search(question, top_k=2)
        
        # Build context
        context = "\n\n".join([
            f"[{doc.filename}]:\n{doc.content}"
            for doc in relevant_docs
        ])
        
        # Generate answer
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Answer based on the provided context only."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
            ]
        )
        
        return response.choices[0].message.content

# Test
if __name__ == "__main__":
    rag = SemanticRAG("docs")
    
    # These queries now work with synonyms!
    questions = [
        "What's the PTO policy?",  # Finds "vacation" docs
        "Can I work remotely?",     # Finds "work from home" docs
        "What retirement plans exist?"  # Finds "401k" docs
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        answer = rag.ask(q)
        print(f"A: {answer}")
```

### Task 6: Compare Models (45 min)

```python
# compare_models.py
from openai import OpenAI
from dotenv import load_dotenv
import numpy as np
import time

load_dotenv()
client = OpenAI()

def get_embedding(text: str, model: str) -> list:
    response = client.embeddings.create(model=model, input=text)
    return response.data[0].embedding

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Test pairs
test_pairs = [
    ("I love pizza", "Pizza is my favorite food"),
    ("I love pizza", "I hate pizza"),
    ("The stock market crashed", "Financial markets declined sharply"),
    ("A cat sleeps on the couch", "The weather is sunny today")
]

models = ["text-embedding-3-small", "text-embedding-3-large"]

for model in models:
    print(f"\n{'='*50}")
    print(f"Model: {model}")
    print("="*50)
    
    start = time.time()
    
    for text1, text2 in test_pairs:
        emb1 = get_embedding(text1, model)
        emb2 = get_embedding(text2, model)
        sim = cosine_similarity(emb1, emb2)
        print(f"{sim:.4f} | '{text1}' vs '{text2}'")
    
    elapsed = time.time() - start
    print(f"\nTime: {elapsed:.2f}s | Dimensions: {len(emb1)}")
```

---

## 🎯 Optional Challenges

*Embeddings are the foundation of modern AI search. Master them.*

### Challenge 1: Similarity Threshold Explorer
Build a tool to find the optimal similarity threshold:
```python
# Test different thresholds on your document set
# At what threshold do you get best precision/recall?
for threshold in [0.6, 0.7, 0.8, 0.9]:
    results = search(query, threshold=threshold)
    # Measure: Are results relevant? Are good results missed?
```

### Challenge 2: Embedding Visualization
Reduce embedding dimensions and visualize:
```python
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

# Embed 50 different sentences
# Use TSNE to reduce to 2D
# Plot and color by category
# Do similar meanings cluster together?
```

### Challenge 3: Multi-Language Embeddings
Test if embeddings work across languages:
```python
# Does "I love programming" (English) 
# match "Me encanta programar" (Spanish)?
eng_emb = get_embedding("I love programming")
sp_emb = get_embedding("Me encanta programar")
print(cosine_similarity(eng_emb, sp_emb))  # How close?
```

### Challenge 4: Embedding Cache with TTL
Build a production cache:
```python
class EmbeddingCache:
    def __init__(self, ttl_hours=24):
        self.cache = {}
        self.timestamps = {}
    
    def get(self, text):
        # Return cached if exists and not expired
        # Otherwise compute, cache, and return
```

### Challenge 5: Embedding Quality Test Suite
Create automated tests for your embedding setup:
```python
test_cases = [
    ("king", "queen", "high"),  # Should be high similarity
    ("dog", "cat", "high"),
    ("computer", "banana", "low"),  # Should be low
]
# Run all tests, report pass/fail
```

---

## Knowledge Checklist

- [ ] I understand that embeddings convert text to numbers
- [ ] I can generate embeddings using OpenAI's API
- [ ] I can calculate cosine similarity between vectors
- [ ] I can build semantic search with embeddings
- [ ] I understand the difference between small and large models
- [ ] I upgraded my RAG to use semantic search

---

## Deliverables

1. `first_embedding.py` — Basic embedding generation
2. `similarity.py` — Similarity calculations
3. `semantic_search.py` — Search by meaning
4. `batch_embeddings.py` — Efficient batch processing
5. `semantic_rag.py` — RAG with semantic search
6. `compare_models.py` — Model comparison

---

## What's Next?

Next week you'll build a proper RAG system with:
- Document chunking (splitting large docs)
- Vector databases (Qdrant) for fast search
- Better context construction

---

## Resources

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [Understanding Embeddings](https://www.youtube.com/watch?v=5MaWmXwxFNQ)
- [Cosine Similarity Explained](https://www.pinecone.io/learn/cosine-similarity/)
