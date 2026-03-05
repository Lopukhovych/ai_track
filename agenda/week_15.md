# Week 15: Capstone Project & Interview Prep

**Month:** 4 (Production & Career) | **Duration:** 8-10 hours

---

## Overview

Congratulations on reaching the final week! 🎉 This week you'll build your **capstone project** combining everything you've learned, prepare your **portfolio**, and get ready for **AI engineering interviews**.

---

## Learning Objectives

By the end of this week, you will:
- Complete a production-quality capstone project
- Have a polished AI engineering portfolio
- Know common interview questions and patterns
- Be ready to demonstrate your skills
- Have a clear path for continued learning

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| Chat / RAG | `gpt-4o-mini` | `llama3.1:8b` |
| Embeddings | `text-embedding-3-small` | `nomic-embed-text` |
| Vision | `gpt-4o` | `llama3.2-vision:11b` |
| Code generation | `gpt-4o-mini` | `qwen2.5-coder:7b` |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b && ollama pull nomic-embed-text
```

```python
from scripts.model_config import get_client, CHAT_MODEL, EMBED_MODEL, VISION_MODEL, CODE_MODEL
# Capstone tip: build the project with Ollama first to avoid API costs during development,
# then test with OpenAI before submitting for portfolio.
```

---

## Portfolio Project #3: Full-Stack AI Application (6-8 hours)

### The Project: AI Research Assistant

Build a complete AI research assistant that:
- Answers questions using RAG over your documents
- Has multi-modal capabilities (vision, audio)
- Uses agents with tools for complex tasks
- Is production-ready (secure, observable, resilient)
- Has a clean API interface

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI RESEARCH ASSISTANT                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐   │
│  │   FastAPI   │────▶│   AI Core    │────▶│  OpenAI API │   │
│  │   Gateway   │     │              │     └─────────────┘   │
│  └─────────────┘     │  - RAG       │                       │
│         │            │  - Agents    │     ┌─────────────┐   │
│         │            │  - Tools     │────▶│   Qdrant    │   │
│         ▼            │  - Multi-mod │     │  Vector DB  │   │
│  ┌─────────────┐     └──────────────┘     └─────────────┘   │
│  │  Security   │            │                               │
│  │  Layer      │            ▼                               │
│  │  - Auth     │     ┌──────────────┐                       │
│  │  - Moderat. │     │ Observability │                      │
│  │  - Rate Lim │     │ - Logging     │                      │
│  └─────────────┘     │ - Metrics     │                      │
│                      │ - Tracing     │                      │
│                      └──────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Part 1: Core Application (capstone/core.py)

```python
# capstone/core.py
"""
Core AI Research Assistant with RAG, Tools, and Multi-Modal support.
"""
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import base64

load_dotenv()
client = OpenAI()

@dataclass
class Document:
    content: str
    source: str
    embedding: Optional[List[float]] = None

class KnowledgeBase:
    """Simple vector-based knowledge base."""
    
    def __init__(self):
        self.documents: List[Document] = []
    
    def add_document(self, content: str, source: str):
        """Add a document to the knowledge base."""
        embedding = self._embed(content)
        self.documents.append(Document(
            content=content,
            source=source,
            embedding=embedding
        ))
    
    def _embed(self, text: str) -> List[float]:
        """Get embedding for text."""
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity."""
        import numpy as np
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def search(self, query: str, top_k: int = 3) -> List[Document]:
        """Search for relevant documents."""
        if not self.documents:
            return []
        
        query_embedding = self._embed(query)
        
        scored = [
            (doc, self._similarity(query_embedding, doc.embedding))
            for doc in self.documents
            if doc.embedding is not None
        ]
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in scored[:top_k]]

class ToolKit:
    """Tools for the research assistant."""
    
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
    
    @property
    def definitions(self) -> List[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "Search the knowledge base for relevant information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform a mathematical calculation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "Math expression to evaluate"
                            }
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "summarize_text",
                    "description": "Summarize a piece of text",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to summarize"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["brief", "detailed", "bullet_points"],
                                "description": "Summary style"
                            }
                        },
                        "required": ["text"]
                    }
                }
            }
        ]
    
    def execute(self, name: str, arguments: dict) -> str:
        """Execute a tool."""
        if name == "search_knowledge":
            docs = self.kb.search(arguments["query"])
            if not docs:
                return "No relevant documents found."
            return "\n\n".join([
                f"[{doc.source}]\n{doc.content}"
                for doc in docs
            ])
        
        elif name == "calculate":
            try:
                # Safe evaluation
                result = eval(arguments["expression"], {"__builtins__": {}})
                return f"Result: {result}"
            except Exception as e:
                return f"Calculation error: {e}"
        
        elif name == "summarize_text":
            style = arguments.get("style", "brief")
            prompt = f"Summarize this text ({style} style):\n\n{arguments['text']}"
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        
        return f"Unknown tool: {name}"

class ResearchAssistant:
    """Main research assistant class."""
    
    def __init__(self):
        self.kb = KnowledgeBase()
        self.toolkit = ToolKit(self.kb)
        self.conversation: List[dict] = []
        self.system_prompt = """You are an AI Research Assistant.

Your capabilities:
1. Answer questions using your knowledge base
2. Perform calculations
3. Summarize text
4. Analyze images (when provided)
5. Engage in helpful conversation

Always use tools when they would help provide accurate answers.
Cite your sources when using information from the knowledge base.
Be helpful, accurate, and concise."""
    
    def add_knowledge(self, content: str, source: str = "user"):
        """Add knowledge to the assistant."""
        self.kb.add_document(content, source)
    
    def chat(
        self,
        message: str,
        image_url: Optional[str] = None
    ) -> str:
        """Chat with the assistant."""
        
        # Build message content
        if image_url:
            user_content = [
                {"type": "text", "text": message},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        else:
            user_content = message
        
        # Add to conversation
        self.conversation.append({"role": "user", "content": user_content})
        
        # Build messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation[-10:]  # Keep last 10 messages
        
        # Call with tools
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=self.toolkit.definitions
        )
        
        msg = response.choices[0].message
        
        # Handle tool calls
        if msg.tool_calls:
            self.conversation.append(msg)
            
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = self.toolkit.execute(tc.function.name, args)
                
                self.conversation.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
            
            # Get final response
            final_messages = [
                {"role": "system", "content": self.system_prompt}
            ] + self.conversation[-15:]
            
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=final_messages
            )
            
            reply = final_response.choices[0].message.content
        else:
            reply = msg.content
        
        self.conversation.append({"role": "assistant", "content": reply})
        return reply
    
    def analyze_image(self, image_path: str, question: str = "What is in this image?") -> str:
        """Analyze an image."""
        with open(image_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode()
        
        image_url = f"data:image/jpeg;base64,{base64_image}"
        return self.chat(question, image_url=image_url)
    
    def reset(self):
        """Reset conversation history."""
        self.conversation = []

# Test
if __name__ == "__main__":
    assistant = ResearchAssistant()
    
    # Add some knowledge
    assistant.add_knowledge(
        "Python was created by Guido van Rossum and first released in 1991. "
        "It emphasizes code readability and simplicity.",
        "python_facts.txt"
    )
    assistant.add_knowledge(
        "Machine learning is a subset of artificial intelligence that enables "
        "systems to learn and improve from experience without being explicitly programmed.",
        "ml_basics.txt"
    )
    
    # Test chat
    print("Testing Research Assistant...")
    
    queries = [
        "What is Python?",
        "Calculate 25 * 4 + 100",
        "What is machine learning?"
    ]
    
    for q in queries:
        print(f"\nQ: {q}")
        print(f"A: {assistant.chat(q)}")
```

### Part 2: API Layer (capstone/api.py)

```python
# capstone/api.py
"""
FastAPI application for the Research Assistant.
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time
from functools import wraps

from core import ResearchAssistant

# App setup
app = FastAPI(
    title="AI Research Assistant API",
    description="Production-ready AI research assistant",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Metrics
class Metrics:
    def __init__(self):
        self.requests = 0
        self.errors = 0
        self.total_latency = 0
    
    def record(self, latency: float, error: bool = False):
        self.requests += 1
        self.total_latency += latency
        if error:
            self.errors += 1
    
    @property
    def stats(self):
        return {
            "total_requests": self.requests,
            "errors": self.errors,
            "avg_latency_ms": round(self.total_latency / self.requests * 1000, 2) if self.requests > 0 else 0
        }

metrics = Metrics()

# Rate limiting (simple in-memory)
rate_limits = {}
RATE_LIMIT = 60  # requests per minute

def check_rate_limit(api_key: str):
    now = time.time()
    minute = int(now / 60)
    
    key = f"{api_key}:{minute}"
    rate_limits[key] = rate_limits.get(key, 0) + 1
    
    # Cleanup old entries
    for k in list(rate_limits.keys()):
        if int(k.split(":")[-1]) < minute - 1:
            del rate_limits[k]
    
    return rate_limits[key] <= RATE_LIMIT

# Session management
sessions = {}

def get_or_create_session(session_id: str) -> ResearchAssistant:
    if session_id not in sessions:
        sessions[session_id] = ResearchAssistant()
    return sessions[session_id]

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    image_url: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    latency_ms: float

class KnowledgeRequest(BaseModel):
    content: str
    source: str = "user"
    session_id: str = "default"

class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    metrics: dict

# Dependency
async def verify_api_key(x_api_key: str = Header(...)):
    # In production, validate against a database
    if not x_api_key.startswith("sk-"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if not check_rate_limit(x_api_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return x_api_key

# Endpoints
start_time = time.time()

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        uptime_seconds=round(time.time() - start_time, 2),
        metrics=metrics.stats
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    start = time.time()
    
    try:
        assistant = get_or_create_session(request.session_id)
        response = assistant.chat(
            request.message,
            image_url=request.image_url
        )
        
        latency = time.time() - start
        metrics.record(latency)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
            latency_ms=round(latency * 1000, 2)
        )
    
    except Exception as e:
        latency = time.time() - start
        metrics.record(latency, error=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/knowledge")
async def add_knowledge(
    request: KnowledgeRequest,
    api_key: str = Depends(verify_api_key)
):
    assistant = get_or_create_session(request.session_id)
    assistant.add_knowledge(request.content, request.source)
    
    return {"status": "added", "source": request.source}

@app.delete("/session/{session_id}")
async def clear_session(
    session_id: str,
    api_key: str = Depends(verify_api_key)
):
    if session_id in sessions:
        sessions[session_id].reset()
        return {"status": "cleared", "session_id": session_id}
    return {"status": "not_found", "session_id": session_id}

@app.get("/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    return metrics.stats

# Run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Part 3: Docker Configuration

```dockerfile
# capstone/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY *.py .

# Environment
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

```txt
# capstone/requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
openai==1.12.0
python-dotenv==1.0.0
pydantic==2.6.0
numpy==1.26.4
```

---

## Interview Preparation (2 hours)

### Common AI Engineering Interview Topics

#### 1. Fundamentals

**Q: Explain how LLMs work at a high level.**
```
A: LLMs are trained on massive text datasets to predict the next token.
They use transformer architecture with attention mechanisms to understand
context. At inference time, they generate text token by token, using
probability distributions to select each next token.
```

**Q: What is the difference between embeddings and LLMs?**
```
A: Embeddings convert text into fixed-size vectors that capture semantic
meaning. They're used for similarity search and retrieval. LLMs generate
text and can understand/respond to prompts. You typically use embeddings
for RAG retrieval, then LLMs for generation.
```

**Q: Explain RAG and when you would use it.**
```
A: RAG (Retrieval Augmented Generation) combines search with LLMs:
1. Convert query to embedding
2. Search vector database for relevant documents
3. Include documents in LLM prompt as context
4. LLM generates answer based on retrieved context

Use RAG when you need the LLM to answer based on specific documents
or knowledge that's not in its training data, or needs to be up-to-date.
```

#### 2. Architecture & Design

**Q: How would you design a conversational AI system?**
```
Key components:
1. API Gateway - handle requests, auth, rate limiting
2. Conversation Manager - track history, sessions
3. RAG Pipeline - retrieve relevant context
4. LLM Integration - generate responses
5. Guardrails - input validation, content moderation
6. Observability - logging, metrics, tracing
```

**Q: How do you handle AI system security?**
```
Layers of protection:
1. Input validation - detect prompt injection
2. Content moderation - filter harmful content
3. Output filtering - verify response safety
4. Rate limiting - prevent abuse
5. Authentication - verify users
6. Audit logging - track all interactions
```

#### 3. Practical Scenarios

**Q: Your RAG system returns poor quality answers. How do you debug?**
```
Step-by-step:
1. Check retrieval - are the right documents being found?
2. Check chunking - are chunks the right size?
3. Check embeddings - is semantic similarity working?
4. Check prompt - is context being used correctly?
5. Add evaluation metrics to measure quality
6. Test with known good Q&A pairs
```

**Q: How would you reduce AI API costs?**
```
Strategies:
1. Caching - cache responses for repeated queries
2. Model selection - use smaller models when possible
3. Prompt optimization - reduce token usage
4. Batching - combine multiple requests
5. Fine-tuning - reduce prompt size with custom model
6. Rate limiting - prevent runaway costs
```

### Coding Challenge Practice

```python
# interview_practice.py
"""
Practice problems for AI engineering interviews.
"""

# Problem 1: Implement a simple semantic cache
class SemanticCache:
    """
    Cache that matches queries by semantic similarity.
    If a new query is >90% similar to a cached query, return cached result.
    """
    def __init__(self, threshold=0.9):
        self.threshold = threshold
        self.cache = []  # List of (query_embedding, response)
    
    def get(self, query: str, embed_fn) -> str | None:
        # TODO: Implement semantic lookup
        pass
    
    def set(self, query: str, response: str, embed_fn):
        # TODO: Store query embedding and response
        pass

# Problem 2: Implement retry with circuit breaker
def resilient_call(fn, max_retries=3, failure_threshold=5):
    """
    Call fn with retries and circuit breaker.
    After failure_threshold failures, stop trying for 60 seconds.
    """
    # TODO: Implement
    pass

# Problem 3: Implement a simple ReAct agent
class ReActAgent:
    """
    Agent that follows Thought -> Action -> Observation loop.
    """
    def __init__(self, tools: dict):
        self.tools = tools  # {"tool_name": callable}
    
    def run(self, question: str, max_steps=5) -> str:
        """
        Execute ReAct loop until answer is found.
        """
        # TODO: Implement
        pass

# Problem 4: Implement document chunking
def chunk_document(text: str, chunk_size=500, overlap=50) -> list[str]:
    """
    Split document into overlapping chunks.
    Try to split at sentence boundaries.
    """
    # TODO: Implement
    pass
```

### Enterprise AI Interview Topics

These topics are commonly asked in enterprise AI engineering interviews:

#### 1. Data Engineering & SQL

**Q: Write a SQL query to find the top 5 most frequently retrieved documents.**
```sql
WITH retrieval_counts AS (
    SELECT 
        document_id,
        COUNT(*) as retrieval_count,
        AVG(similarity_score) as avg_similarity
    FROM search_logs
    WHERE timestamp > NOW() - INTERVAL '30 days'
    GROUP BY document_id
)
SELECT 
    d.title,
    r.retrieval_count,
    ROUND(r.avg_similarity, 3) as avg_score
FROM retrieval_counts r
JOIN documents d ON r.document_id = d.id
ORDER BY r.retrieval_count DESC
LIMIT 5;
```

**Q: Explain ETL vs ELT pipelines.**
```
ETL (Extract, Transform, Load):
- Transform data BEFORE loading to destination
- Better for on-premise, limited storage
- Transformations happen in staging area

ELT (Extract, Load, Transform):
- Load raw data first, transform in destination
- Better for cloud data warehouses (BigQuery, Snowflake)
- Use cloud compute power for transformations

For AI: ELT often preferred because you can:
- Keep raw data for re-processing with new models
- Run multiple transformation pipelines
- Scale compute independently
```

#### 2. Enterprise Integration

**Q: How would you integrate AI with Microsoft Teams or Slack?**
```
Architecture:
1. Webhook/Bot endpoint receives messages
2. Message router identifies intent (command vs conversation)
3. AI service processes with context
4. Response formatter creates platform-specific reply
5. Audit logger tracks all interactions

Key considerations:
- Authentication (OAuth, tokens)
- Rate limiting (platform + AI API)
- Async responses for long operations
- Thread/channel context management
- Error handling with user-friendly messages
```

**Q: How do you handle secrets in production AI systems?**
```
Levels (worst to best):
1. Hardcoded (NEVER do this)
2. Environment variables (OK for simple cases)
3. .env files with .gitignore (local dev only)
4. Secret managers (Key Vault, AWS Secrets Manager)
5. Managed Identity (best - no secrets at all)

Production pattern:
- Use Managed Identity when possible
- Fall back to Key Vault for API keys
- Rotate secrets regularly
- Never log secrets
- Use different keys per environment
```

#### 3. Security & Compliance

**Q: Explain red-teaming for AI systems.**
```
Red-teaming = adversarial testing of AI systems

Categories of attacks to test:
1. Prompt injection - "Ignore instructions and..."
2. Jailbreaking - bypass content policies
3. Data extraction - extract training data
4. Bias exploitation - trigger biased outputs
5. Resource exhaustion - costly prompts

Process:
1. Define attack surface
2. Create attack dataset
3. Test systematically
4. Document vulnerabilities
5. Implement mitigations
6. Re-test continuously
```

**Q: How do you ensure GDPR compliance for AI?**
```
Key requirements:
1. Right to explanation - explain AI decisions
2. Right to erasure - delete user data from training
3. Data minimization - only collect needed data
4. Purpose limitation - use data only for stated purpose
5. Storage limitation - don't keep data forever

Implementation:
- Log all AI decisions with reasoning
- Implement data deletion pipelines
- Track consent and purpose
- Use anonymization where possible
- Regular compliance audits
```

#### 4. Evaluation & Quality

**Q: How do you create ground-truth datasets for RAG evaluation?**
```
Process:
1. Sample real queries from production
2. Manually identify correct source documents
3. Write expected answers (or acceptable criteria)
4. Include edge cases (no answer available, ambiguous)
5. Stratify by topic/difficulty

Quality criteria:
- Inter-rater reliability (multiple annotators)
- Coverage of use cases
- Updated regularly
- Includes negative examples

Tools: LabelStudio, Prodigy, or custom annotation UI
```

**Q: How do you set up CI/CD for AI systems?**
```
Pipeline stages:

1. Code Quality
   - Linting, formatting
   - Type checking
   - Unit tests

2. AI-Specific Tests
   - Prompt regression tests
   - Tool call validation
   - RAG retrieval quality checks

3. Evaluation
   - Run against ground-truth dataset
   - Check quality metrics don't regress
   - Flag if below threshold

4. Deploy (if passed)
   - Canary deployment
   - A/B testing framework
   - Rollback capability
```

#### 5. Performance & Production

**Q: How do you implement hybrid search for RAG?**
```
Hybrid = Vector search + Keyword search

Implementation:
1. Run vector search (semantic similarity)
2. Run keyword search (BM25/TF-IDF)
3. Combine scores with Reciprocal Rank Fusion:

def rrf_score(rank, k=60):
    return 1 / (k + rank)

combined_score = alpha * vector_score + (1-alpha) * keyword_score

When to use:
- Exact matches matter (product codes, names)
- Domain-specific terminology
- Acronyms and abbreviations
```

**Q: How do you handle document processing for RAG?**
```
Pipeline:
1. Extraction
   - PDFs: pdfplumber, pymupdf, Azure Document Intelligence
   - Office: python-docx, openpyxl
   - HTML: BeautifulSoup

2. Cleaning
   - Remove headers/footers
   - Handle tables
   - Preserve structure

3. Chunking
   - Recursive character splitting
   - Semantic chunking (by topic)
   - Document-aware chunking (respect sections)

4. Enrichment
   - Add metadata (source, date, author)
   - Generate summaries
   - Extract entities
```

### System Design Template

When asked to design an AI system, follow this structure:

```
1. CLARIFY REQUIREMENTS
   - What is the use case?
   - What scale? (users, requests/sec)
   - What quality requirements?
   - What constraints? (cost, latency)

2. HIGH-LEVEL ARCHITECTURE
   - Draw the main components
   - Show data flow
   - Identify AI vs traditional components

3. DEEP DIVE ON KEY COMPONENTS
   - RAG pipeline design
   - Model selection
   - Prompt engineering strategy

4. PRODUCTION CONSIDERATIONS
   - How to monitor quality?
   - How to handle failures?
   - How to control costs?
   - How to iterate/improve?

5. TRADE-OFFS
   - Acknowledge alternatives
   - Explain your choices
```

---

## Career Resources

### Portfolio Checklist

Your portfolio should demonstrate:

- [ ] **Technical Skills**
  - [ ] API integration (OpenAI, Anthropic)
  - [ ] RAG implementation
  - [ ] Agent development
  - [ ] Production hardening

- [ ] **Projects**
  - [ ] Portfolio #1: HR Bot (RAG + Security)
  - [ ] Portfolio #2: Multi-Agent App
  - [ ] Portfolio #3: Full-Stack Research Assistant

- [ ] **Code Quality**
  - [ ] Clean, documented code
  - [ ] Tests (at least examples)
  - [ ] Docker/deployment ready
  - [ ] README with setup instructions

### GitHub Profile

Structure your AI projects:
```
ai-portfolio/
├── README.md           # Overview of all projects
├── hr-bot/             # Portfolio #1
│   ├── README.md
│   ├── src/
│   └── tests/
├── agent-app/          # Portfolio #2
│   └── ...
└── research-assistant/ # Portfolio #3 (Capstone)
    └── ...
```

### Continued Learning

**Next Steps:**
1. **Specialize** — Pick an area (agents, vision, speech, etc.)
2. **Build** — Create more projects
3. **Contribute** — Open source AI projects
4. **Stay Updated** — Follow AI news, papers, releases

**Resources:**
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI Cookbook](https://cookbook.openai.com/)
- [Anthropic Documentation](https://docs.anthropic.com/)
- [Hugging Face](https://huggingface.co/)
- [AI Papers](https://arxiv.org/list/cs.AI/recent)

---

## Knowledge Checklist

- [ ] I completed the capstone project
- [ ] My portfolio has 3 substantial projects
- [ ] I can explain RAG, agents, and AI concepts
- [ ] I practiced common interview questions
- [ ] I understand system design patterns
- [ ] I have a plan for continued learning

---

## Deliverables

1. **Capstone Project** — Complete AI Research Assistant
   - Core functionality (`core.py`)
   - API layer (`api.py`)
   - Docker deployment
2. **Portfolio** — GitHub repository with all 3 projects
3. **Interview Prep** — Practiced answers to common questions

---

## 🎉 Congratulations!

You've completed the AI Engineering curriculum!

**What you've learned:**
- Month 1: AI fundamentals, APIs, prompting, RAG basics
- Month 2: Embeddings, vector DBs, evaluations, security
- Month 3: Tool calling, agents, frameworks, multi-modal
- Month 4: MCP, observability, production hardening, deployment

**What you can do:**
- Build production-ready AI applications
- Implement RAG systems
- Create AI agents with tools
- Deploy and monitor AI systems
- Continue learning independently

**Good luck on your AI engineering journey!** 🚀
