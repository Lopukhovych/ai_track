# Week 9: Agent Frameworks — LangGraph Deep Dive & Multi-Modal AI

**Month:** 3 (Intelligence) | **Duration:** 8-12 hours

---

## Overview

Building agents from scratch is educational, but production systems need **orchestration frameworks**. This week you'll get a deep dive into **LangGraph** — the industry standard for stateful agent workflows — covering its core architecture, all major workflow patterns, checkpointing, human-in-the-loop, and memory. You'll also learn **CrewAI** for multi-agent collaboration and explore **Vision/Audio** APIs for multi-modal applications.

---

## Learning Objectives

By the end of this week, you will:
- Understand LangGraph's core architecture (StateGraph, nodes, edges, reducers)
- Know the five fundamental workflow patterns (chaining, parallelization, routing, orchestrator-worker, evaluator-optimizer)
- Distinguish agents from workflows and know when to use each
- Implement checkpointing and durable execution
- Build human-in-the-loop workflows
- Use short-term and long-term memory in LangGraph
- Create multi-agent teams with CrewAI
- Work with Vision and Audio APIs for multi-modal AI

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| LangGraph agents / chat | `gpt-4o-mini` | `llama3.1:8b` |
| Vision / image understanding | `gpt-4o` | `llama3.2-vision:11b` or `llava:7b` |
| Audio transcription (Whisper) | OpenAI Whisper API | `whisper` via `ollama run whisper` |
| Multi-agent orchestration | `gpt-4o-mini` | `llama3.1:8b` |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b           # agents and chat
ollama pull llama3.2-vision:11b   # vision tasks (~7GB); or llava:7b (~4GB)
```

```python
from scripts.model_config import get_client, CHAT_MODEL, VISION_MODEL
# LangGraph works with any OpenAI-compatible client — just swap the model
```

> For vision tasks: `llama3.2-vision:11b` offers better instruction following; `llava:7b` is lighter and faster.

---

## Theory

### 1. LangGraph Architecture (45 min)

LangGraph is a **low-level orchestration framework** for building stateful, long-running agents. It uses a directed graph to represent the flow of execution.

**Core primitives:**

| Primitive | Role |
|-----------|------|
| **StateGraph** | The graph container; defines state schema |
| **State** | Typed dict flowing through all nodes |
| **Node** | A Python function that reads state and returns updates |
| **Edge** | A connection between nodes (fixed or conditional) |
| **Reducer** | Function that merges node output into existing state |
| **Checkpointer** | Persists state between steps (enables durability) |

**How state flows:**

```
┌────────┐    state     ┌──────────┐    state     ┌──────────┐
│  START │ ──────────→  │  Node A  │ ──────────→  │  Node B  │
└────────┘              └──────────┘              └──────────┘
                             ↑ state update merged by reducer
```

**The reducer pattern:**

```python
from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    # operator.add merges lists: existing + new
    messages: Annotated[list, operator.add]
    # No annotation = replace (last write wins)
    step: str
```

**Building a minimal graph:**

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class State(TypedDict):
    value: int

def add_one(state: State) -> dict:
    return {"value": state["value"] + 1}

def double(state: State) -> dict:
    return {"value": state["value"] * 2}

graph = StateGraph(State)
graph.add_node("add_one", add_one)
graph.add_node("double", double)
graph.add_edge(START, "add_one")
graph.add_edge("add_one", "double")
graph.add_edge("double", END)

app = graph.compile()
result = app.invoke({"value": 3})
# value: (3 + 1) * 2 = 8
```

---

### 2. Five Workflow Patterns (60 min)

These patterns cover the vast majority of real-world agent needs.

#### Pattern 1: Prompt Chaining

Sequential LLM calls where each step processes the previous output. Best for tasks with well-defined, verifiable stages.

```
Input → [LLM 1] → Intermediate → [LLM 2] → Output
```

*Use cases:* Draft → Review → Polish, Extract → Validate → Format

#### Pattern 2: Parallelization

Multiple nodes run simultaneously, then results are merged. Two sub-patterns:
- **Sectioning** — split work across parallel workers for speed
- **Voting** — run same task N times, take majority answer for confidence

```
                 ┌→ [Worker A] ─┐
Input → [Split] ─┤→ [Worker B] ─┼→ [Merge] → Output
                 └→ [Worker C] ─┘
```

*Use cases:* Multi-document processing, ensemble evaluation, A/B generation

#### Pattern 3: Routing

Classify the input first, then route to a specialized handler.

```
Input → [Classifier] → "billing"  → [Billing Handler]
                    → "support"  → [Support Handler]
                    → "feedback" → [Feedback Handler]
```

*Use cases:* Customer support triage, content moderation, multi-skill assistants

#### Pattern 4: Orchestrator-Worker

One LLM breaks a task into subtasks and delegates to worker nodes. Workers report back, orchestrator synthesizes. LangGraph's **`Send` API** enables dynamic worker spawning when subtasks aren't known in advance.

```
Input → [Orchestrator] → Send(worker, task_1)
                       → Send(worker, task_2)  → [Merge]
                       → Send(worker, task_3)
```

*Use cases:* Code generation with multiple files, parallel research, distributed summarization

#### Pattern 5: Evaluator-Optimizer

Generate → Evaluate → Loop until quality threshold met.

```
Input → [Generator] → draft → [Evaluator] ──pass──→ Output
                         ↑                  │
                         └──────fail────────┘
```

*Use cases:* Writing quality loops, test-driven code generation, RAG answer refinement

---

### 3. Workflows vs Agents (30 min)

| Dimension | Workflow | Agent |
|-----------|----------|-------|
| Control flow | Predetermined | Dynamic, self-directed |
| Tool usage | Fixed sequence | AI decides which/when |
| Predictability | High | Lower |
| Flexibility | Lower | High |
| Best for | Well-defined processes | Open-ended tasks |

**Rule of thumb:** Start with a workflow. Add agent autonomy only where deterministic paths fail.

LangGraph supports both — you can mix workflow nodes with agentic nodes in the same graph.

---

### 4. Checkpointing & Durable Execution (30 min)

Checkpointing saves the full graph state after each node runs. This enables:
- **Resuming** after failures without restarting
- **Human-in-the-loop** — pause and wait for human input
- **Time travel** — replay from any past checkpoint
- **Multi-session memory** — pick up a conversation days later

```python
from langgraph.checkpoint.memory import MemorySaver

# In-memory checkpointer (use SqliteSaver or PostgresSaver for production)
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# Thread ID identifies a conversation/session
config = {"configurable": {"thread_id": "user-123"}}

# Each call resumes from the last checkpoint for this thread
result1 = app.invoke({"messages": [HumanMessage("Hello")]}, config)
result2 = app.invoke({"messages": [HumanMessage("Continue")]}, config)
```

**State inspection:**
```python
# View state at any point
state = app.get_state(config)
print(state.values)  # Current state
print(state.next)    # Next nodes to run
```

---

### 5. Human-in-the-Loop (30 min)

LangGraph provides `interrupt` to pause execution and wait for human input before a node runs.

```python
from langgraph.types import interrupt

def review_node(state: State) -> dict:
    # Pause here — surface the draft for human review
    human_feedback = interrupt({
        "draft": state["draft"],
        "instructions": "Approve or edit this draft."
    })
    # Execution resumes when .update_state() is called externally
    return {"draft": human_feedback.get("edited", state["draft"])}
```

**Resuming after interrupt:**
```python
# Human reviews, then resumes with their input
app.update_state(config, {"feedback": "Approved"}, as_node="review_node")
result = app.invoke(None, config)  # None = resume from checkpoint
```

**Common patterns:**
- Approve before sending emails / making API calls
- Edit before storing to database
- Flag low-confidence outputs for human review

---

### 6. Memory Architecture (30 min)

LangGraph distinguishes two kinds of memory:

| Type | Scope | Stored In | Use Case |
|------|-------|-----------|----------|
| **Short-term** | Single session | State / `MessagesState` | Conversation context |
| **Long-term** | Cross-session | Memory Store | User preferences, facts |

**Short-term (MessagesState):**
```python
from langgraph.graph import MessagesState  # Built-in state with messages list

graph = StateGraph(MessagesState)
# messages auto-accumulate using add_messages reducer
```

**Long-term (Memory Store):**
```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Write a memory
store.put(("user", "alice"), "preferences", {"language": "Python", "level": "advanced"})

# Read in any node
def personalized_node(state, store):
    prefs = store.get(("user", "alice"), "preferences")
    return {"context": f"User prefers {prefs.value['language']}"}
```

---

### 7. CrewAI Overview (20 min)

CrewAI = role-based multi-agent teams. Higher abstraction than LangGraph — less control, faster to set up.

**Key concepts:**
- **Agent** — has a role, goal, backstory, and optional tools
- **Task** — what an agent should do; can depend on other tasks
- **Crew** — collection of agents + tasks + a process
- **Process** — `sequential` (linear) or `hierarchical` (manager delegates)

**When to choose CrewAI over LangGraph:**
- You want agents that feel like a team with distinct roles
- Your task maps naturally to research → review → write pipelines
- You don't need fine-grained control flow

---

### 8. Deep Agents Pattern (20 min)

For complex, long-horizon tasks, the "deep agent" pattern adds:
- **Planning** — task decomposition before execution
- **Context isolation** — virtual filesystem to avoid context overflow
- **Subagent delegation** — spawn specialized agents for subtasks
- **Persistent memory** — cross-conversation Memory Store

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[your_tool],
    system_prompt="You are a research agent. Break tasks into steps."
)
result = agent.invoke({"messages": [{"role": "user", "content": "Research X"}]})
```

Use deep agent patterns when: single agent context fills up, tasks require 10+ steps, or you need specialized subtask handling.

---

### 9. Choosing the Right Tool (15 min)

| Situation | Recommendation |
|-----------|----------------|
| Simple chatbot | Plain OpenAI |
| Deterministic multi-step workflow | LangGraph workflow patterns |
| Agentic loop with tools | LangGraph agent |
| Need checkpoints / resume | LangGraph + checkpointer |
| Human approval in the loop | LangGraph + interrupt |
| Role-based research/writing teams | CrewAI |
| Long-horizon complex tasks | Deep Agents pattern |
| Maximum control, no dependencies | Custom from scratch |

---

## Hands-On Practice

### Task 1: Install Frameworks (10 min)

```bash
pip install langgraph langchain-openai langchain-core crewai
```

---

### Task 2: LangGraph — Workflow Patterns (90 min)

#### 2a. Prompt Chaining

```python
# chain_workflow.py
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

class ChainState(TypedDict):
    topic: str
    outline: str
    draft: str
    final: str

def create_outline(state: ChainState) -> dict:
    """Step 1: Create an outline."""
    response = llm.invoke(f"Create a 3-point outline for a blog post about: {state['topic']}")
    return {"outline": response.content}

def write_draft(state: ChainState) -> dict:
    """Step 2: Write a draft from the outline."""
    response = llm.invoke(
        f"Write a short blog post using this outline:\n{state['outline']}\n\nKeep it under 200 words."
    )
    return {"draft": response.content}

def polish_draft(state: ChainState) -> dict:
    """Step 3: Polish the draft."""
    response = llm.invoke(
        f"Improve this draft — fix grammar, improve flow, make it more engaging:\n{state['draft']}"
    )
    return {"final": response.content}

graph = StateGraph(ChainState)
graph.add_node("outline", create_outline)
graph.add_node("draft", write_draft)
graph.add_node("polish", polish_draft)
graph.add_edge(START, "outline")
graph.add_edge("outline", "draft")
graph.add_edge("draft", "polish")
graph.add_edge("polish", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"topic": "Why Python is great for AI"})
    print("=== FINAL POST ===")
    print(result["final"])
```

#### 2b. Routing Workflow

```python
# routing_workflow.py
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal
import json
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

class SupportState(TypedDict):
    message: str
    category: str
    response: str

def classify(state: SupportState) -> dict:
    """Classify the incoming message."""
    result = llm.invoke(
        f"""Classify this support message into one category: billing, technical, general

Message: {state['message']}

Respond with JSON: {{"category": "billing|technical|general"}}"""
    )
    data = json.loads(result.content)
    return {"category": data["category"]}

def handle_billing(state: SupportState) -> dict:
    response = llm.invoke(
        f"You are a billing specialist. Answer this: {state['message']}"
    )
    return {"response": response.content}

def handle_technical(state: SupportState) -> dict:
    response = llm.invoke(
        f"You are a technical support engineer. Answer this: {state['message']}"
    )
    return {"response": response.content}

def handle_general(state: SupportState) -> dict:
    response = llm.invoke(f"Answer this customer message helpfully: {state['message']}")
    return {"response": response.content}

def route(state: SupportState) -> Literal["billing", "technical", "general"]:
    return state["category"]

graph = StateGraph(SupportState)
graph.add_node("classify", classify)
graph.add_node("billing", handle_billing)
graph.add_node("technical", handle_technical)
graph.add_node("general", handle_general)

graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route)
graph.add_edge("billing", END)
graph.add_edge("technical", END)
graph.add_edge("general", END)

app = graph.compile()

if __name__ == "__main__":
    messages = [
        "My invoice is wrong, I was charged twice",
        "The app crashes when I try to upload files",
        "What are your business hours?",
    ]
    for msg in messages:
        result = app.invoke({"message": msg})
        print(f"\n[{result['category'].upper()}] {msg}")
        print(f"→ {result['response'][:100]}...")
```

#### 2c. Evaluator-Optimizer Loop

```python
# evaluator_optimizer.py
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal
import json
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

class OptimizeState(TypedDict):
    task: str
    draft: str
    feedback: str
    score: int
    iterations: int

def generate(state: OptimizeState) -> dict:
    """Generate or improve the draft."""
    if state.get("feedback"):
        prompt = f"""Improve this draft based on the feedback:

Draft: {state['draft']}
Feedback: {state['feedback']}

Write an improved version."""
    else:
        prompt = f"Write a response to: {state['task']}"

    response = llm.invoke(prompt)
    return {"draft": response.content, "iterations": state.get("iterations", 0) + 1}

def evaluate(state: OptimizeState) -> dict:
    """Score the draft 1-10."""
    result = llm.invoke(
        f"""Evaluate this response to the task: "{state['task']}"

Response: {state['draft']}

Rate it 1-10 and give feedback for improvement.
Return JSON: {{"score": 7, "feedback": "..."}}"""
    )
    data = json.loads(result.content)
    return {"score": data["score"], "feedback": data["feedback"]}

def should_continue(state: OptimizeState) -> Literal["generate", "__end__"]:
    """Continue improving if score < 8 and we have budget."""
    if state["score"] >= 8 or state.get("iterations", 0) >= 3:
        return "__end__"
    return "generate"

graph = StateGraph(OptimizeState)
graph.add_node("generate", generate)
graph.add_node("evaluate", evaluate)
graph.add_edge(START, "generate")
graph.add_edge("generate", "evaluate")
graph.add_conditional_edges("evaluate", should_continue)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"task": "Explain why recursion is powerful in programming"})
    print(f"Final score: {result['score']}/10 after {result['iterations']} iteration(s)")
    print(f"\n{result['draft']}")
```

---

### Task 3: LangGraph — Full Agent with Tools & Checkpointing (60 min)

```python
# langgraph_agent.py
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

# --- Define tools using @tool decorator ---

@tool
def search(query: str) -> str:
    """Search the web for information on a topic."""
    # Mock — replace with real API in production
    return f"Search results for '{query}': Found comprehensive information on this topic."

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression like '2 * 3 + 4'."""
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as e:
        return f"Error: {e}"

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    return f"Weather in {city}: 20°C, partly cloudy."

tools = [search, calculate, get_weather]
tools_by_name = {t.name: t for t in tools}

# --- LLM with tools bound ---
llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

# --- Nodes ---
def agent_node(state: MessagesState) -> dict:
    """Call the LLM to decide next action."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: MessagesState) -> dict:
    """Execute all tool calls from the last AI message."""
    last_message = state["messages"][-1]
    results = []

    for tool_call in last_message.tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        results.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )

    return {"messages": results}

def should_use_tools(state: MessagesState) -> str:
    """Route: use tools or return final answer."""
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return "__end__"

# --- Build graph ---
graph = StateGraph(MessagesState)
graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_use_tools)
graph.add_edge("tools", "agent")  # Loop back after tool execution

# --- Compile with checkpointer ---
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# --- Multi-turn conversation using checkpointing ---
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "demo-session-1"}}

    turns = [
        "What is 25 * 4 + 100?",
        "What's the weather in London?",
        "Based on our conversation, what two things did we discuss?",
    ]

    for question in turns:
        print(f"\nUser: {question}")
        result = app.invoke(
            {"messages": [HumanMessage(content=question)]},
            config=config
        )
        final_message = result["messages"][-1]
        print(f"Agent: {final_message.content}")
```

---

### Task 4: Human-in-the-Loop Workflow (45 min)

```python
# human_in_loop_graph.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

class EmailState(TypedDict):
    request: str
    draft: str
    approved: bool
    final: str

def draft_email(state: EmailState) -> dict:
    """AI drafts an email."""
    response = llm.invoke(
        f"Draft a professional email for this request: {state['request']}"
    )
    return {"draft": response.content}

def human_review(state: EmailState) -> dict:
    """Pause for human approval."""
    # This suspends execution and surfaces state to the caller
    feedback = interrupt({
        "draft": state["draft"],
        "action": "Please review this email draft. Return 'approve' or an edited version."
    })

    if feedback == "approve":
        return {"approved": True, "final": state["draft"]}
    else:
        # Human provided an edited version
        return {"approved": True, "final": feedback}

def send_email(state: EmailState) -> dict:
    """Send the approved email."""
    print(f"\n📧 SENDING EMAIL:\n{state['final']}")
    return {}

graph = StateGraph(EmailState)
graph.add_node("draft", draft_email)
graph.add_node("review", human_review)
graph.add_node("send", send_email)

graph.add_edge(START, "draft")
graph.add_edge("draft", "review")
graph.add_edge("review", "send")
graph.add_edge("send", END)

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "email-1"}}

    # Step 1: Run until interrupt
    result = app.invoke(
        {"request": "Email the team about tomorrow's 10am standup being cancelled"},
        config=config
    )
    print("Draft ready for review:")
    print(result["draft"])

    # Step 2: Human provides feedback (simulate approval)
    app.update_state(config, values=None)  # Provide resume value
    result = app.invoke(Command(resume="approve"), config=config)
    print("Email sent!")
```

---

### Task 5: LangGraph Orchestrator-Worker with Send API (45 min)

```python
# orchestrator_worker.py
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
import operator
import json
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini")

class MainState(TypedDict):
    topic: str
    subtasks: list[str]
    results: Annotated[list[str], operator.add]  # Merge results from workers

class WorkerState(TypedDict):
    subtask: str
    result: str

def orchestrate(state: MainState) -> dict:
    """Break topic into subtasks."""
    response = llm.invoke(
        f"""Break this topic into 3 research subtasks:
Topic: {state['topic']}
Return JSON: {{"subtasks": ["task1", "task2", "task3"]}}"""
    )
    data = json.loads(response.content)
    return {"subtasks": data["subtasks"]}

def dispatch_workers(state: MainState):
    """Dynamically create a worker for each subtask."""
    return [Send("worker", {"subtask": task}) for task in state["subtasks"]]

def worker(state: WorkerState) -> dict:
    """Each worker handles one subtask."""
    response = llm.invoke(f"Research this subtask briefly (2-3 sentences): {state['subtask']}")
    return {"results": [f"[{state['subtask'][:30]}] {response.content}"]}

def synthesize(state: MainState) -> dict:
    """Combine all worker results."""
    combined = "\n\n".join(state["results"])
    response = llm.invoke(
        f"Synthesize these research findings into a coherent summary:\n{combined}"
    )
    return {"results": [f"SYNTHESIS:\n{response.content}"]}

graph = StateGraph(MainState)
graph.add_node("orchestrate", orchestrate)
graph.add_node("worker", worker)
graph.add_node("synthesize", synthesize)

graph.add_edge(START, "orchestrate")
graph.add_conditional_edges("orchestrate", dispatch_workers, ["worker"])
graph.add_edge("worker", "synthesize")
graph.add_edge("synthesize", END)

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"topic": "Impact of AI on software engineering jobs"})
    for r in result["results"]:
        print(r)
        print()
```

---

### Task 6: CrewAI — Multi-Agent Research Team (45 min)

```python
# research_team.py
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for information on a topic."""
    return f"Search results for '{query}': Comprehensive findings available."

# Agents with distinct roles
researcher = Agent(
    role="Senior Research Analyst",
    goal="Research topics thoroughly and find accurate, relevant information",
    backstory="Expert researcher with 10 years experience in technology analysis.",
    tools=[web_search],
    verbose=True
)

fact_checker = Agent(
    role="Fact Checker",
    goal="Verify claims and ensure accuracy of all information",
    backstory="Meticulous fact-checker who questions everything and validates sources.",
    verbose=True
)

writer = Agent(
    role="Technical Writer",
    goal="Transform research into clear, engaging content",
    backstory="Professional writer who turns complex topics into accessible articles.",
    verbose=True
)

# Tasks flow through the pipeline
research_task = Task(
    description="Research the current state of AI agent frameworks in 2024-2025. Cover: LangGraph, CrewAI, AutoGen, and their key use cases.",
    agent=researcher,
    expected_output="Detailed findings covering each framework's strengths and use cases"
)

verify_task = Task(
    description="Fact-check the research findings. Flag anything that seems inaccurate or needs clarification.",
    agent=fact_checker,
    expected_output="Verified research with accuracy notes",
    context=[research_task]
)

write_task = Task(
    description="Write a 300-word technical summary of AI agent frameworks for a developer audience.",
    agent=writer,
    expected_output="A polished 300-word developer-focused summary",
    context=[verify_task]
)

crew = Crew(
    agents=[researcher, fact_checker, writer],
    tasks=[research_task, verify_task, write_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    result = crew.kickoff()
    print("\n" + "="*60)
    print("FINAL OUTPUT:")
    print("="*60)
    print(result)
```

---

### Task 7: Framework Comparison (15 min)

```python
# comparison.py
"""
Decision guide for choosing agent frameworks.

PLAIN OPENAI
  When: Simple chat, one-shot Q&A, direct API control
  Not when: Multi-step workflows, complex state needed

LANGGRAPH
  When:
  - Complex state machines with branching logic
  - Need checkpointing / durability / resume
  - Human-in-the-loop approval flows
  - Fine-grained tool call control
  - Mixing deterministic + agentic nodes
  Examples: Document approval system, code review pipeline,
            multi-step research with human checkpoints

CREWAI
  When:
  - Role-based agent collaboration
  - Research → Review → Write pipelines
  - Task-level delegation feels natural
  - Less boilerplate than LangGraph for standard patterns
  Examples: Content creation teams, research reports,
            data analysis with multiple specialists

DEEP AGENTS PATTERN
  When:
  - Long-horizon tasks (10+ steps)
  - Context overflow is a concern
  - Need specialized subagent delegation
  - Cross-session memory is essential

BOTH (LangGraph + CrewAI)
  When: Complex orchestration needs multiple specialized crews
  Use LangGraph as outer orchestrator, CrewAI for crew subtasks
"""

frameworks = {
    "Plain OpenAI":   {"complexity": "Low",    "state": "Manual",    "checkpoints": "No",  "multi_agent": "No"},
    "LangGraph":      {"complexity": "Medium",  "state": "Built-in",  "checkpoints": "Yes", "multi_agent": "Graph nodes"},
    "CrewAI":         {"complexity": "Low-Med", "state": "Automatic", "checkpoints": "No",  "multi_agent": "Role-based"},
    "Deep Agents":    {"complexity": "Medium",  "state": "Store",     "checkpoints": "Yes", "multi_agent": "Subagents"},
}

for name, props in frameworks.items():
    print(f"\n{'─'*40}")
    print(f"  {name}")
    for k, v in props.items():
        print(f"    {k}: {v}")
```

---

## 🟡 Optional: Multi-Modal AI (Vision & Audio)

*Less frequently asked in interviews, but important for production applications that handle images, documents, or voice.*

### Theory: What Modalities OpenAI Supports

| Modality | Model | Input | Output | Real-World Use |
|----------|-------|-------|--------|----------------|
| **Vision** | gpt-4o / gpt-4o-mini | Image + text | Text | OCR, chart analysis, product images |
| **Image Generation** | DALL-E 3 | Text prompt | Image | Marketing, prototyping |
| **Speech-to-Text** | Whisper | Audio file | Text | Meeting notes, voice commands |
| **Text-to-Speech** | TTS-1 | Text | Audio | Accessibility, voice assistants |

### Multi-Modal Vision

#### Basic Image Analysis

```python
# vision_basics.py
from openai import OpenAI
import base64
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def encode_image(path: str) -> str:
    """Encode image to base64 for the API."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def analyze_image(image_path: str, question: str = "What is in this image?") -> str:
    """Send an image to GPT-4o-mini for analysis."""
    b64 = encode_image(image_path)

    # Detect format from extension
    ext = Path(image_path).suffix.lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/jpeg")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}
            ]
        }],
        max_tokens=500
    )
    return response.choices[0].message.content

def analyze_image_url(url: str, question: str) -> str:
    """Analyze an image from a URL (no base64 needed)."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": url}}
            ]
        }]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    # Local file
    # print(analyze_image("screenshot.png", "Describe what you see"))

    # URL
    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/JPEG_example_flower.jpg/256px-JPEG_example_flower.jpg"
    print(analyze_image_url(url, "What flower is this? What color is it?"))
```

#### Document OCR and Data Extraction

```python
# document_ocr.py
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
import base64
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class InvoiceData(BaseModel):
    invoice_number: Optional[str]
    date: Optional[str]
    vendor: Optional[str]
    total_amount: Optional[float]
    line_items: List[str]

def extract_invoice_data(image_path: str) -> InvoiceData:
    """Extract structured data from an invoice image."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """Extract invoice data and return JSON:
{
    "invoice_number": "...",
    "date": "...",
    "vendor": "...",
    "total_amount": 0.00,
    "line_items": ["item 1", "item 2"]
}"""},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }],
        response_format={"type": "json_object"}
    )

    data = json.loads(response.choices[0].message.content)
    return InvoiceData(**data)

def analyze_chart(image_path: str) -> dict:
    """Extract insights from a chart or graph image."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": """Analyze this chart. Return JSON:
{
    "chart_type": "bar|line|pie|scatter|...",
    "title": "...",
    "key_insights": ["insight1", "insight2"],
    "trend": "increasing|decreasing|stable",
    "notable_values": {"max": "...", "min": "..."}
}"""},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
            ]
        }],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
```

#### Multi-Image Comparison

```python
# multi_image.py
from openai import OpenAI
import base64
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def compare_images(image_paths: list[str], question: str) -> str:
    """Send multiple images in one request for comparison."""
    content = [{"type": "text", "text": question}]

    for path in image_paths:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
        })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        max_tokens=500
    )
    return response.choices[0].message.content

# Usage: compare_images(["v1.png", "v2.png"], "What changed between these UI designs?")
```

---

### Multi-Modal Audio

#### Speech-to-Text with Whisper

```python
# whisper_transcribe.py
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def transcribe(audio_path: str, language: str = None) -> str:
    """Transcribe audio file to text using Whisper."""
    with open(audio_path, "rb") as f:
        params = {
            "model": "whisper-1",
            "file": f,
            "response_format": "text"
        }
        if language:
            params["language"] = language  # e.g. "en", "fr", "de"

        return client.audio.transcriptions.create(**params)

def transcribe_with_timestamps(audio_path: str) -> dict:
    """Transcribe with word-level timestamps."""
    with open(audio_path, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="verbose_json",  # Returns segments with timestamps
            timestamp_granularities=["segment"]
        )
    return {
        "text": result.text,
        "segments": [
            {"start": s.start, "end": s.end, "text": s.text}
            for s in result.segments
        ]
    }

def translate_audio_to_english(audio_path: str) -> str:
    """Translate non-English audio directly to English text."""
    with open(audio_path, "rb") as f:
        return client.audio.translations.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )

# Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
# Max file size: 25 MB
```

#### Text-to-Speech

```python
# tts.py
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Available voices: alloy, ash, coral, echo, fable, onyx, nova, sage, shimmer
VOICES = {
    "neutral": "alloy",
    "professional": "onyx",
    "friendly": "nova",
    "warm": "shimmer",
}

def speak(text: str, output_path: str, voice: str = "alloy", speed: float = 1.0) -> str:
    """Convert text to speech and save to file."""
    response = client.audio.speech.create(
        model="tts-1",        # tts-1-hd for higher quality
        voice=voice,
        input=text,
        speed=speed           # 0.25 to 4.0
    )
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path

def speak_ssml(text: str, output_path: str) -> str:
    """Use tts-1-hd for higher quality output."""
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input=text
    )
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path

if __name__ == "__main__":
    speak("Hello! Welcome to the AI Engineering course.", "greeting.mp3", voice="nova")
    print("Audio saved to greeting.mp3")
```

---

### Full Multi-Modal Pipeline

```python
# multimodal_pipeline.py
"""
A complete multi-modal pipeline:
1. Receive voice question (audio)
2. Transcribe with Whisper
3. Optionally analyze an image
4. Generate AI response
5. Speak the response (TTS)
"""
from openai import OpenAI
from pathlib import Path
import base64
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class MultiModalAssistant:
    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self.system_prompt = system_prompt
        self.history = []

    def transcribe(self, audio_path: str) -> str:
        """Voice → text."""
        with open(audio_path, "rb") as f:
            return client.audio.transcriptions.create(
                model="whisper-1", file=f, response_format="text"
            )

    def analyze_image(self, image_path: str) -> str:
        """Image → text description."""
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image concisely."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }],
            max_tokens=200
        )
        return response.choices[0].message.content

    def chat(self, text_input: str, image_context: str = None) -> str:
        """Generate text response with optional image context."""
        user_content = text_input
        if image_context:
            user_content = f"[Image context: {image_context}]\n\nUser question: {text_input}"

        self.history.append({"role": "user", "content": user_content})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.history
            ]
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})
        return reply

    def speak(self, text: str, output_path: str) -> str:
        """Text → audio file."""
        response = client.audio.speech.create(
            model="tts-1", voice="nova", input=text
        )
        with open(output_path, "wb") as f:
            f.write(response.content)
        return output_path

    def voice_chat(self, audio_path: str, image_path: str = None) -> dict:
        """Full pipeline: audio in → audio out."""
        # 1. Transcribe question
        question = self.transcribe(audio_path)
        print(f"You said: {question}")

        # 2. Optionally analyze image
        image_context = None
        if image_path:
            image_context = self.analyze_image(image_path)
            print(f"Image context: {image_context}")

        # 3. Generate response
        answer = self.chat(question, image_context)
        print(f"Assistant: {answer}")

        # 4. Speak response
        output_audio = "response.mp3"
        self.speak(answer, output_audio)

        return {
            "question": question,
            "answer": answer,
            "audio": output_audio
        }

# Usage:
# assistant = MultiModalAssistant("You are a helpful assistant.")
# result = assistant.voice_chat("question.mp3", image_path="chart.png")
```

---

## Knowledge Checklist

**LangGraph Core**
- [ ] I understand StateGraph, nodes, edges, and reducers
- [ ] I can implement the five workflow patterns (chaining, parallelization, routing, orchestrator-worker, evaluator-optimizer)
- [ ] I know the difference between workflows and agents
- [ ] I can add checkpointing for durable execution
- [ ] I can implement human-in-the-loop with `interrupt`
- [ ] I understand short-term vs long-term memory

**CrewAI**
- [ ] I can create agents with roles, goals, and tools
- [ ] I can define tasks with context dependencies
- [ ] I understand sequential vs hierarchical process

**Multi-Modal (Optional)**
- [ ] I can send images to gpt-4o-mini for analysis
- [ ] I can extract structured data from images (OCR)
- [ ] I can transcribe audio with Whisper
- [ ] I can generate speech with TTS
- [ ] I can build a voice-in/voice-out pipeline

---

## Deliverables

**LangGraph**
1. `chain_workflow.py` — Prompt chaining pattern
2. `routing_workflow.py` — Input routing pattern
3. `evaluator_optimizer.py` — Generate-evaluate loop
4. `langgraph_agent.py` — Full agent with tools + checkpointing
5. `human_in_loop_graph.py` — Human approval workflow
6. `orchestrator_worker.py` — Dynamic worker spawning

**CrewAI**
7. `research_team.py` — Multi-agent research pipeline

**Framework**
8. `comparison.py` — Decision guide

**Multi-Modal (Optional)**
9. `vision_basics.py` — Image analysis
10. `document_ocr.py` — Document extraction
11. `whisper_transcribe.py` — Audio transcription
12. `tts.py` — Text-to-speech
13. `multimodal_pipeline.py` — Full voice/vision pipeline

---

## What's Next?

Next week: **Data Engineering for AI** — SQL, pipelines, and data quality for production AI systems!

---

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Conceptual Guide — Workflows vs Agents](https://langchain-ai.github.io/langgraph/concepts/workflows-agents/)
- [LangGraph How-To: Human-in-the-Loop](https://langchain-ai.github.io/langgraph/how-tos/human-in-the-loop/)
- [LangGraph How-To: Checkpointing](https://langchain-ai.github.io/langgraph/how-tos/checkpointing/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [OpenAI Vision Guide](https://platform.openai.com/docs/guides/vision)
- [OpenAI Audio Guide](https://platform.openai.com/docs/guides/speech-to-text)
- [Whisper Model Card](https://openai.com/research/whisper)
