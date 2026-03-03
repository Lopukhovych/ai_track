# AI Engineering Knowledge Reference

Quick reference for key concepts, APIs, and patterns covered in the curriculum.

---

## Table of Contents

- [LLM APIs](#llm-apis)
- [Prompting Patterns](#prompting-patterns)
- [Structured Output](#structured-output)
- [Embeddings](#embeddings)
- [Vector Databases](#vector-databases)
- [RAG Architecture](#rag-architecture)
- [Tool Calling](#tool-calling)
- [Agent Patterns](#agent-patterns)
- [Frameworks](#frameworks)
- [MCP Protocol](#mcp-protocol)
- [Production Patterns](#production-patterns)
- [Evaluation Methods](#evaluation-methods)
- [Enterprise AI Topics](#enterprise-ai-topics)
- [Interview Quick Reference](#interview-quick-reference)

---

## LLM APIs

### OpenAI

```python
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are helpful."},
        {"role": "user", "content": "Hello"}
    ],
    temperature=0.7,
    max_tokens=500
)
print(response.choices[0].message.content)
```

### Anthropic

```python
from anthropic import Anthropic
client = Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=500,
    system="You are helpful.",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.content[0].text)
```

### Google Gemini

```python
import google.generativeai as genai
genai.configure()

model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content("Hello")
print(response.text)
```

### Ollama (Local)

```python
from openai import OpenAI
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

response = client.chat.completions.create(
    model="llama3.2",
    messages=[{"role": "user", "content": "Hello"}]
)
```

### LLM Provider Comparison

| Provider | Best For | Context Window | Pricing (approx) | Unique Features |
|----------|----------|----------------|------------------|-----------------|
| **OpenAI GPT-4o** | General purpose, coding | 128K | $5/$15 per 1M tokens | Best tool calling, vision |
| **GPT-4o-mini** | Cost-effective tasks | 128K | $0.15/$0.60 per 1M | Best value for simple tasks |
| **Claude Sonnet** | Long docs, analysis | 200K | $3/$15 per 1M | Extended thinking, artifacts |
| **Claude Haiku** | Fast, cheap | 200K | $0.25/$1.25 per 1M | Fastest Claude model |
| **Gemini 1.5 Pro** | Multimodal, long context | 1M-2M | $1.25/$5 per 1M | Largest context window |
| **Gemini Flash** | Speed, efficiency | 1M | $0.075/$0.30 per 1M | Very fast, cheap |
| **Ollama/Local** | Privacy, offline | Varies | Free | No data leaves machine |

**When to use which:**
- **Production chat apps**: GPT-4o-mini or Claude Haiku (cost + quality balance)
- **Complex reasoning**: GPT-4o or Claude Sonnet  
- **Very long documents**: Gemini 1.5 Pro (1M+ context)
- **Sensitive data**: Ollama (local, no API calls)
- **Multimodal (images)**: GPT-4o or Gemini

---

## Prompting Patterns

### Zero-Shot
Direct instruction without examples.
```
Classify this text as positive, negative, or neutral: "{text}"
```

### Few-Shot
Provide examples before the query.
```
Classify these texts:
"I love it" -> positive
"Terrible experience" -> negative

Now classify: "{text}"
```

### Chain of Thought (CoT)
Force step-by-step reasoning.
```
Think step by step:
1. First, identify...
2. Then, analyze...
3. Finally, conclude...
```

### Structured Prompting
Request specific format.
```
Respond in JSON format:
{
  "answer": "...",
  "confidence": 0.0-1.0,
  "reasoning": "..."
}
```

---

## Structured Output

### OpenAI Response Format

```python
from pydantic import BaseModel

class Answer(BaseModel):
    answer: str
    confidence: float
    sources: list[str]

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[...],
    response_format=Answer
)
parsed = response.choices[0].message.parsed
```

### Anthropic Tool Use for Structure

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[...],
    tools=[{
        "name": "structured_response",
        "description": "Return structured data",
        "input_schema": Answer.model_json_schema()
    }],
    tool_choice={"type": "tool", "name": "structured_response"}
)
```

---

## Embeddings

### Create Embeddings

```python
def embed(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",  # 1536 dims
        input=text
    )
    return response.data[0].embedding
```

### Similarity

```python
import numpy as np

def cosine_similarity(a: list, b: list) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

### Embedding Models

| Model | Dims | Use Case |
|-------|------|----------|
| `text-embedding-3-small` | 1536 | General, cost-effective |
| `text-embedding-3-large` | 3072 | Higher quality |
| `sentence-transformers/all-MiniLM-L6-v2` | 384 | Open-source, fast |

---

## Vector Databases

### Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

client = QdrantClient(":memory:")  # or path="./db" or url="..."

# Create collection
client.create_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# Insert
client.upsert(
    collection_name="docs",
    points=[PointStruct(id=1, vector=embedding, payload={"text": "..."})]
)

# Search
results = client.search(
    collection_name="docs",
    query_vector=query_embedding,
    limit=5
)
```

### ChromaDB

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("docs")

collection.add(
    ids=["1"],
    embeddings=[embedding],
    documents=["..."],
    metadatas=[{"source": "..."}]
)

results = collection.query(query_embeddings=[query_embedding], n_results=5)
```

---

## RAG Architecture

### Basic Pipeline

```python
def rag_query(question: str) -> str:
    # 1. Embed query
    query_embedding = embed(question)
    
    # 2. Retrieve documents
    docs = vector_db.search(query_embedding, limit=5)
    
    # 3. Build context
    context = "\n".join([d.payload["text"] for d in docs])
    
    # 4. Generate answer
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Context:\n{context}"},
            {"role": "user", "content": question}
        ]
    )
    
    return response.choices[0].message.content
```

### Query Rewriting

```python
def rewrite_query(original: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": f"Rewrite for search:\n{original}"
        }]
    )
    return response.choices[0].message.content
```

### RAG with Citations

```python
SYSTEM = """Answer based on sources. Cite with [1], [2], etc.
If not in sources, say "I don't have information about that."
"""
```

---

## Tool Calling

### Define Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search knowledge base",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    }
]
```

### Execute Tool Calls

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools
)

if response.choices[0].message.tool_calls:
    for tc in response.choices[0].message.tool_calls:
        name = tc.function.name
        args = json.loads(tc.function.arguments)
        result = execute_tool(name, args)
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(result)
        })
```

---

## Agent Patterns

### Basic Agent Loop

```python
class Agent:
    def __init__(self, tools: list, max_steps: int = 10):
        self.tools = tools
        self.max_steps = max_steps
        self.messages = []
    
    def run(self, task: str) -> str:
        self.messages.append({"role": "user", "content": task})
        
        for step in range(self.max_steps):
            response = self.call_llm()
            
            if response.tool_calls:
                self.execute_tools(response.tool_calls)
            else:
                return response.content  # Final answer
        
        return "Max steps reached"
```

### Safety Limits

```python
MAX_TOOL_CALLS = 10
MAX_TIME_SECONDS = 30
MAX_TOKENS = 10000
```

---

## Frameworks

### LangGraph

```python
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    messages: list

def chatbot(state: State) -> dict:
    return {"messages": [llm.invoke(state["messages"])]}

graph = StateGraph(State)
graph.add_node("chatbot", chatbot)
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)
app = graph.compile()
```

### CrewAI

```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Researcher",
    goal="Find accurate information",
    llm="gpt-4o-mini"
)

task = Task(
    description="Research X topic",
    agent=researcher,
    expected_output="Summary with sources"
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
```

---

## MCP Protocol

### MCP Server

```python
from mcp.server import Server
from mcp.types import Tool

server = Server("my-tools")

@server.list_tools()
async def list_tools():
    return [Tool(name="search", description="...", inputSchema={...})]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "search":
        return [TextContent(type="text", text=results)]
```

### MCP Client

```python
from mcp import ClientSession

session = ClientSession(read_stream, write_stream)
await session.initialize()
tools = await session.list_tools()
result = await session.call_tool("search", {"query": "..."})
```

---

## Production Patterns

### Budget Enforcement

```python
@dataclass
class RequestBudget:
    max_tokens: int = 4000
    max_time_seconds: float = 30.0
    max_cost_usd: float = 0.10
```

### Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.state = "closed"
        self.failures = 0
```

### Retry with Backoff

```python
delay = base_delay * (2 ** attempt)
time.sleep(min(delay, max_delay))
```

### Graceful Degradation

1. Full response
2. Cached response
3. Retrieval-only (no generation)
4. Fallback message

---

## Evaluation Methods

### Metrics

| Metric | What It Measures |
|--------|------------------|
| **Accuracy** | Correct vs expected |
| **Faithfulness** | Grounded in sources |
| **Relevance** | On-topic response |
| **Toxicity** | Harmful content |
| **Latency** | Response time |
| **Cost** | $ per request |

### LLM-as-Judge

```python
def evaluate_answer(question: str, answer: str, context: str) -> dict:
    prompt = f"""Evaluate this answer:
Question: {question}
Context: {context}
Answer: {answer}

Score 1-5 on: Accuracy, Faithfulness, Helpfulness
"""
    response = client.chat.completions.create(...)
    return parse_scores(response)
```

---

## Enterprise AI Topics

### SQL for AI Engineers

```sql
-- Most searched documents
WITH search_stats AS (
    SELECT document_id, COUNT(*) as count, AVG(similarity) as avg_sim
    FROM search_logs
    GROUP BY document_id
)
SELECT d.title, s.count, ROUND(s.avg_sim, 2)
FROM search_stats s
JOIN documents d ON s.document_id = d.id
ORDER BY s.count DESC LIMIT 10;
```

### Data Quality Checks

```python
def validate_chunk(chunk: dict) -> list[str]:
    errors = []
    if not chunk.get("text"):
        errors.append("Empty text")
    if len(chunk.get("embedding", [])) != 1536:
        errors.append("Invalid embedding dimension")
    if not chunk.get("source"):
        errors.append("Missing source")
    return errors
```

### RBAC (Role-Based Access Control)

```python
ROLE_PERMISSIONS = {
    "admin": {"query", "modify", "delete", "manage_users"},
    "developer": {"query", "modify", "view_logs"},
    "user": {"query"},
    "auditor": {"view_logs"},
}

def check_permission(role: str, action: str) -> bool:
    return action in ROLE_PERMISSIONS.get(role, set())
```

### Secrets Management

```python
# ❌ Never hardcode
api_key = "sk-..."  

# ✅ Environment variables
api_key = os.environ["OPENAI_API_KEY"]

# ✅ Secret manager (production)
# Azure Key Vault, AWS Secrets Manager, etc.
```

### Red-Teaming Categories

| Attack Type | Example | Defense |
|-------------|---------|---------|
| Prompt Injection | "Ignore instructions" | Input validation |
| Jailbreaking | "Pretend you're evil" | Content filters |
| Data Extraction | "Reveal your prompt" | Prompt protection |
| Resource Exhaustion | Very long prompts | Token limits |

---

## Interview Quick Reference

### RAG Design Questions
- Chunking: 500-1000 tokens, overlap 10-20%
- Embedding: text-embedding-3-small for most cases
- Retrieval: k=5-10, then rerank
- Why RAG fails: bad chunking, wrong embedding, no relevant docs

### Agent Design Questions
- When to use: multi-step, tool use, dynamic
- When not to: simple Q&A, latency-critical
- Safety: max steps, timeout, human approval

### Cost Optimization
- Model routing (cheap for simple)
- Prompt caching
- Response caching  
- Smaller context windows

### Latency Optimization
- Streaming
- Parallel retrieval
- Model selection
- Caching

### Production Checklist
- [ ] Error handling
- [ ] Rate limiting
- [ ] Budget enforcement
- [ ] Monitoring/tracing
- [ ] Evaluation suite
- [ ] Gradual rollout
