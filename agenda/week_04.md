# Week 4: Connect to Your Data (Introduction to RAG)

**Month:** 1 (First Steps) | **Duration:** 6-8 hours

---

## Overview

Your chatbot is smart, but it only knows things from its training data. This week you'll teach it to answer questions from **your own documents**. This technique is called **RAG (Retrieval-Augmented Generation)** — the most important concept in AI engineering.

**Milestone:** By the end of this week, your chatbot can answer questions about your own files!

---

## Learning Objectives

By the end of this week, you will:
- Understand why RAG is essential for AI applications
- Load and read text files in Python
- Search documents for relevant information
- Combine search results with AI to answer questions
- Build a simple document Q&A system

---

## Theory (2 hours)

### 1. Why Can't AI Just Read My Files? (30 min)

**The problem:**
- LLMs are trained on public internet data (cutoff date)
- They don't know about YOUR documents, database, emails
- They can't access files on your computer

**The solution: RAG (Retrieval-Augmented Generation)**

```
1. User asks: "What's our vacation policy?"
              ↓
2. RETRIEVE: Search your documents for relevant text
              ↓
3. AUGMENT: Add found text to the prompt
              ↓
4. GENERATE: LLM answers using the context
```

**Simple example:**
```python
# Without RAG
"What's our vacation policy?" → "I don't have that information"

# With RAG
context = search_documents("vacation policy")  
prompt = f"Based on this: {context}\n\nAnswer: What's our vacation policy?"
# → "According to the employee handbook, you get 20 days PTO..."
```

### 2. The RAG Pipeline (Simple Version) (30 min)

```
┌─────────────────────────────────────────────────┐
│              Simple RAG Pipeline                │
├─────────────────────────────────────────────────┤
│  1. LOAD: Read documents into memory            │
│     └─ Text files, PDFs, etc.                   │
├─────────────────────────────────────────────────┤
│  2. SEARCH: Find relevant parts                 │
│     └─ This week: keyword search                │
│     └─ Next week: semantic search (embeddings)  │
├─────────────────────────────────────────────────┤
│  3. PROMPT: Add context to question             │
│     └─ "Using this context: {results}"          │
├─────────────────────────────────────────────────┤
│  4. GENERATE: LLM creates answer                │
│     └─ Grounded in your documents               │
└─────────────────────────────────────────────────┘
```

### 3. Why RAG Works (30 min)

**Benefits of RAG:**
| Benefit | Explanation |
|---------|-------------|
| **Access private data** | AI can use your documents |
| **Always current** | Just update the documents |
| **Reduces hallucination** | AI answers from facts, not imagination |
| **No training needed** | Just change what you search |
| **Cheaper** | Don't need to fine-tune model |

**Limitations we'll solve later:**
- Keyword search isn't always accurate (Week 5-6: embeddings)
- Large documents need chunking (Week 5-6: chunking)
- Need to cite sources (Week 6: citations)

### 4. Basic Search Concepts (30 min)

**Keyword search:** Find documents containing specific words
```python
if "vacation" in document:
    return document
```

**Problems with keyword search:**
- "vacation" won't find "time off" or "PTO"
- Need exact word matches

**Next week's solution: Semantic search** (using embeddings)
- Understands meaning, not just keywords
- "vacation" finds "time off", "PTO", "leave"

---

## Hands-On Practice (4-6 hours)

### Task 1: Load Text Documents (45 min)

First, create some sample documents:

```python
# create_sample_docs.py
import os

# Create docs folder
os.makedirs("docs", exist_ok=True)

docs = {
    "company_info.txt": """
Company: TechCorp Inc.
Founded: 2020
Location: San Francisco, CA
Industry: Software Development
Employees: 150

Mission: To build AI-powered tools that make developers more productive.
""",
    
    "vacation_policy.txt": """
VACATION POLICY

All employees receive paid time off (PTO) as follows:
- 0-2 years: 15 days per year
- 2-5 years: 20 days per year  
- 5+ years: 25 days per year

Unused vacation days can be carried over up to 5 days.
Request vacation at least 2 weeks in advance through the HR portal.
""",
    
    "remote_work.txt": """
REMOTE WORK POLICY

TechCorp supports hybrid work:
- Minimum 2 days per week in office (Tues, Wed, Thurs)
- Remote work allowed Mon and Fri
- Full remote requires manager approval

Equipment allowance: $500 for home office setup.
Internet reimbursement: $50/month.
""",
    
    "benefits.txt": """
EMPLOYEE BENEFITS

Health Insurance:
- Medical, dental, and vision covered at 80%
- Family coverage available

Retirement:
- 401(k) with 4% company match
- Vesting after 1 year

Other Benefits:
- $1000 annual learning budget
- Gym membership reimbursement up to $50/month
- Free lunch on office days
"""
}

for filename, content in docs.items():
    with open(f"docs/{filename}", "w") as f:
        f.write(content)

print("Created sample documents in docs/")
```

Run it:
```bash
python create_sample_docs.py
```

### Task 2: Document Loader (45 min)

```python
# document_loader.py
import os
from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Document:
    """A document with content and metadata."""
    content: str
    filename: str
    path: str

def load_documents(folder: str) -> List[Document]:
    """Load all text files from a folder."""
    documents = []
    folder_path = Path(folder)
    
    for file in folder_path.glob("*.txt"):
        content = file.read_text()
        doc = Document(
            content=content,
            filename=file.name,
            path=str(file)
        )
        documents.append(doc)
        print(f"Loaded: {file.name} ({len(content)} chars)")
    
    return documents

# Test
if __name__ == "__main__":
    docs = load_documents("docs")
    print(f"\nTotal documents: {len(docs)}")
```

### Task 3: Simple Keyword Search (60 min)

```python
# simple_search.py
from document_loader import load_documents, Document
from typing import List
from dataclasses import dataclass

@dataclass
class SearchResult:
    document: Document
    score: float
    matched_terms: List[str]

def search(query: str, documents: List[Document], top_k: int = 3) -> List[SearchResult]:
    """Search documents by keyword matching."""
    
    # Split query into words
    query_terms = query.lower().split()
    results = []
    
    for doc in documents:
        content_lower = doc.content.lower()
        
        # Count matching terms
        matched = [term for term in query_terms if term in content_lower]
        
        if matched:
            # Score = percentage of query terms found
            score = len(matched) / len(query_terms)
            results.append(SearchResult(
                document=doc,
                score=score,
                matched_terms=matched
            ))
    
    # Sort by score descending
    results.sort(key=lambda x: x.score, reverse=True)
    
    return results[:top_k]

# Test
if __name__ == "__main__":
    docs = load_documents("docs")
    
    queries = [
        "vacation policy",
        "remote work",
        "health insurance benefits",
        "401k retirement"
    ]
    
    for query in queries:
        print(f"\n=== Query: '{query}' ===")
        results = search(query, docs)
        
        if results:
            for r in results:
                print(f"  {r.document.filename} (score: {r.score:.2f}, matched: {r.matched_terms})")
        else:
            print("  No results found")
```

### Task 4: RAG Q&A Function (60 min)

```python
# rag_qa.py
from openai import OpenAI
from dotenv import load_dotenv
from document_loader import load_documents
from simple_search import search

load_dotenv()
client = OpenAI()

def ask_documents(question: str, documents_folder: str = "docs") -> str:
    """Ask a question and get an answer from documents."""
    
    # Load documents
    docs = load_documents(documents_folder)
    
    # Search for relevant documents
    results = search(question, docs, top_k=2)
    
    if not results:
        return "I couldn't find any relevant information in the documents."
    
    # Build context from search results
    context_parts = []
    for result in results:
        context_parts.append(f"From {result.document.filename}:\n{result.document.content}")
    
    context = "\n\n---\n\n".join(context_parts)
    
    # Create prompt with context
    prompt = f"""Answer the question based ONLY on the provided context.
If the answer is not in the context, say "I don't have information about that."

Context:
{context}

Question: {question}

Answer:"""
    
    # Get answer from AI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You answer questions based only on the provided context."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

# Test
if __name__ == "__main__":
    questions = [
        "How many vacation days do I get after 3 years?",
        "Can I work from home on Monday?",
        "What's the 401k match?",
        "What's the CEO's name?"  # Not in docs
    ]
    
    for q in questions:
        print(f"\nQ: {q}")
        answer = ask_documents(q)
        print(f"A: {answer}")
```

### Task 5: Document Q&A Chatbot (60 min)

```python
# doc_chatbot.py
from openai import OpenAI
from dotenv import load_dotenv
from document_loader import load_documents, Document
from simple_search import search
from typing import List

load_dotenv()
client = OpenAI()

class DocumentChatbot:
    """A chatbot that answers from documents."""
    
    def __init__(self, documents_folder: str):
        self.documents = load_documents(documents_folder)
        self.conversation = []
        print(f"Loaded {len(self.documents)} documents")
    
    def chat(self, question: str) -> str:
        """Ask a question, get an answer from documents."""
        
        # Search for relevant docs
        results = search(question, self.documents, top_k=2)
        
        # Build context
        if results:
            context = "\n\n".join([
                f"[{r.document.filename}]: {r.document.content}"
                for r in results
            ])
        else:
            context = "No relevant documents found."
        
        # Add user question to conversation
        self.conversation.append({"role": "user", "content": question})
        
        # Build messages with context
        system_prompt = f"""You are a helpful assistant that answers questions based on company documents.

Available Information:
{context}

Rules:
- Answer based ONLY on the provided information
- If information is not available, say so
- Be concise but complete
- Cite which document the information comes from"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation
        ]
        
        # Get response
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        answer = response.choices[0].message.content
        
        # Add to conversation
        self.conversation.append({"role": "assistant", "content": answer})
        
        return answer
    
    def list_documents(self) -> None:
        """Show available documents."""
        print("\nAvailable documents:")
        for doc in self.documents:
            print(f"  - {doc.filename}")

# Interactive chat
if __name__ == "__main__":
    print("=" * 50)
    print("  Document Q&A Chatbot")
    print("=" * 50)
    
    bot = DocumentChatbot("docs")
    bot.list_documents()
    print("\nAsk me anything about these documents!")
    print("Commands: /docs (list docs), /quit (exit)\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input == "/quit":
            print("Goodbye!")
            break
        elif user_input == "/docs":
            bot.list_documents()
        else:
            answer = bot.chat(user_input)
            print(f"Bot: {answer}\n")
```

### Task 6: Add Source Citations (45 min)

```python
# rag_with_citations.py
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from document_loader import load_documents
from simple_search import search
import json

load_dotenv()
client = OpenAI()

class AnswerWithCitations(BaseModel):
    answer: str
    sources: List[str]
    confidence: str  # high, medium, low

def ask_with_citations(question: str, documents_folder: str = "docs") -> AnswerWithCitations:
    """Get answer with source citations."""
    
    docs = load_documents(documents_folder)
    results = search(question, docs, top_k=2)
    
    if not results:
        return AnswerWithCitations(
            answer="I couldn't find relevant information.",
            sources=[],
            confidence="low"
        )
    
    # Build numbered context
    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(f"[Source {i}: {r.document.filename}]\n{r.document.content}")
    
    context = "\n\n".join(context_parts)
    
    prompt = f"""Answer based on these sources:

{context}

Question: {question}

Return JSON:
{{
    "answer": "your answer here",
    "sources": ["source1.txt", "source2.txt"],
    "confidence": "high/medium/low"
}}"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer questions with citations."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    return AnswerWithCitations(**data)

# Test
if __name__ == "__main__":
    question = "What benefits do employees get for health insurance?"
    result = ask_with_citations(question)
    
    print(f"Q: {question}")
    print(f"A: {result.answer}")
    print(f"Sources: {result.sources}")
    print(f"Confidence: {result.confidence}")
```

---

## 🎯 Optional Challenges

*Extra practice for those who want to go deeper. Solutions not provided — figure it out!*

### Challenge 1: Multi-Domain RAG
Add 10+ documents from 3 different domains (HR, Engineering, Sales). Modify your search to handle queries that might span multiple domains.

### Challenge 2: "No Information Found" Detection
What happens when you ask about something NOT in the documents? Build detection that returns "I don't have information about that" instead of making things up.

```python
# Hint: Check relevance scores, use a threshold
def ask_or_decline(question: str) -> str:
    # If no relevant docs found, decline to answer
    pass
```

### Challenge 3: Chunk Size Experiment
Create the same document set with 3 different chunk sizes (100, 300, 500 words). Test the same 10 questions on each. Which performs best? Document your findings.

### Challenge 4: Conversation Memory + RAG
Combine what you learned in Week 2 (chatbot memory) with RAG. Build a document chatbot that remembers the conversation:

```
User: What's our vacation policy?
AI: Employees get 15 days PTO per year...
User: What about sick days?     <-- Remembers we're talking about policies
AI: Sick leave is separate from PTO...
User: How does that compare to holidays?  <-- Maintains context
```

### Challenge 5: Build a RAG API
Wrap your RAG system in a simple HTTP API using FastAPI:
```python
@app.post("/ask")
def ask_documents(question: str):
    return {"answer": ..., "sources": [...]}
```

---

## Knowledge Checklist

- [ ] I understand what RAG is and why it's important
- [ ] I can load text documents in Python
- [ ] I can search documents for relevant content
- [ ] I can combine search results with AI prompts
- [ ] I built a document Q&A chatbot
- [ ] I can add citations to answers

---

## Deliverables

1. Sample documents in `docs/` folder
2. `document_loader.py` — Load text files
3. `simple_search.py` — Keyword search
4. `rag_qa.py` — Basic Q&A function
5. `doc_chatbot.py` — Interactive document chatbot
6. `rag_with_citations.py` — Answers with sources

---

## Month 1 Complete!

You've built a chatbot that:
- Remembers conversations (Week 2)
- Returns structured data (Week 3)
- Answers from your documents (Week 4)

**Next month** you'll make it much better:
- Semantic search (find by meaning, not just keywords)
- Better document handling (chunking, vector databases)
- Quality testing (evaluations)
- Security (guardrails)

---

## Resources

- [RAG Overview](https://python.langchain.com/docs/tutorials/rag/)
- [OpenAI Cookbook - RAG](https://cookbook.openai.com/examples/question_answering_using_embeddings)
