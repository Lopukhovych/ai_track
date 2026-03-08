# Week 10: LangGraph in Practice + LangSmith & Langfuse

**Month:** 3 (Intelligence) | **Duration:** 8-10 hours

---

## Overview

Week 9 gave you LangGraph theory — all five workflow patterns, checkpointing, human-in-the-loop, and memory. This week you **build** with it. You'll implement the key patterns as running code, then hook them up to **LangSmith** and **Langfuse** — the two dominant observability platforms for LLM applications. By the end you'll be able to trace every token, inspect every tool call, and evaluate agent quality in a real dashboard.

---

## Learning Objectives

By the end of this week, you will:
- Build chaining, routing, and evaluator-optimizer LangGraph patterns from scratch
- Add checkpointing and human-in-the-loop to a working agent
- Connect a LangGraph agent to LangSmith for automatic tracing
- Self-host or use cloud Langfuse for open-source observability
- Create evaluation datasets and run LLM-as-judge in both platforms
- Understand when to use LangSmith vs Langfuse vs custom logging

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| LangGraph agent | `gpt-5-mini` | `llama3.1:8b` |
| LLM-as-judge evaluation | `gpt-5-mini` | `qwq:32b` or `llama3.1:8b` |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b
```

```python
from scripts.model_config import get_client, CHAT_MODEL, REASON_MODEL
```

> Both LangSmith and Langfuse are provider-agnostic — they trace any LLM call regardless of whether you use OpenAI or Ollama.

---

## Theory (2 hours)

### 1. LangGraph Patterns Recap (30 min)

You learned these in week 9. Quick reference before implementation:

| Pattern | Shape | Use When |
|---------|-------|----------|
| **Chaining** | A → B → C | Fixed sequential steps |
| **Parallelization** | A → B+C → D | Independent sub-tasks |
| **Routing** | A → if/else → B or C | Input-dependent branching |
| **Orchestrator-Worker** | A → [B, C, D dynamic] | Unknown number of sub-tasks |
| **Evaluator-Optimizer** | A → B → judge → loop | Output quality must meet threshold |

**The compile-run-inspect cycle:**

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

app = builder.compile(checkpointer=MemorySaver())

# Thread config enables checkpointing and state history
config = {"configurable": {"thread_id": "t1"}}
result = app.invoke({"input": "..."}, config)

# Inspect state at any point
snapshot = app.get_state(config)
print(snapshot.values)   # current state dict
print(snapshot.next)     # what node runs next (empty if done)

# Full history (every checkpoint)
for step in app.get_state_history(config):
    print(step.values, step.next)
```

### 2. LangSmith (45 min)

**What it is:** LangChain's hosted observability and evaluation platform. Zero code changes needed — set two env vars and every LangChain/LangGraph call appears in the dashboard as a traced tree.

**Core features:**

| Feature | What it does |
|---------|-------------|
| **Automatic tracing** | Every LangGraph run is a full trace tree |
| **Run details** | Input/output, tokens, latency, cost per node |
| **Datasets** | Golden Q&A pairs for regression testing |
| **Evaluators** | LLM-as-judge, exact match, embedding similarity |
| **Prompt Hub** | Version-controlled, shareable prompt templates |

**Setup (under 2 minutes):**
```bash
pip install langsmith langchain-openai langgraph
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=ls-...        # from smith.langchain.com
export LANGCHAIN_PROJECT=week-10       # groups traces by project
```

That is all. Now every `app.invoke()` call auto-traces to `smith.langchain.com`.

**Running a programmatic evaluation:**
```python
from langsmith import Client
from langsmith.evaluation import evaluate
from langchain_openai import ChatOpenAI

client = Client()
llm = ChatOpenAI(model="gpt-5-mini")

# 1. Build a dataset
dataset = client.create_dataset("rag-eval-v1")
client.create_examples(
    inputs=[{"question": "What is RAG?"}],
    outputs=[{"answer": "Retrieval-Augmented Generation combines search with LLM generation"}],
    dataset_id=dataset.id
)

# 2. Define an LLM-as-judge evaluator
def correctness(run, example):
    score_text = llm.invoke(
        f"Rate 0-1: Expected='{example.outputs['answer']}' Got='{run.outputs['answer']}'. Reply with float only."
    ).content
    return {"key": "correctness", "score": float(score_text.strip())}

# 3. Run evaluation
results = evaluate(
    lambda inputs: {"answer": my_rag_chain(inputs["question"])},
    data=dataset.name,
    evaluators=[correctness],
    experiment_prefix="baseline"
)
```

### 3. Langfuse (45 min)

**What it is:** Open-source LLM observability. Self-host for full data privacy, or use Langfuse Cloud. Works with any LLM stack — not tied to LangChain.

**Core features:**

| Feature | What it does |
|---------|-------------|
| **Traces** | Hierarchical spans per LLM/function call |
| **Scores** | Attach numeric or boolean quality signals |
| **Datasets** | Evaluation sets with expected outputs |
| **Prompt Management** | Version prompts, track which version ran per trace |
| **Cost tracking** | Token usage and estimated cost per trace |
| **Self-hostable** | Free Docker Compose deployment |

**Setup options:**
```bash
# Option A: Langfuse Cloud (easiest)
pip install langfuse
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
# No LANGFUSE_HOST needed — defaults to cloud.langfuse.com

# Option B: Self-hosted (full privacy)
git clone https://github.com/langfuse/langfuse && cd langfuse
cp .env.langfuse.example .env   # edit with random NEXTAUTH_SECRET, SALT
docker compose up -d
# UI at http://localhost:3000 — create API keys there
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_HOST=http://localhost:3000
```

**Two integration styles:**

```python
# Style 1: @observe decorator (zero-boilerplate)
from langfuse.decorators import observe, langfuse_context

@observe()
def my_pipeline(question: str) -> str:
    answer = call_llm(question)
    langfuse_context.score_current_trace(name="relevance", value=0.9)
    return answer

# Style 2: LangChain CallbackHandler (for LangGraph)
from langfuse.callback import CallbackHandler

handler = CallbackHandler()   # reads env vars automatically
result = app.invoke(input, config={"callbacks": [handler]})

# Attach a manual score after the fact
from langfuse import Langfuse
lf = Langfuse()
lf.score(trace_id=handler.get_trace_id(), name="helpfulness", value=1.0)
lf.flush()   # always flush before process exit
```

### 4. LangSmith vs Langfuse vs Custom (15 min)

| | LangSmith | Langfuse | Custom (week 12) |
|---|-----------|----------|----------------|
| **Setup** | 2 env vars | 2 env vars | Write code |
| **Self-hosted** | No | Yes (free) | Yes |
| **LangGraph native** | Yes, automatic | Via callback | Manual |
| **Non-LangChain** | Limited | First-class | Full control |
| **Eval datasets** | Yes | Yes | Build yourself |
| **Prompt management** | Prompt Hub | Prompts UI | None |
| **Cost** | Free tier + paid | Free OSS | Your infra cost |

**Decision guide:**
- Use **LangSmith** when: your stack is LangChain/LangGraph and setup time matters.
- Use **Langfuse** when: you need self-hosted, non-LangChain SDKs, or team-level prompt management.
- Use **custom logging** when: you need to integrate with existing APM (Datadog, Azure Monitor) or need both.

---

## Hands-On Practice (4-6 hours)

### Task 1: LangGraph Chaining + Routing (60 min)

Build two patterns as standalone scripts:

```python
# langgraph_patterns.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Literal

llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

# ---- Pattern 1: Chaining (summarize → translate → format) ----

class ChainState(TypedDict):
    text: str
    summary: str
    translated: str
    final: str

def summarize(state: ChainState) -> dict:
    r = llm.invoke([SystemMessage("Summarize in one sentence."), HumanMessage(state["text"])])
    return {"summary": r.content}

def translate_to_french(state: ChainState) -> dict:
    r = llm.invoke([SystemMessage("Translate to French."), HumanMessage(state["summary"])])
    return {"translated": r.content}

def format_output(state: ChainState) -> dict:
    return {"final": f"FR: {state['translated']}"}

chain = StateGraph(ChainState)
chain.add_node("summarize", summarize)
chain.add_node("translate", translate_to_french)
chain.add_node("format", format_output)
chain.add_edge(START, "summarize")
chain.add_edge("summarize", "translate")
chain.add_edge("translate", "format")
chain.add_edge("format", END)
chain_app = chain.compile()

# ---- Pattern 2: Routing (classify → specialist) ----

class RouteState(TypedDict):
    question: str
    category: str
    answer: str

def classify(state: RouteState) -> dict:
    r = llm.invoke([
        SystemMessage('Classify the question. Reply with exactly one word: "math", "science", or "general"'),
        HumanMessage(state["question"])
    ])
    return {"category": r.content.strip().lower()}

def route(state: RouteState) -> Literal["math_expert", "science_expert", "general_assistant"]:
    c = state["category"]
    if "math" in c:
        return "math_expert"
    if "science" in c:
        return "science_expert"
    return "general_assistant"

def math_expert(state: RouteState) -> dict:
    r = llm.invoke([SystemMessage("You are a math expert."), HumanMessage(state["question"])])
    return {"answer": r.content}

def science_expert(state: RouteState) -> dict:
    r = llm.invoke([SystemMessage("You are a science expert."), HumanMessage(state["question"])])
    return {"answer": r.content}

def general_assistant(state: RouteState) -> dict:
    r = llm.invoke([HumanMessage(state["question"])])
    return {"answer": r.content}

router = StateGraph(RouteState)
for name, fn in [("classify", classify), ("math_expert", math_expert),
                  ("science_expert", science_expert), ("general_assistant", general_assistant)]:
    router.add_node(name, fn)
router.add_edge(START, "classify")
router.add_conditional_edges("classify", route)
for n in ["math_expert", "science_expert", "general_assistant"]:
    router.add_edge(n, END)
route_app = router.compile()

if __name__ == "__main__":
    # Chaining
    r = chain_app.invoke({"text": "The mitochondria is the powerhouse of the cell and produces ATP."})
    print("Chain:", r["final"])

    # Routing
    for q in ["What is 2+2?", "Why is the sky blue?", "Tell me a joke"]:
        r = route_app.invoke({"question": q})
        print(f"Route [{r['category']}]: {r['answer'][:60]}...")
```

### Task 2: Evaluator-Optimizer with Checkpointing (60 min)

```python
# evaluator_optimizer.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Literal
import json, re

llm = ChatOpenAI(model="gpt-5-mini", temperature=0.7)
judge_llm = ChatOpenAI(model="gpt-5-mini", temperature=0)

MAX_ITER = 3
THRESHOLD = 0.8

class EvalState(TypedDict):
    task: str
    draft: str
    feedback: str
    score: float
    iterations: int
    final: str

def generate(state: EvalState) -> dict:
    prompt = state["task"]
    if state.get("feedback"):
        prompt += f"\n\nPrevious feedback to address:\n{state['feedback']}"
    r = llm.invoke([SystemMessage("You are a skilled writer. Produce high-quality output."), HumanMessage(prompt)])
    return {"draft": r.content, "iterations": state.get("iterations", 0) + 1}

def evaluate(state: EvalState) -> dict:
    r = judge_llm.invoke([
        SystemMessage('Judge this output 0.0-1.0. Respond as JSON: {"score": 0.7, "feedback": "..."}'),
        HumanMessage(f"Task: {state['task']}\n\nOutput:\n{state['draft']}")
    ])
    match = re.search(r'\{.*\}', r.content, re.DOTALL)
    data = json.loads(match.group()) if match else {"score": 0.5, "feedback": "No feedback"}
    return {"score": data["score"], "feedback": data["feedback"]}

def should_continue(state: EvalState) -> Literal["generate", "accept"]:
    return "accept" if state["score"] >= THRESHOLD or state["iterations"] >= MAX_ITER else "generate"

def accept(state: EvalState) -> dict:
    return {"final": state["draft"]}

builder = StateGraph(EvalState)
builder.add_node("generate", generate)
builder.add_node("evaluate", evaluate)
builder.add_node("accept", accept)
builder.add_edge(START, "generate")
builder.add_edge("generate", "evaluate")
builder.add_conditional_edges("evaluate", should_continue)
builder.add_edge("accept", END)

app = builder.compile(checkpointer=MemorySaver())

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "eval-demo"}}
    result = app.invoke(
        {"task": "Write a 2-sentence pitch for an AI observability tool.", "iterations": 0},
        config=config
    )

    print(f"Iterations: {result['iterations']} | Score: {result['score']:.2f}")
    print(f"Output: {result['final']}")

    # Show all checkpointed states
    history = list(app.get_state_history(config))
    print(f"\n{len(history)} checkpoints saved")
    for step in reversed(history):
        print(f"  → {step.next or ['END']} | score={step.values.get('score', '-')}")
```

### Task 3: Human-in-the-Loop Agent (60 min)

```python
# human_in_loop.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Annotated
import operator

llm = ChatOpenAI(model="gpt-5-mini")

class ReviewState(TypedDict):
    messages: Annotated[list, operator.add]
    draft_action: str
    approved: bool

def plan_action(state: ReviewState) -> dict:
    response = llm.invoke(state["messages"] + [
        HumanMessage("What specific action should we take? Be concrete.")
    ])
    return {"messages": [AIMessage(response.content)], "draft_action": response.content}

def human_review(state: ReviewState) -> dict:
    # interrupt() pauses graph; resumes after app.update_state()
    decision = interrupt({
        "question": "Approve this action?",
        "action": state["draft_action"]
    })
    approved = str(decision).lower() in ("yes", "y", "approve")
    return {
        "approved": approved,
        "messages": [HumanMessage(f"Decision: {'approved' if approved else 'rejected'}")]
    }

def execute_action(state: ReviewState) -> dict:
    r = llm.invoke([HumanMessage(f"Execute this: {state['draft_action']}")])
    return {"messages": [AIMessage(f"Done: {r.content[:100]}")]}

def reject_action(state: ReviewState) -> dict:
    return {"messages": [AIMessage("Action rejected. No changes made.")]}

builder = StateGraph(ReviewState)
builder.add_node("plan", plan_action)
builder.add_node("review", human_review)
builder.add_node("execute", execute_action)
builder.add_node("reject", reject_action)
builder.add_edge(START, "plan")
builder.add_edge("plan", "review")
builder.add_conditional_edges(
    "review",
    lambda s: "execute" if s["approved"] else "reject"
)
builder.add_edge("execute", END)
builder.add_edge("reject", END)

app = builder.compile(checkpointer=MemorySaver(), interrupt_before=["review"])

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "review-demo"}}

    # Run until interrupt
    app.invoke(
        {"messages": [HumanMessage("Archive all log files older than 90 days.")], "approved": False},
        config=config
    )

    snapshot = app.get_state(config)
    print(f"Paused before: {snapshot.next}")
    print(f"Proposed: {snapshot.values['draft_action'][:100]}")

    # Human approves
    decision = input("Approve? (yes/no): ").strip()
    app.update_state(config, {"approved": decision.lower() in ("yes", "y")}, as_node="review")

    # Resume
    final = app.invoke(None, config)
    for msg in final["messages"][-2:]:
        print(f"[{type(msg).__name__}]: {msg.content[:80]}")
```

### Task 4: LangSmith Tracing + Evaluation (45 min)

```bash
pip install langsmith langchain-openai langgraph
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=ls-...
export LANGCHAIN_PROJECT=week-10-practice
```

```python
# langsmith_tracing.py
from langsmith import Client, traceable
from langsmith.evaluation import evaluate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

client = Client()
llm = ChatOpenAI(model="gpt-5-mini")

# @traceable adds a named span — appears nested inside auto-traces
@traceable(name="retrieval")
def fake_retrieval(query: str) -> list[str]:
    return [f"Doc 1 about {query}: relevant content here", f"Doc 2 about {query}: more context"]

@traceable(name="rag_pipeline")
def rag_answer(question: str) -> str:
    docs = fake_retrieval(question)
    context = "\n".join(docs)
    r = llm.invoke([HumanMessage(f"Context:\n{context}\n\nQuestion: {question}")])
    return r.content

# --- Dataset setup ---
def get_or_create_dataset(name: str) -> str:
    existing = [d.name for d in client.list_datasets()]
    if name not in existing:
        ds = client.create_dataset(name)
        client.create_examples(
            inputs=[
                {"question": "What is LangGraph?"},
                {"question": "What is LangSmith?"},
                {"question": "How does RAG work?"},
            ],
            outputs=[
                {"answer": "LangGraph is a framework for building stateful agent workflows using directed graphs"},
                {"answer": "LangSmith is an observability and evaluation platform for LLM applications"},
                {"answer": "RAG retrieves relevant documents and injects them as context for the LLM to answer"},
            ],
            dataset_id=ds.id
        )
        print(f"Created dataset: {name}")
    return name

# --- LLM-as-judge evaluator ---
def correctness_evaluator(run, example):
    r = llm.invoke([HumanMessage(
        f"Rate correctness 0.0-1.0. Expected: '{example.outputs['answer']}'. "
        f"Got: '{run.outputs['output']}'. Reply with float only."
    )])
    try:
        score = float(r.content.strip())
    except:
        score = 0.5
    return {"key": "correctness", "score": min(1.0, max(0.0, score))}

if __name__ == "__main__":
    # Test traced pipeline
    answer = rag_answer("What is LangGraph?")
    print(f"Answer: {answer[:100]}")
    print("-> Check smith.langchain.com for the trace!\n")

    # Run evaluation
    dataset_name = get_or_create_dataset("week10-rag-eval")
    results = evaluate(
        lambda inputs: {"output": rag_answer(inputs["question"])},
        data=dataset_name,
        evaluators=[correctness_evaluator],
        experiment_prefix="week10-baseline",
        max_concurrency=1
    )
    print(f"Evaluation complete — see results at smith.langchain.com/datasets")
```

### Task 5: Langfuse Tracing (45 min)

```bash
# Self-hosted setup
git clone https://github.com/langfuse/langfuse && cd langfuse
cp .env.langfuse.example .env
# Edit .env: set NEXTAUTH_SECRET and SALT to random strings
docker compose up -d
# Create API keys at http://localhost:3000 -> Settings -> API Keys

pip install langfuse
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
export LANGFUSE_HOST=http://localhost:3000
```

```python
# langfuse_tracing.py
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context
from langfuse.callback import CallbackHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
import operator

langfuse = Langfuse()
llm = ChatOpenAI(model="gpt-5-mini")

# ---- Style 1: @observe decorator ----
@observe(name="retrieval")
def retrieve_docs(query: str) -> list[str]:
    return [f"Document 1 about {query}", f"Document 2 about {query}"]

@observe(name="generate_answer")
def generate(question: str, docs: list[str]) -> str:
    context = "\n".join(docs)
    r = llm.invoke([HumanMessage(f"Context: {context}\n\nQ: {question}")])
    langfuse_context.update_current_observation(
        input=question,
        output=r.content,
        metadata={"doc_count": len(docs)}
    )
    return r.content

@observe(name="rag_pipeline")
def rag_with_score(question: str) -> str:
    docs = retrieve_docs(question)
    answer = generate(question, docs)
    # Score the root trace
    langfuse_context.score_current_trace(name="relevance", value=0.85, comment="heuristic")
    return answer

# ---- Style 2: LangGraph + CallbackHandler ----
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

def call_model(state: AgentState) -> dict:
    r = llm.invoke(state["messages"])
    return {"messages": [r]}

builder = StateGraph(AgentState)
builder.add_node("agent", call_model)
builder.add_edge(START, "agent")
builder.add_edge("agent", END)
agent_app = builder.compile()

def run_agent_traced(question: str):
    handler = CallbackHandler()  # reads env vars
    result = agent_app.invoke(
        {"messages": [HumanMessage(question)]},
        config={"callbacks": [handler]}
    )
    langfuse.score(
        trace_id=handler.get_trace_id(),
        name="helpfulness",
        value=1.0,
        comment="manual test score"
    )
    return result

if __name__ == "__main__":
    print("Testing @observe style...")
    answer = rag_with_score("Explain checkpointing in LangGraph")
    print(f"Answer: {answer[:100]}")

    print("\nTesting LangGraph + callback style...")
    result = run_agent_traced("What is Langfuse?")
    print(f"Agent: {result['messages'][-1].content[:100]}")

    langfuse.flush()
    print("\n-> Check http://localhost:3000 for traces!")
```

### Task 6: Langfuse Evaluation Datasets (45 min)

```python
# langfuse_eval.py
from langfuse import Langfuse
from langfuse.decorators import observe
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

langfuse = Langfuse()
llm = ChatOpenAI(model="gpt-5-mini")

def setup_dataset(name: str):
    try:
        return langfuse.get_dataset(name)
    except Exception:
        ds = langfuse.create_dataset(name, description="LangGraph QA pairs")
        items = [
            ("What is a StateGraph?",
             "A StateGraph is a directed graph in LangGraph where nodes receive and return typed state"),
            ("What is a reducer in LangGraph?",
             "A reducer merges node output into existing state, declared via Annotated type hints"),
            ("What does interrupt() do?",
             "interrupt() pauses graph execution at a node boundary, waiting for human input via update_state()"),
        ]
        for q, a in items:
            langfuse.create_dataset_item(dataset_name=name, input={"question": q}, expected_output={"answer": a})
        print(f"Created dataset '{name}' with {len(items)} items")
        return langfuse.get_dataset(name)

@observe()
def answer_question(question: str) -> str:
    r = llm.invoke([HumanMessage(question)])
    return r.content

def run_evaluation(dataset, experiment_name: str):
    for item in dataset.items:
        q = item.input["question"]
        expected = item.expected_output["answer"]

        with item.observe(run_name=experiment_name) as handler:
            answer = answer_question(q)

            # LLM-as-judge score
            judge_r = llm.invoke([HumanMessage(
                f"Rate 0.0-1.0 how well this captures the key idea.\n"
                f"Expected: {expected}\nGot: {answer}\nReply with a float only."
            )])
            try:
                score = float(judge_r.content.strip())
            except:
                score = 0.5

            langfuse.score(
                trace_id=handler.get_trace_id(),
                name="semantic_match",
                value=min(1.0, max(0.0, score))
            )
            print(f"  Q: {q[:50]}... | Score: {score:.2f}")

if __name__ == "__main__":
    dataset = setup_dataset("week10-langgraph-qa")
    print("\nRunning evaluation...")
    run_evaluation(dataset, "gpt-5-mini-baseline")
    langfuse.flush()
    print("\n-> Check Langfuse > Datasets for scores!")
```

### Task 7: Dual Tracing — LangSmith + Langfuse Simultaneously (30 min)

```python
# dual_tracing.py
"""Both platforms trace the same LangGraph run at once."""
from langfuse.callback import CallbackHandler as LangfuseHandler
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
from langfuse import Langfuse

# LangSmith traces via env var LANGCHAIN_TRACING_V2=true (automatic)
# Langfuse traces via explicit callback
langfuse_handler = LangfuseHandler()
langfuse = Langfuse()
llm = ChatOpenAI(model="gpt-5-mini")

@tool
def count_words(text: str) -> int:
    """Count the number of words in text."""
    return len(text.split())

@tool
def reverse_text(text: str) -> str:
    """Reverse a string character by character."""
    return text[::-1]

tools = [count_words, reverse_text]
llm_with_tools = llm.bind_tools(tools)

def agent_node(state: MessagesState) -> dict:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def should_continue(state: MessagesState):
    return "tools" if state["messages"][-1].tool_calls else END

builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", should_continue)
builder.add_edge("tools", "agent")
app = builder.compile()

if __name__ == "__main__":
    question = "How many words are in 'Hello world from LangGraph'? Then reverse that phrase."
    result = app.invoke(
        {"messages": [HumanMessage(question)]},
        config={"callbacks": [langfuse_handler]}  # LangSmith is auto
    )

    for msg in result["messages"]:
        label = type(msg).__name__
        content = msg.content or str(msg.tool_calls)
        print(f"[{label}]: {str(content)[:80]}")

    langfuse_handler.langfuse.flush()
    print("\n-> Check smith.langchain.com AND your Langfuse dashboard")
```

---

## Knowledge Checklist

- [ ] I can build chaining, routing, and evaluator-optimizer patterns in LangGraph
- [ ] I can add checkpointing and inspect state history with `get_state_history()`
- [ ] I can implement human-in-the-loop with `interrupt()` and `update_state()`
- [ ] LangSmith is set up and I can see my agent traces in the dashboard
- [ ] I can create evaluation datasets and run LLM-as-judge in LangSmith
- [ ] Langfuse is running (cloud or self-hosted) and I can see traces
- [ ] I can use both `@observe` and `CallbackHandler` with Langfuse
- [ ] I can attach scores to traces in Langfuse and run dataset evaluations
- [ ] I understand when to choose LangSmith vs Langfuse vs custom logging

---

## Deliverables

1. `langgraph_patterns.py` — Chaining and routing workflows
2. `evaluator_optimizer.py` — Quality loop with checkpointing
3. `human_in_loop.py` — Human approval workflow
4. `langsmith_tracing.py` — LangSmith traces + evaluation dataset
5. `langfuse_tracing.py` — Langfuse `@observe` + `CallbackHandler`
6. `langfuse_eval.py` — Langfuse dataset evaluation + scoring
7. `dual_tracing.py` — Simultaneous LangSmith + Langfuse

---

## What's Next?

Next week: **Agent Frameworks + Multi-Modal AI** — advanced LangGraph patterns (orchestrator-worker, deep agents, multi-agent with Strands Agents) and Vision/Audio APIs!

---

## Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph Checkpointing](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangSmith Docs](https://docs.smith.langchain.com/)
- [LangSmith Evaluation Guide](https://docs.smith.langchain.com/evaluation)
- [Langfuse Docs](https://langfuse.com/docs)
- [Langfuse Self-Hosting](https://langfuse.com/docs/deployment/self-host)
- [Langfuse LangChain Integration](https://langfuse.com/docs/integrations/langchain)
