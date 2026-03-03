# Week 11: Agent Frameworks (LangGraph & CrewAI)

**Month:** 3 (Intelligence) | **Duration:** 6-8 hours

---

## Overview

Building agents from scratch is educational, but in production you'll use frameworks. This week you'll learn **LangGraph** for stateful agent workflows and **CrewAI** for multi-agent collaboration.

---

## Learning Objectives

By the end of this week, you will:
- Understand when to use agent frameworks
- Build stateful workflows with LangGraph
- Create multi-agent teams with CrewAI
- Chain agents for complex tasks
- Choose the right framework for your use case

---

## Theory (2 hours)

### 1. Why Agent Frameworks? (30 min)

**Building from scratch:**
- Full control
- Simple use cases
- Learning purposes

**Using frameworks:**
- Complex state management
- Multi-agent coordination
- Production features (retry, logging, checkpoints)
- Battle-tested patterns

### 2. LangGraph Overview (30 min)

**LangGraph** = Graphs for agent workflows

```
┌─────────┐     ┌─────────┐     ┌─────────┐
│  START  │ ──→ │ AGENT   │ ──→ │  TOOLS  │
└─────────┘     └─────────┘     └─────────┘
                     ↑               │
                     └───────────────┘
                     (loop until done)
```

**Key concepts:**
- **Nodes**: Functions that do work
- **Edges**: Connections between nodes
- **State**: Data that flows through the graph
- **Conditional edges**: Branch based on state

### 3. CrewAI Overview (30 min)

**CrewAI** = Teams of AI agents with roles

```
┌─────────────────────────────────────────┐
│                 CREW                     │
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐       │
│  │  Researcher │  │   Writer    │       │
│  │  (Agent 1)  │  │  (Agent 2)  │       │
│  └─────────────┘  └─────────────┘       │
│         │                │              │
│         └──── Tasks ─────┘              │
└─────────────────────────────────────────┘
```

**Key concepts:**
- **Agent**: Role, goal, backstory
- **Task**: What the agent should do
- **Crew**: Collection of agents + tasks
- **Process**: Sequential or hierarchical

### 4. Choosing a Framework (30 min)

| Use Case | Framework |
|----------|-----------|
| Simple chatbot | Just OpenAI |
| Complex workflows | LangGraph |
| Multi-agent teams | CrewAI |
| RAG applications | LangChain |
| Maximum control | Build custom |

---

## Hands-On Practice (4-6 hours)

### Task 1: Install Frameworks (15 min)

```bash
pip install langgraph langchain-openai crewai
```

### Task 2: LangGraph Basics (60 min)

```python
# langgraph_basics.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

# Define the state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next_step: str

# Define nodes
def start_node(state: AgentState) -> dict:
    """Initial processing."""
    return {
        "messages": ["Started processing"],
        "next_step": "process"
    }

def process_node(state: AgentState) -> dict:
    """Main processing."""
    # Check if we have enough messages
    if len(state["messages"]) >= 3:
        return {
            "messages": ["Processing complete"],
            "next_step": "end"
        }
    return {
        "messages": ["Still processing..."],
        "next_step": "process"
    }

def end_node(state: AgentState) -> dict:
    """Final step."""
    return {"messages": ["Done!"]}

# Define routing
def should_continue(state: AgentState) -> str:
    """Decide next node."""
    if state["next_step"] == "end":
        return "end"
    return "process"

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("start", start_node)
workflow.add_node("process", process_node)
workflow.add_node("end", end_node)

# Add edges
workflow.set_entry_point("start")
workflow.add_edge("start", "process")
workflow.add_conditional_edges(
    "process",
    should_continue,
    {"process": "process", "end": "end"}
)
workflow.add_edge("end", END)

# Compile
app = workflow.compile()

# Run
if __name__ == "__main__":
    result = app.invoke({"messages": [], "next_step": "start"})
    print("Messages:", result["messages"])
```

### Task 3: LangGraph Agent with Tools (60 min)

```python
# langgraph_agent.py
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from typing import TypedDict, Annotated, Sequence
import operator
import json
from dotenv import load_dotenv

load_dotenv()

# Tools
def search(query: str) -> str:
    return f"Found results for: {query}"

def calculate(expression: str) -> str:
    try:
        return str(eval(expression))
    except:
        return "Error"

tools_map = {"search": search, "calculate": calculate}

# Tool definitions for LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search for information",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Do math",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    }
]

# State
class AgentState(TypedDict):
    messages: Annotated[Sequence, operator.add]

# LLM
llm = ChatOpenAI(model="gpt-4o-mini").bind_tools(tools)

# Nodes
def agent_node(state: AgentState):
    """Call the LLM."""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState):
    """Execute tools."""
    last_message = state["messages"][-1]
    results = []
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        args = tool_call["args"]
        
        result = tools_map[tool_name](**args)
        
        results.append(ToolMessage(
            content=result,
            tool_call_id=tool_call["id"]
        ))
    
    return {"messages": results}

def should_continue(state: AgentState) -> str:
    """Check if we should continue."""
    last_message = state["messages"][-1]
    
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
workflow.add_edge("tools", "agent")

app = workflow.compile()

# Run
if __name__ == "__main__":
    result = app.invoke({
        "messages": [HumanMessage(content="What is 25 * 17?")]
    })
    
    for msg in result["messages"]:
        print(f"{msg.__class__.__name__}: {msg.content}")
```

### Task 4: CrewAI Basics (60 min)

```python
# crewai_basics.py
from crewai import Agent, Task, Crew
from dotenv import load_dotenv

load_dotenv()

# Define agents
researcher = Agent(
    role="Research Analyst",
    goal="Research and gather accurate information",
    backstory="You are an expert researcher with years of experience finding reliable information.",
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Write clear and engaging content",
    backstory="You are a professional writer who creates compelling content from research.",
    verbose=True
)

# Define tasks
research_task = Task(
    description="Research the basics of Python programming language: its history, creator, and main features.",
    agent=researcher,
    expected_output="A summary of Python's history, creator, and 5 main features"
)

writing_task = Task(
    description="Write a short blog post introduction about Python based on the research.",
    agent=writer,
    expected_output="A 100-word engaging introduction to Python",
    context=[research_task]  # Uses output from research
)

# Create crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=True
)

# Run
if __name__ == "__main__":
    result = crew.kickoff()
    print("\n" + "="*50)
    print("FINAL OUTPUT:")
    print("="*50)
    print(result)
```

### Task 5: CrewAI with Custom Tools (45 min)

```python
# crewai_tools.py
from crewai import Agent, Task, Crew
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Define custom tools
@tool("Search Tool")
def search_tool(query: str) -> str:
    """Search for information on a topic."""
    return f"Search results for '{query}': Found relevant information about {query}."

@tool("Calculator")
def calculator_tool(expression: str) -> str:
    """Calculate a mathematical expression."""
    try:
        return str(eval(expression))
    except:
        return "Error in calculation"

# Agent with tools
analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and calculate metrics",
    backstory="Expert data analyst skilled in research and calculations.",
    tools=[search_tool, calculator_tool],
    verbose=True
)

# Task
analysis_task = Task(
    description="""
    1. Search for Python's release year
    2. Calculate how many years old Python is (current year is 2024)
    3. Provide a brief summary
    """,
    agent=analyst,
    expected_output="Python's age and a brief summary"
)

crew = Crew(
    agents=[analyst],
    tasks=[analysis_task],
    verbose=True
)

if __name__ == "__main__":
    result = crew.kickoff()
    print(f"\nResult: {result}")
```

### Task 6: Multi-Agent Research Team (60 min)

```python
# research_team.py
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

# Tools
@tool("Web Search")
def web_search(query: str) -> str:
    """Search the web for information."""
    return f"Results for '{query}': Comprehensive information found."

@tool("Summarizer")
def summarize(text: str) -> str:
    """Summarize long text."""
    return f"Summary: {text[:100]}..."

# Agents
lead_researcher = Agent(
    role="Lead Researcher",
    goal="Coordinate research and ensure comprehensive coverage",
    backstory="Senior researcher who ensures thorough and accurate research.",
    tools=[web_search],
    verbose=True
)

fact_checker = Agent(
    role="Fact Checker",
    goal="Verify all facts and claims",
    backstory="Meticulous fact-checker with an eye for accuracy.",
    verbose=True
)

editor = Agent(
    role="Editor",
    goal="Polish and finalize content",
    backstory="Experienced editor who crafts clear, engaging content.",
    tools=[summarize],
    verbose=True
)

# Tasks
research_task = Task(
    description="Research the topic of 'AI in healthcare': current applications, benefits, and challenges.",
    agent=lead_researcher,
    expected_output="Detailed research findings on AI in healthcare"
)

verify_task = Task(
    description="Review the research and verify key facts are accurate.",
    agent=fact_checker,
    expected_output="Verified research with notes on accuracy",
    context=[research_task]
)

edit_task = Task(
    description="Create a polished executive summary from the verified research.",
    agent=editor,
    expected_output="A clear, professional executive summary (200 words)",
    context=[verify_task]
)

# Crew with sequential process
crew = Crew(
    agents=[lead_researcher, fact_checker, editor],
    tasks=[research_task, verify_task, edit_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    print("🚀 Starting Research Team\n")
    result = crew.kickoff()
    print("\n" + "="*50)
    print("FINAL EXECUTIVE SUMMARY:")
    print("="*50)
    print(result)
```

### Task 7: Compare Approaches (30 min)

```python
# comparison.py
"""
When to use each approach:

1. PLAIN OPENAI
   - Simple chat
   - One-shot tasks
   - Direct API control needed
   
   Example: Basic chatbot, quick Q&A

2. LANGGRAPH
   - Complex state machines
   - Custom control flow
   - Need checkpoints/persistence
   - Fine-grained tool control
   
   Example: Multi-step workflows, approval systems

3. CREWAI
   - Role-based collaboration
   - Simulated team dynamics
   - Complex research/writing tasks
   - Hierarchical delegation
   
   Example: Content creation, research reports

4. BOTH
   - Very complex systems
   - LangGraph for orchestration
   - CrewAI for specialized subtasks
"""

# Quick feature comparison
features = {
    "Plain OpenAI": {
        "complexity": "Low",
        "multi_agent": "Manual",
        "state_management": "Manual",
        "tool_calling": "Built-in",
        "best_for": "Simple apps"
    },
    "LangGraph": {
        "complexity": "Medium",
        "multi_agent": "Graph-based",
        "state_management": "Built-in",
        "tool_calling": "Flexible",
        "best_for": "Workflows"
    },
    "CrewAI": {
        "complexity": "Low-Medium",
        "multi_agent": "Role-based",
        "state_management": "Automatic",
        "tool_calling": "Decorators",
        "best_for": "Teams/Research"
    }
}

for framework, props in features.items():
    print(f"\n{framework}:")
    for k, v in props.items():
        print(f"  {k}: {v}")
```

---

## Knowledge Checklist

- [ ] I understand when to use frameworks vs custom code
- [ ] I can build workflows with LangGraph
- [ ] I can use conditional edges and state
- [ ] I can create multi-agent crews with CrewAI
- [ ] I understand Process.sequential vs hierarchical
- [ ] I know which framework to choose for my use case

---

## Deliverables

1. `langgraph_basics.py` — Simple workflow
2. `langgraph_agent.py` — Agent with tools
3. `crewai_basics.py` — Simple crew
4. `crewai_tools.py` — Crew with tools
5. `research_team.py` — Multi-agent team
6. `comparison.py` — Framework comparison

---

## What's Next?

Next week: **Data Engineering for AI** — SQL, pipelines, and data quality!

---

## 🟡 Optional Section: Multi-Modal AI

*This section covers working with images and audio. It's marked as optional (🟡) because while useful, it's less frequently asked in interviews compared to RAG and agents.*

### Multi-Modal Theory (30 min)

**Modalities OpenAI supports:**
| Modality | API | What It Does |
|----------|-----|--------------|
| **Vision** | gpt-4o-mini | Understand images, OCR |
| **Image Gen** | DALL-E 3 | Create images from text |
| **Speech-to-Text** | Whisper | Transcribe audio |
| **Text-to-Speech** | TTS | Generate spoken audio |

### Vision: Analyzing Images (30 min)

```python
# vision.py
from openai import OpenAI
import base64

client = OpenAI()

def encode_image(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def analyze_image(image_path: str, question: str = "What's in this image?") -> str:
    base64_img = encode_image(image_path)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_img}"
                }}
            ]
        }],
        max_tokens=300
    )
    return response.choices[0].message.content

# Use cases:
# - Document processing (read scanned PDFs)
# - Product image analysis
# - Chart/graph understanding
# - Accessibility (describe images)
```

### Image Generation: DALL-E (30 min)

```python
# image_generation.py
from openai import OpenAI

client = OpenAI()

def generate_image(prompt: str, size: str = "1024x1024") -> str:
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        quality="standard",
        n=1
    )
    return response.data[0].url

# Tips for better results:
# - Be specific: "digital art of..." vs "a picture of..."
# - Include style: "oil painting", "3D render", "photograph"
# - Describe composition: "close-up", "wide angle", "centered"
```

### Audio: Speech-to-Text (Whisper) (30 min)

```python
# transcribe.py
from openai import OpenAI
from pathlib import Path

client = OpenAI()

def transcribe_audio(audio_path: str) -> str:
    with open(audio_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format="text"
        )
    return transcript

# Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
# Max file size: 25 MB
# Use cases: meeting notes, voice commands, podcasts
```

### Audio: Text-to-Speech (TTS) (30 min)

```python
# text_to_speech.py
from openai import OpenAI
from pathlib import Path

client = OpenAI()

def text_to_speech(text: str, output_path: str, voice: str = "alloy") -> str:
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,  # alloy, echo, fable, onyx, nova, shimmer
        input=text
    )
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    
    return output_path

# Use cases: accessibility, voice assistants, audio content
```

### Multi-Modal Agent Example (45 min)

```python
# multimodal_agent.py
from openai import OpenAI
import base64

client = OpenAI()

class MultiModalAssistant:
    """Assistant that can see, speak, and listen."""
    
    def analyze_and_describe(self, image_path: str) -> str:
        """Analyze image and generate audio description."""
        # 1. Analyze image
        description = self._analyze_image(image_path)
        
        # 2. Generate speech
        audio_path = f"{image_path}_description.mp3"
        self._text_to_speech(description, audio_path)
        
        return {"description": description, "audio": audio_path}
    
    def _analyze_image(self, path: str) -> str:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image for a visually impaired person."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }]
        )
        return response.choices[0].message.content
    
    def _text_to_speech(self, text: str, path: str):
        response = client.audio.speech.create(model="tts-1", voice="nova", input=text)
        with open(path, "wb") as f:
            f.write(response.content)

# Usage:
# assistant = MultiModalAssistant()
# result = assistant.analyze_and_describe("photo.jpg")
```

### Multi-Modal Checklist

- [ ] I can send images to GPT-4 Vision for analysis
- [ ] I understand DALL-E image generation
- [ ] I can transcribe audio with Whisper
- [ ] I can generate speech with TTS
- [ ] I can combine modalities in an application

---

## Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [OpenAI Vision Guide](https://platform.openai.com/docs/guides/vision)
- [OpenAI Audio Guide](https://platform.openai.com/docs/guides/text-to-speech)
