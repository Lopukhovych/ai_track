# Week 13: MCP & Observability

**Month:** 4 (Production & Career) | **Duration:** 6-8 hours

---

## Overview

Welcome to Month 4! You're entering production territory. This week you'll learn about **MCP (Model Context Protocol)** for connecting AI to external systems, and **observability** for understanding what your AI is doing in production.

---

## Learning Objectives

By the end of this week, you will:
- Understand what MCP is and why it matters
- Build MCP servers to expose tools
- Connect AI to external systems via MCP
- Implement logging and tracing
- Set up observability for AI applications

---

## Theory (2 hours)

### 1. What is MCP? (30 min)

**MCP (Model Context Protocol)** is a standard for connecting AI models to external tools and data sources.

```
┌─────────────────────────────────────────────────┐
│              MCP Architecture                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────┐        ┌─────────────┐            │
│  │   AI    │ ←MCP→  │ MCP Server  │            │
│  │ Client  │        │  (Tools)    │            │
│  └─────────┘        └─────────────┘            │
│                            │                    │
│                  ┌─────────┼─────────┐         │
│                  ↓         ↓         ↓         │
│              Database   APIs     Files         │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Why MCP?**
- **Standardized** way to connect AI to tools
- **Secure** — tools run in isolated servers
- **Reusable** — same tools work with any AI client
- **Composable** — mix and match tool servers

### 2. MCP Components (30 min)

| Component | Role |
|-----------|------|
| **MCP Server** | Exposes tools and resources |
| **MCP Client** | Connects AI to servers |
| **Tools** | Functions the AI can call |
| **Resources** | Data the AI can read |
| **Prompts** | Pre-built prompt templates |

### 3. Observability Basics (30 min)

**Why observe AI?**
- Debug failed responses
- Track costs
- Measure quality
- Detect issues

**The Three Pillars:**
1. **Logs** — What happened?
2. **Metrics** — How much? How fast?
3. **Traces** — What was the journey?

### 4. AI-Specific Observability (30 min)

**What to track:**
- Token usage and costs
- Latency per request
- Tool call success/failure
- RAG retrieval quality
- Model response quality

**Tools:**
- **LangSmith** — LangChain ecosystem
- **Helicone** — OpenAI proxy with analytics
- **Arize** — ML observability
- **Custom logging** — Simple but effective

---

## Hands-On Practice (4-6 hours)

### Quick Async Primer (15 min)

MCP uses Python's `async`/`await` syntax. If you're new to async:

```python
# Regular function - runs once, returns result
def get_data():
    return "Hello"

# Async function - can wait for slow operations without blocking
async def get_data_async():
    await some_slow_operation()  # "await" pauses here until done
    return "Hello"

# Running async code
import asyncio

async def main():
    result = await get_data_async()
    print(result)

asyncio.run(main())  # Start the async program
```

**Key concepts:**
- `async def` — declares an async function
- `await` — pause until async operation completes
- `asyncio.run()` — starts the async event loop

Don't worry about deeply understanding async yet — just know that MCP handlers are `async def` functions and you call them with `await`.

---

### Task 1: Simple MCP Server (60 min)

```python
# mcp_server.py
"""
A simple MCP server exposing calculator tools.
Run with: python mcp_server.py
"""
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
import asyncio

# Create server
server = Server("calculator")

# Define tools
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        ),
        types.Tool(
            name="multiply",
            description="Multiply two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, 
    arguments: dict | None
) -> list[types.TextContent]:
    """Execute a tool."""
    
    if not arguments:
        raise ValueError("Arguments required")
    
    if name == "add":
        result = arguments["a"] + arguments["b"]
    elif name == "multiply":
        result = arguments["a"] * arguments["b"]
    else:
        raise ValueError(f"Unknown tool: {name}")
    
    return [types.TextContent(type="text", text=str(result))]

async def main():
    """Run the server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="calculator",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Task 2: MCP Client (45 min)

```python
# mcp_client.py
"""
Connect to an MCP server and use its tools.
"""
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class MCPClient:
    """Simple MCP client for demonstration."""
    
    def __init__(self):
        # In a real MCP client, you'd connect to the server
        # For demo, we simulate the tools
        self.tools = {
            "add": lambda a, b: a + b,
            "multiply": lambda a, b: a * b
        }
        
        self.tool_definitions = [
            {
                "type": "function",
                "function": {
                    "name": "add",
                    "description": "Add two numbers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number"},
                            "b": {"type": "number"}
                        },
                        "required": ["a", "b"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "multiply",
                    "description": "Multiply two numbers",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number"},
                            "b": {"type": "number"}
                        },
                        "required": ["a", "b"]
                    }
                }
            }
        ]
    
    def call_tool(self, name: str, arguments: dict) -> str:
        """Execute a tool."""
        if name in self.tools:
            result = self.tools[name](**arguments)
            return str(result)
        raise ValueError(f"Unknown tool: {name}")
    
    def chat(self, message: str) -> str:
        """Chat with tool access."""
        
        messages = [{"role": "user", "content": message}]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=self.tool_definitions
        )
        
        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = self.call_tool(tc.function.name, args)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
            
            final = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            return final.choices[0].message.content
        
        return msg.content

# Test
if __name__ == "__main__":
    mcp = MCPClient()
    
    queries = [
        "What is 15 + 27?",
        "Multiply 7 by 8",
        "Add 100 and 200, then tell me the result"
    ]
    
    for q in queries:
        print(f"Q: {q}")
        print(f"A: {mcp.chat(q)}\n")
```

### Task 3: Basic Logging (45 min)

```python
# ai_logging.py
"""
Comprehensive logging for AI applications.
"""
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('ai_app')

@dataclass
class AICallLog:
    """Log entry for an AI call."""
    timestamp: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    success: bool
    error: Optional[str] = None
    tool_calls: Optional[List[str]] = None
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))

class AILogger:
    """Logger for AI operations."""
    
    def __init__(self, app_name: str = "ai_app"):
        self.logger = logging.getLogger(app_name)
        self.calls: List[AICallLog] = []
    
    def log_call(
        self,
        model: str,
        response,
        latency_ms: float,
        tool_calls: List[str] = None,
        error: str = None
    ) -> AICallLog:
        """Log an AI API call."""
        
        log_entry = AICallLog(
            timestamp=datetime.now().isoformat(),
            model=model,
            prompt_tokens=response.usage.prompt_tokens if response else 0,
            completion_tokens=response.usage.completion_tokens if response else 0,
            total_tokens=response.usage.total_tokens if response else 0,
            latency_ms=latency_ms,
            success=error is None,
            error=error,
            tool_calls=tool_calls
        )
        
        self.calls.append(log_entry)
        
        if error:
            self.logger.error(f"AI call failed: {log_entry.to_json()}")
        else:
            self.logger.info(f"AI call: {log_entry.to_json()}")
        
        return log_entry
    
    def get_stats(self) -> dict:
        """Get statistics."""
        if not self.calls:
            return {}
        
        total_tokens = sum(c.total_tokens for c in self.calls)
        avg_latency = sum(c.latency_ms for c in self.calls) / len(self.calls)
        success_rate = sum(1 for c in self.calls if c.success) / len(self.calls)
        
        return {
            "total_calls": len(self.calls),
            "total_tokens": total_tokens,
            "average_latency_ms": round(avg_latency, 2),
            "success_rate": round(success_rate * 100, 1),
            "estimated_cost_usd": total_tokens * 0.000002  # Rough estimate
        }

# Usage with OpenAI
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI()
ai_logger = AILogger()

def logged_chat(message: str) -> str:
    """Chat with logging."""
    
    start = time.time()
    error = None
    response = None
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        error = str(e)
        raise
    finally:
        latency = (time.time() - start) * 1000
        ai_logger.log_call(
            model="gpt-4o-mini",
            response=response,
            latency_ms=latency,
            error=error
        )

# Test
if __name__ == "__main__":
    # Make some calls
    logged_chat("Hello!")
    logged_chat("What is 2+2?")
    logged_chat("Tell me a joke")
    
    # Print stats
    print("\n📊 Stats:")
    for k, v in ai_logger.get_stats().items():
        print(f"  {k}: {v}")
```

### Task 4: Request Tracing (60 min)

```python
# tracing.py
"""
Distributed tracing for AI applications.
"""
import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional
from contextlib import contextmanager
import json

@dataclass
class Span:
    """A span in a trace."""
    name: str
    trace_id: str
    span_id: str
    parent_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    attributes: dict = field(default_factory=dict)
    status: str = "OK"
    
    def end(self, status: str = "OK"):
        self.end_time = datetime.now()
        self.status = status
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() * 1000
        return 0
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "duration_ms": round(self.duration_ms, 2),
            "status": self.status,
            "attributes": self.attributes
        }

class Tracer:
    """Simple tracer for AI operations."""
    
    def __init__(self):
        self.traces: dict = {}
        self._current_span: Optional[Span] = None
    
    def start_trace(self, name: str) -> Span:
        """Start a new trace."""
        trace_id = str(uuid.uuid4())[:8]
        span = Span(
            name=name,
            trace_id=trace_id,
            span_id=str(uuid.uuid4())[:8]
        )
        self.traces[trace_id] = [span]
        self._current_span = span
        return span
    
    def start_span(self, name: str) -> Span:
        """Start a child span."""
        if not self._current_span:
            return self.start_trace(name)
        
        span = Span(
            name=name,
            trace_id=self._current_span.trace_id,
            span_id=str(uuid.uuid4())[:8],
            parent_id=self._current_span.span_id
        )
        self.traces[span.trace_id].append(span)
        parent = self._current_span
        self._current_span = span
        return span
    
    @contextmanager
    def span(self, name: str, **attributes):
        """Context manager for spans."""
        s = self.start_span(name)
        s.attributes = attributes
        try:
            yield s
        except Exception as e:
            s.attributes["error"] = str(e)
            s.end("ERROR")
            raise
        finally:
            s.end()
    
    def print_trace(self, trace_id: str):
        """Print a trace."""
        if trace_id not in self.traces:
            print(f"Trace {trace_id} not found")
            return
        
        print(f"\n🔍 Trace: {trace_id}")
        for span in self.traces[trace_id]:
            indent = "  " if span.parent_id else ""
            status = "✓" if span.status == "OK" else "✗"
            print(f"{indent}{status} {span.name} ({span.duration_ms}ms)")
            if span.attributes:
                for k, v in span.attributes.items():
                    print(f"{indent}    {k}: {v}")

# Global tracer
tracer = Tracer()

# Example usage with RAG
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def traced_rag_query(question: str) -> str:
    """RAG query with tracing."""
    
    with tracer.span("rag_query", question=question) as root:
        
        # Embedding
        with tracer.span("create_embedding"):
            emb_response = client.embeddings.create(
                model="text-embedding-3-small",
                input=question
            )
        
        # Simulated search
        with tracer.span("vector_search", top_k=3):
            import time
            time.sleep(0.1)  # Simulate search
            docs = ["Doc 1", "Doc 2", "Doc 3"]
        
        # LLM call
        with tracer.span("llm_generate") as llm_span:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": f"Context: {docs}\n\nQ: {question}"}
                ]
            )
            llm_span.attributes["tokens"] = response.usage.total_tokens
        
        return response.choices[0].message.content

# Test
if __name__ == "__main__":
    result = traced_rag_query("What is machine learning?")
    print(f"\nAnswer: {result}")
    
    # Print the trace
    trace_id = list(tracer.traces.keys())[0]
    tracer.print_trace(trace_id)
```

### Task 5: Metrics Collection (45 min)

```python
# metrics.py
"""
Collect and report metrics for AI applications.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List
import time

class MetricsCollector:
    """Collects AI application metrics."""
    
    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.start_time = datetime.now()
    
    def increment(self, name: str, value: int = 1):
        """Increment a counter."""
        self.counters[name] += value
    
    def set_gauge(self, name: str, value: float):
        """Set a gauge value."""
        self.gauges[name] = value
    
    def record(self, name: str, value: float):
        """Record a histogram value."""
        self.histograms[name].append(value)
    
    def get_histogram_stats(self, name: str) -> dict:
        """Get histogram statistics."""
        values = self.histograms.get(name, [])
        if not values:
            return {}
        
        sorted_vals = sorted(values)
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "p50": sorted_vals[len(sorted_vals) // 2],
            "p95": sorted_vals[int(len(sorted_vals) * 0.95)] if len(sorted_vals) >= 20 else max(values)
        }
    
    def report(self) -> dict:
        """Generate metrics report."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            "uptime_seconds": round(uptime, 2),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "histograms": {
                name: self.get_histogram_stats(name)
                for name in self.histograms
            }
        }
        
        return report
    
    def print_report(self):
        """Print a formatted report."""
        report = self.report()
        
        print("\n📊 Metrics Report")
        print("=" * 40)
        print(f"Uptime: {report['uptime_seconds']}s")
        
        print("\nCounters:")
        for name, value in report['counters'].items():
            print(f"  {name}: {value}")
        
        print("\nGauges:")
        for name, value in report['gauges'].items():
            print(f"  {name}: {value}")
        
        print("\nHistograms:")
        for name, stats in report['histograms'].items():
            print(f"  {name}:")
            for k, v in stats.items():
                print(f"    {k}: {round(v, 2)}")

# Global metrics
metrics = MetricsCollector()

# Decorator for timing
def timed(metric_name: str):
    """Decorator to time function execution."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                metrics.increment(f"{metric_name}_success")
                return result
            except Exception as e:
                metrics.increment(f"{metric_name}_error")
                raise
            finally:
                latency = (time.time() - start) * 1000
                metrics.record(f"{metric_name}_latency_ms", latency)
        return wrapper
    return decorator

# Usage
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

@timed("chat_completion")
def chat(message: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": message}]
    )
    
    # Record token usage
    metrics.increment("total_tokens", response.usage.total_tokens)
    metrics.set_gauge("last_response_tokens", response.usage.total_tokens)
    
    return response.choices[0].message.content

# Test
if __name__ == "__main__":
    # Make some calls
    for i in range(5):
        chat(f"Say hello {i}")
    
    # Print report
    metrics.print_report()
```

### Task 6: Observability Dashboard (45 min)

```python
# dashboard.py
"""
Simple observability dashboard combining all components.
"""
from ai_logging import AILogger, logged_chat
from tracing import Tracer, tracer
from metrics import MetricsCollector, metrics
from datetime import datetime
import json

class AIObservability:
    """Combined observability for AI applications."""
    
    def __init__(self):
        self.logger = AILogger("ai_dashboard")
        self.tracer = Tracer()
        self.metrics = MetricsCollector()
    
    def monitored_call(self, message: str) -> dict:
        """Make a monitored AI call."""
        import time
        from openai import OpenAI
        from dotenv import load_dotenv
        
        load_dotenv()
        client = OpenAI()
        
        # Start trace
        with self.tracer.span("ai_call", input=message[:50]) as span:
            start = time.time()
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": message}]
                )
                
                latency = (time.time() - start) * 1000
                
                # Log
                self.logger.log_call(
                    model="gpt-4o-mini",
                    response=response,
                    latency_ms=latency
                )
                
                # Metrics
                self.metrics.increment("calls_success")
                self.metrics.record("latency_ms", latency)
                self.metrics.increment("tokens_used", response.usage.total_tokens)
                
                span.attributes["tokens"] = response.usage.total_tokens
                span.attributes["latency_ms"] = latency
                
                return {
                    "success": True,
                    "response": response.choices[0].message.content,
                    "tokens": response.usage.total_tokens,
                    "latency_ms": latency
                }
                
            except Exception as e:
                self.metrics.increment("calls_error")
                span.attributes["error"] = str(e)
                span.end("ERROR")
                
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def dashboard(self) -> str:
        """Generate dashboard view."""
        
        stats = self.logger.get_stats()
        metrics_report = self.metrics.report()
        
        dashboard = f"""
╔══════════════════════════════════════════════════════════╗
║                   AI OBSERVABILITY DASHBOARD              ║
╠══════════════════════════════════════════════════════════╣
║ Uptime: {metrics_report['uptime_seconds']:.1f}s                                         ║
╠══════════════════════════════════════════════════════════╣
║ CALLS                                                     ║
║   Total: {stats.get('total_calls', 0):<10} Success Rate: {stats.get('success_rate', 0)}%                ║
╠══════════════════════════════════════════════════════════╣
║ TOKENS                                                    ║
║   Total Used: {stats.get('total_tokens', 0):<10}                                 ║
║   Est. Cost:  ${stats.get('estimated_cost_usd', 0):.4f}                                ║
╠══════════════════════════════════════════════════════════╣
║ LATENCY                                                   ║
║   Average: {stats.get('average_latency_ms', 0):.1f}ms                                      ║
╚══════════════════════════════════════════════════════════╝
"""
        return dashboard

# Test
if __name__ == "__main__":
    obs = AIObservability()
    
    # Make some calls
    print("Making test calls...")
    for prompt in ["Hello!", "What is AI?", "Tell me a joke"]:
        result = obs.monitored_call(prompt)
        print(f"  ✓ {prompt[:20]}... ({result.get('latency_ms', 0):.0f}ms)")
    
    # Show dashboard
    print(obs.dashboard())
```

---

## Knowledge Checklist

- [ ] I understand what MCP is and how it works
- [ ] I can create a simple MCP server
- [ ] I can connect an AI to MCP tools
- [ ] I can implement logging for AI calls
- [ ] I can create traces for request flow
- [ ] I can collect and report metrics

---

## Deliverables

1. `mcp_server.py` — Simple MCP server
2. `mcp_client.py` — MCP client integration
3. `ai_logging.py` — AI-specific logging
4. `tracing.py` — Request tracing
5. `metrics.py` — Metrics collection
6. `dashboard.py` — Combined observability

---

## What's Next?

Next week: **Production Hardening** — rate limiting, caching, failover, and reliability patterns!

---

## Resources

- [MCP Specification](https://modelcontextprotocol.io/docs)
- [OpenTelemetry for AI](https://opentelemetry.io/)
- [LangSmith](https://docs.smith.langchain.com/)
