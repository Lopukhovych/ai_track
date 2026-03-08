# Week 7: Agent Fundamentals

**Month:** 3 (Intelligence) | **Duration:** 6-8 hours

---

## Overview

This week you'll create **agents** — AI systems that can plan, reason, and execute multi-step tasks autonomously. This is where AI gets truly powerful.

---

## Learning Objectives

By the end of this week, you will:
- Understand the difference between tools and agents
- Build a ReAct (Reason + Act) agent
- Implement agent loops with planning
- Handle errors and retries
- Build an autonomous task executor

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| ReAct agent (reasoning) | `gpt-5-mini` | `deepseek-r1:8b` (native chain-of-thought) |
| Faster / lighter agent | `gpt-5-mini` | `llama3.1:8b` |

**Quick start with Ollama:**
```bash
ollama pull deepseek-r1:8b   # ~5.2GB — built-in <think> reasoning traces
ollama pull llama3.1:8b      # lighter fallback
```

```python
from scripts.model_config import get_client, REASON_MODEL
# deepseek-r1 outputs its reasoning in <think>...</think> blocks — great for debugging agents
```

> `deepseek-r1:8b` is ideal for ReAct loops: its chain-of-thought reasoning is visible and helps you understand why the agent took each step.

---

## Theory (2 hours)

### 1. Tools vs Agents (30 min)

| Tool Calling | Agent |
|--------------|-------|
| One question → one action | One goal → many actions |
| You manage the loop | Agent manages itself |
| No memory between calls | Remembers and plans |
| Reactive | Proactive |

**Tool calling:**
```
User: "What's the weather in Paris?"
AI: get_weather("Paris") → "It's 18°C"
Done.
```

**Agent:**
```
User: "Plan a weekend trip to Paris"
Agent:
  1. First, I'll check the weather → get_weather("Paris")
  2. Now I'll search for hotels → search_hotels("Paris")
  3. Let me find activities → search_attractions("Paris")
  4. I'll create an itinerary → create_plan(...)
Done!
```

### 2. The ReAct Pattern (30 min)

**ReAct = Reasoning + Acting**

```
GOAL: Book the cheapest flight to London

THOUGHT: I need to search for available flights first
ACTION: search_flights(destination="London", date="2024-03-15")
OBSERVATION: [Flight results: $450, $380, $520]

THOUGHT: The $380 flight is cheapest. I should book it.
ACTION: book_flight(flight_id="FL380")
OBSERVATION: Booking confirmed #12345

THOUGHT: I've booked the flight. Task complete.
ANSWER: I booked flight #12345 for $380 to London.
```

**Key components:**
- **Thought**: Planning what to do next
- **Action**: Executing a tool
- **Observation**: Seeing the result
- **Loop**: Repeat until goal achieved

### 3. Agent Architecture (30 min)

```
┌────────────────────────────────────────────────┐
│                     AGENT                      │
├────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐ │
│  │               MEMORY                      │ │
│  │  - Conversation history                   │ │
│  │  - Task state                             │ │
│  │  - Previous observations                  │ │
│  └──────────────────────────────────────────┘ │
│                      ↓                         │
│  ┌──────────────────────────────────────────┐ │
│  │            REASONING (LLM)                │ │
│  │  - What's the current state?              │ │
│  │  - What should I do next?                 │ │
│  │  - Am I done?                             │ │
│  └──────────────────────────────────────────┘ │
│                      ↓                         │
│  ┌──────────────────────────────────────────┐ │
│  │               TOOLS                        │ │
│  │  search() │ calculate() │ write()         │ │
│  └──────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘
```

### 4. Common Agent Patterns (30 min)

| Pattern | Use Case |
|---------|----------|
| **ReAct** | General reasoning + action |
| **Plan-and-Execute** | Complex multi-step tasks |
| **Self-Reflection** | Improve answers iteratively |
| **Multi-Agent** | Specialized collaboration |

---

## Hands-On Practice (4-6 hours)

### Task 1: Simple ReAct Agent (60 min)

```python
# react_agent.py
from openai import OpenAI
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = OpenAI()

# Tools
def search_web(query: str) -> str:
    """Mock web search."""
    return f"Search results for '{query}': Found relevant information about {query}."

def calculate(expression: str) -> str:
    """Calculate math expression."""
    try:
        return str(eval(expression))
    except:
        return "Error in calculation"

def get_weather(city: str) -> str:
    """Mock weather."""
    return f"Weather in {city}: 20°C, partly cloudy"

tools = {
    "search_web": search_web,
    "calculate": calculate,
    "get_weather": get_weather
}

REACT_PROMPT = """You are a helpful assistant that uses tools to answer questions.

Available tools:
- search_web(query): Search the web for information
- calculate(expression): Do math calculations
- get_weather(city): Get weather for a city

Always use this format:
THOUGHT: [your reasoning about what to do]
ACTION: tool_name(arguments)

When you have enough information:
THOUGHT: [summary of what you learned]
ANSWER: [your final answer]

Begin!

Question: {question}
"""

def parse_response(text: str) -> tuple:
    """Parse agent response into thought, action, or answer."""

    # Check for answer
    if "ANSWER:" in text:
        thought = re.search(r"THOUGHT:(.*?)(?:ANSWER:|$)", text, re.DOTALL)
        answer = re.search(r"ANSWER:(.*?)$", text, re.DOTALL)
        return "answer", {
            "thought": thought.group(1).strip() if thought else "",
            "answer": answer.group(1).strip() if answer else text
        }

    # Check for action
    if "ACTION:" in text:
        thought = re.search(r"THOUGHT:(.*?)ACTION:", text, re.DOTALL)
        action = re.search(r"ACTION:\s*(\w+)\((.*?)\)", text)

        if action:
            return "action", {
                "thought": thought.group(1).strip() if thought else "",
                "tool": action.group(1),
                "args": action.group(2).strip('"\'')
            }

    return "unknown", {"text": text}

def run_agent(question: str, max_steps: int = 5) -> str:
    """Run the ReAct agent."""

    prompt = REACT_PROMPT.format(question=question)
    messages = [{"role": "user", "content": prompt}]

    for step in range(max_steps):
        print(f"\n--- Step {step + 1} ---")

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            temperature=0
        )

        text = response.choices[0].message.content
        print(text)

        result_type, data = parse_response(text)

        if result_type == "answer":
            return data["answer"]

        if result_type == "action":
            # Execute tool
            tool_name = data["tool"]
            tool_args = data["args"]

            if tool_name in tools:
                observation = tools[tool_name](tool_args)
            else:
                observation = f"Unknown tool: {tool_name}"

            print(f"OBSERVATION: {observation}")

            # Add to messages
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", "content": f"OBSERVATION: {observation}"})
        else:
            messages.append({"role": "assistant", "content": text})
            messages.append({"role": "user", "content": "Continue reasoning. Use THOUGHT/ACTION or ANSWER format."})

    return "Max steps reached without answer"

# Test
if __name__ == "__main__":
    questions = [
        "What is 25 * 17?",
        "What's the weather like in Tokyo?",
        "Calculate 15% of 200 and tell me if it's more than 25"
    ]

    for q in questions:
        print(f"\n{'='*50}")
        print(f"QUESTION: {q}")
        print("="*50)
        answer = run_agent(q)
        print(f"\n✅ FINAL: {answer}")
```

### Task 2: Agent with Memory (45 min)

```python
# memory_agent.py
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass, field
from typing import List, Dict
import json

load_dotenv()
client = OpenAI()

@dataclass
class AgentMemory:
    """Agent's working memory."""
    goal: str = ""
    steps_taken: List[Dict] = field(default_factory=list)
    observations: List[str] = field(default_factory=list)
    current_plan: List[str] = field(default_factory=list)

    def add_step(self, thought: str, action: str, result: str):
        self.steps_taken.append({
            "thought": thought,
            "action": action,
            "result": result
        })
        self.observations.append(result)

    def summary(self) -> str:
        return f"""
GOAL: {self.goal}

COMPLETED STEPS:
{chr(10).join([f"- {s['action']}: {s['result'][:100]}" for s in self.steps_taken])}

OBSERVATIONS SO FAR:
{chr(10).join(self.observations[-3:])}
"""

class MemoryAgent:
    def __init__(self):
        self.client = OpenAI()
        self.memory = AgentMemory()
        self.tools = {
            "search": lambda q: f"Found info about: {q}",
            "calculate": lambda e: str(eval(e)),
            "note": lambda n: f"Noted: {n}"
        }

    def run(self, goal: str, max_steps: int = 5) -> str:
        self.memory.goal = goal

        for step in range(max_steps):
            # Build prompt with memory
            prompt = f"""
{self.memory.summary()}

Available tools: search(query), calculate(expr), note(text)

What should you do next to achieve the goal?
Respond with JSON: {{"thought": "...", "action": "tool(arg)", "done": false}}
Or if complete: {{"thought": "...", "answer": "...", "done": true}}
"""

            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)
            print(f"Step {step + 1}: {data}")

            if data.get("done"):
                return data.get("answer", "Completed")

            # Execute action
            action = data.get("action", "")
            import re
            match = re.match(r"(\w+)\((.*?)\)", action)

            if match:
                tool, arg = match.groups()
                result = self.tools.get(tool, lambda x: "Unknown tool")(arg.strip('"\''))
                self.memory.add_step(data.get("thought", ""), action, result)
            else:
                self.memory.add_step(data.get("thought", ""), "none", "No action taken")

        return "Goal not completed in max steps"

# Test
if __name__ == "__main__":
    agent = MemoryAgent()
    result = agent.run("Calculate 15% of 250 and add 50 to it")
    print(f"\nFinal: {result}")
```

### Task 3: Plan-and-Execute Agent (60 min)

```python
# plan_agent.py
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class PlanAndExecuteAgent:
    """Agent that creates a plan first, then executes it."""

    def __init__(self):
        self.client = OpenAI()
        self.tools = {
            "search": lambda q: f"Results for '{q}': relevant information found",
            "write": lambda text: f"Written: {text[:50]}...",
            "calculate": lambda e: str(eval(e)),
        }

    def create_plan(self, goal: str) -> list:
        """Have LLM create a plan."""

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": f"""Create a step-by-step plan to achieve this goal:

GOAL: {goal}

Available tools: search(query), write(text), calculate(expression)

Return JSON: {{"steps": ["step 1", "step 2", ...]}}
Each step should be a specific action with the tool to use."""
            }],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        return data.get("steps", [])

    def execute_step(self, step: str, context: list) -> str:
        """Execute a single step."""

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": f"""Execute this step:

STEP: {step}

Previous context:
{chr(10).join(context[-3:])}

Available tools: search(query), write(text), calculate(expression)

Return JSON: {{"tool": "tool_name", "argument": "...", "reasoning": "..."}}"""
            }],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        tool = data.get("tool", "")
        arg = data.get("argument", "")

        if tool in self.tools:
            return self.tools[tool](arg)
        return f"Executed: {step}"

    def run(self, goal: str) -> str:
        # Phase 1: Plan
        print("📋 Creating plan...")
        plan = self.create_plan(goal)

        print(f"Plan ({len(plan)} steps):")
        for i, step in enumerate(plan, 1):
            print(f"  {i}. {step}")

        # Phase 2: Execute
        print("\n🚀 Executing plan...")
        context = []

        for i, step in enumerate(plan, 1):
            print(f"\nStep {i}: {step}")
            result = self.execute_step(step, context)
            print(f"  → {result}")
            context.append(f"{step}: {result}")

        # Phase 3: Summarize
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": f"""Summarize what was accomplished:

GOAL: {goal}

EXECUTION:
{chr(10).join(context)}

Provide a brief summary of results."""
            }]
        )

        return response.choices[0].message.content

# Test
if __name__ == "__main__":
    agent = PlanAndExecuteAgent()
    result = agent.run("Research Python's history and calculate how old it is")
    print(f"\n✅ Summary:\n{result}")
```

### Task 4: Error-Handling Agent (45 min)

```python
# robust_agent.py
from openai import OpenAI
from dotenv import load_dotenv
import json
import traceback

load_dotenv()
client = OpenAI()

class RobustAgent:
    """Agent with error handling and retries."""

    def __init__(self):
        self.client = OpenAI()
        self.max_retries = 3

    def execute_with_retry(self, task: str) -> dict:
        """Execute a task with retries on failure."""

        errors = []

        for attempt in range(self.max_retries):
            try:
                result = self._attempt_task(task, errors)
                return {"success": True, "result": result, "attempts": attempt + 1}

            except Exception as e:
                error_msg = f"Attempt {attempt + 1}: {str(e)}"
                errors.append(error_msg)
                print(f"⚠️ {error_msg}")

                if attempt == self.max_retries - 1:
                    return {
                        "success": False,
                        "error": str(e),
                        "attempts": self.max_retries,
                        "all_errors": errors
                    }

    def _attempt_task(self, task: str, previous_errors: list) -> str:
        """Single attempt at a task."""

        error_context = ""
        if previous_errors:
            error_context = f"""
Previous attempts failed:
{chr(10).join(previous_errors)}

Learn from these errors and try a different approach.
"""

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": f"""Complete this task:

TASK: {task}

{error_context}

Return JSON: {{
    "approach": "how you'll do it",
    "result": "the actual result"
}}"""
            }],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        # Simulate occasional failures for demo
        import random
        if random.random() < 0.3 and len(previous_errors) < 2:
            raise Exception("Simulated random failure")

        return data.get("result", "No result")

    def run(self, goal: str) -> str:
        """Run the agent on a goal."""

        result = self.execute_with_retry(goal)

        if result["success"]:
            return f"✅ Success (attempts: {result['attempts']}): {result['result']}"
        else:
            return f"❌ Failed after {result['attempts']} attempts: {result['error']}"

# Test
if __name__ == "__main__":
    agent = RobustAgent()
    print(agent.run("What is 2 + 2?"))
```

### Task 5: Multi-Step Task Executor (60 min)

```python
# task_executor.py
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Optional
import json

load_dotenv()

@dataclass
class TaskResult:
    task: str
    success: bool
    result: str
    subtasks: List['TaskResult'] = None

class TaskExecutor:
    """Execute complex multi-step tasks."""

    def __init__(self):
        self.client = OpenAI()
        self.tools = {
            "search": lambda q: f"Found: {q}",
            "write": lambda t: f"Created: {t[:30]}...",
            "calculate": lambda e: str(eval(e)),
            "list": lambda items: f"Listed {items}",
        }

    def decompose_task(self, task: str) -> List[str]:
        """Break down a complex task."""

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": f"""Break this task into simple subtasks:

TASK: {task}

Tools available: search, write, calculate, list

Return JSON: {{"subtasks": ["task1", "task2", ...]}}
Each subtask should be simple and actionable."""
            }],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        return data.get("subtasks", [task])

    def execute_simple_task(self, task: str) -> str:
        """Execute a simple atomic task."""

        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{
                "role": "user",
                "content": f"""Execute this task:

TASK: {task}

Available tools: search(query), write(text), calculate(expr), list(items)

Return JSON: {{"tool": "name", "arg": "argument", "result": "what happened"}}"""
            }],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)

        tool = data.get("tool", "")
        if tool in self.tools:
            return self.tools[tool](data.get("arg", ""))
        return data.get("result", "Completed")

    def execute(self, task: str) -> TaskResult:
        """Execute a potentially complex task."""

        # Try to decompose
        subtasks = self.decompose_task(task)

        if len(subtasks) <= 1:
            # Simple task - execute directly
            result = self.execute_simple_task(task)
            return TaskResult(task=task, success=True, result=result)

        # Complex task - execute subtasks
        print(f"📋 Decomposed into {len(subtasks)} subtasks")

        subtask_results = []
        all_success = True

        for i, subtask in enumerate(subtasks, 1):
            print(f"  {i}. {subtask}")
            result = self.execute_simple_task(subtask)
            print(f"     → {result}")

            subtask_results.append(TaskResult(
                task=subtask,
                success=True,
                result=result
            ))

        # Combine results
        combined = "\n".join([f"- {r.result}" for r in subtask_results])

        return TaskResult(
            task=task,
            success=all_success,
            result=combined,
            subtasks=subtask_results
        )

# Test
if __name__ == "__main__":
    executor = TaskExecutor()

    task = "Research Python's creation date, calculate its age, and list 3 major features"
    print(f"🎯 Task: {task}\n")

    result = executor.execute(task)

    print(f"\n✅ Final Result:\n{result.result}")
```

---

## 🎯 Optional Challenges

*Agents are complex. These challenges push your understanding.*

### Challenge 1: Research Agent
Build an agent that:
1. Takes a research topic
2. Searches for information (mock or real API)
3. Reads and summarizes findings
4. Compiles a structured report with citations

### Challenge 2: Multi-Agent Debate
Create two agents with opposing viewpoints:
```python
agent_optimist = Agent(system="You see the positive side of everything")
agent_skeptic = Agent(system="You question everything critically")

# Make them debate a topic for 5 rounds
topic = "AI will replace most jobs"
result = debate(agent_optimist, agent_skeptic, topic, rounds=5)
```

### Challenge 3: Agent with Human Approval
Build an agent that asks for human confirmation before:
- Taking destructive actions (delete, overwrite)
- Making external API calls
- Spending above a token/cost threshold

```python
if action.requires_approval:
    approved = input(f"Allow '{action.description}'? (y/n): ")
    if approved != 'y':
        return "Action cancelled by user"
```

### Challenge 4: Agent Memory Persistence
Save agent state to a file:
```python
agent.save_state("agent_state.json")  # Save memory, tool history
agent.load_state("agent_state.json")  # Resume later
```
Test: Start a task, kill the program, resume and complete it.

### Challenge 5: Agent Self-Improvement
Build an agent that:
1. Attempts a task
2. Evaluates its own output ("Was this good? What went wrong?")
3. Modifies its approach based on reflection
4. Retries with improvements

---

## Knowledge Checklist

- [ ] I understand the difference between tools and agents
- [ ] I can implement the ReAct pattern
- [ ] I can build agents with memory
- [ ] I understand plan-and-execute architecture
- [ ] I can handle errors and retries
- [ ] I can decompose complex tasks

---

## Deliverables

1. `react_agent.py` — Basic ReAct implementation
2. `memory_agent.py` — Agent with working memory
3. `plan_agent.py` — Plan-and-execute pattern
4. `robust_agent.py` — Error handling
5. `task_executor.py` — Multi-step execution

---

## What's Next?

Next week: **Tool Calling & Function Execution** — teach AI to call real functions and take real actions!

---

## Resources

- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [Building Agents](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/)
