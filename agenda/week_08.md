# Week 8: Tool Calling & Function Execution

**Month:** 3 (Intelligence) | **Duration:** 6-8 hours

---

## Overview

So far your AI can plan and reason. This week you'll teach it to **take actions** — search the web, query databases, send emails, and more. This is called **tool calling** and it's how AI goes from chatbot to useful assistant.

---

## Learning Objectives

By the end of this week, you will:
- Understand how tool calling works
- Define tools with proper schemas
- Handle tool calls and return results
- Chain multiple tool calls together
- Build an AI that can actually DO things

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| Tool calling / function calling | `gpt-4o-mini` | `llama3.1:8b` |
| Structured tool schemas | `gpt-4o-mini` | `qwen2.5:7b` (reliable JSON/schema compliance) |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b   # supports tool calling natively
ollama pull qwen2.5:7b    # better structured output for complex schemas
```

```python
from scripts.model_config import get_client, CHAT_MODEL
# llama3.1 and qwen2.5 both support the OpenAI tools[] parameter format
```

---

## Theory (2 hours)

### 1. What is Tool Calling? (30 min)

**Before tools:** AI can only generate text
```
User: What's the weather in London?
AI: I don't have real-time weather data.
```

**With tools:** AI can execute functions
```
User: What's the weather in London?
AI: [calls get_weather("London")]
    → "It's 15°C and cloudy in London."
```

**The magic:** AI decides WHEN and HOW to use tools.

### 2. How Tool Calling Works (30 min)

```
1. You → Define tools (name, description, parameters)
2. User → Sends question
3. AI → Decides to call tools, returns: {"name": "tool_name", "args": {...}}
4. You → Execute the function with those arguments
5. You → Send results back to AI
6. AI → Generates final response using results
```

```
┌─────────────┐    "What's the weather?"    ┌─────────────┐
│    User     │ ──────────────────────────→ │     AI      │
└─────────────┘                              └─────────────┘
                                                   │
                                    Response with tool_call:
                                    get_weather(city="London")
                                                   ↓
┌─────────────┐    Call function                 ┌─────────────┐
│  Your Code  │ ←────────────────────────────────│    AI       │
└─────────────┘                                  └─────────────┘
       │
       │  Execute: requests.get("weather-api/London")
       │  Result: {"temp": 15, "condition": "cloudy"}
       ↓
┌─────────────┐    Send result back             ┌─────────────┐
│  Your Code  │ ───────────────────────────────→│    AI       │
└─────────────┘                                 └─────────────┘
                                                      │
                                        "It's 15°C and cloudy"
                                                      ↓
┌─────────────┐                                 ┌─────────────┐
│    User     │ ←───────────────────────────────│    AI       │
└─────────────┘                                 └─────────────┘
```

### 3. Tool Schemas (30 min)

Tools are defined with JSON Schema:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature units"
                    }
                },
                "required": ["city"]
            }
        }
    }
]
```

**Key points:**
- Clear names and descriptions help AI choose correctly
- Define required vs optional parameters
- Use enums to constrain choices

### 4. Parallel vs Sequential Tools (30 min)

**Parallel:** AI calls multiple tools at once
```
User: "Weather in London and Paris?"
AI: [
    get_weather("London"),
    get_weather("Paris")
]  # Happens simultaneously
```

**Sequential:** AI needs one result before calling the next
```
User: "Book me on the cheapest flight to London"
AI: 1. search_flights("London")  # Get options
    2. book_flight(flight_id)     # Book the cheapest one
```

---

## Hands-On Practice (4-6 hours)

### Task 1: First Tool (45 min)

```python
# first_tool.py
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

# Define the tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current date and time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone (e.g., 'UTC', 'US/Eastern')"
                    }
                },
                "required": []
            }
        }
    }
]

# Implement the function
def get_current_time(timezone: str = "UTC") -> str:
    from datetime import datetime
    import pytz

    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z")
    except:
        return f"Unknown timezone: {timezone}"

# Available functions mapping
available_functions = {
    "get_current_time": get_current_time
}

def chat_with_tools(user_message: str) -> str:
    """Chat with tool support."""

    messages = [{"role": "user", "content": user_message}]

    # First call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    message = response.choices[0].message

    # Check if AI wants to use a tool
    if message.tool_calls:
        # Add the assistant's message (with tool call)
        messages.append(message)

        # Execute each tool
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"📞 Calling: {function_name}({function_args})")

            # Call the function
            function = available_functions[function_name]
            result = function(**function_args)

            print(f"📋 Result: {result}")

            # Add tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

        # Get final response
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        return final_response.choices[0].message.content

    # No tools needed
    return message.content

# Test
if __name__ == "__main__":
    print(chat_with_tools("What time is it in Tokyo?"))
```

### Task 2: Multiple Tools (60 min)

```python
# multi_tools.py
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

# Define multiple tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform mathematical calculation",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression like '2+2' or 'sqrt(16)'"}
                },
                "required": ["expression"]
            }
        }
    }
]

# Implement functions (mock for demo)
def get_weather(city: str) -> dict:
    """Mock weather data."""
    weather_data = {
        "London": {"temp": 15, "condition": "cloudy"},
        "Paris": {"temp": 18, "condition": "sunny"},
        "Tokyo": {"temp": 22, "condition": "clear"},
    }
    return weather_data.get(city, {"temp": 20, "condition": "unknown"})

def search_wikipedia(query: str) -> str:
    """Mock Wikipedia search."""
    return f"Wikipedia summary for '{query}': This is a mock result about {query}."

def calculate(expression: str) -> float:
    """Safe math calculation."""
    import math
    # Only allow safe operations
    allowed = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "abs": abs}
    try:
        return eval(expression, {"__builtins__": {}}, allowed)
    except:
        return "Error in calculation"

available_functions = {
    "get_weather": get_weather,
    "search_wikipedia": search_wikipedia,
    "calculate": calculate
}

def chat_with_tools(user_message: str) -> str:
    """Chat with multiple tools."""

    messages = [{"role": "user", "content": user_message}]

    # Loop to handle multiple tool call rounds
    while True:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        if not message.tool_calls:
            return message.content

        messages.append(message)

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            print(f"🔧 {function_name}({function_args})")

            result = available_functions[function_name](**function_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

# Test
if __name__ == "__main__":
    queries = [
        "What's the weather in Paris?",
        "What's 25 * 4?",
        "Tell me about the Eiffel Tower",
        "What's the weather in London and what's the square root of 144?",
    ]

    for q in queries:
        print(f"\n👤 {q}")
        print(f"🤖 {chat_with_tools(q)}")
```

### Task 3: Tool with Pydantic (45 min)

```python
# pydantic_tools.py
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

# Define tool schemas with Pydantic
class SearchParams(BaseModel):
    query: str = Field(description="Search query")
    max_results: int = Field(default=5, description="Max results to return")

class EmailParams(BaseModel):
    to: str = Field(description="Recipient email")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body")

# Convert Pydantic to OpenAI tool format
def pydantic_to_tool(name: str, description: str, model: type[BaseModel]) -> dict:
    """Convert Pydantic model to OpenAI tool definition."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": model.model_json_schema()
        }
    }

tools = [
    pydantic_to_tool("search_documents", "Search company documents", SearchParams),
    pydantic_to_tool("send_email", "Send an email", EmailParams)
]

# Implementations
def search_documents(query: str, max_results: int = 5) -> List[str]:
    return [f"Document about {query} (result {i})" for i in range(max_results)]

def send_email(to: str, subject: str, body: str) -> dict:
    print(f"📧 Sending to: {to}")
    print(f"   Subject: {subject}")
    return {"status": "sent", "to": to}

available_functions = {
    "search_documents": search_documents,
    "send_email": send_email
}

# Chat function same as before...
def chat(message: str) -> str:
    messages = [{"role": "user", "content": message}]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        messages.append(msg)

        for tc in msg.tool_calls:
            func = available_functions[tc.function.name]
            args = json.loads(tc.function.arguments)
            result = func(**args)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })

        final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        return final.choices[0].message.content

    return msg.content

# Test
if __name__ == "__main__":
    print(chat("Search for vacation policy documents"))
    print(chat("Send an email to boss@company.com about the meeting tomorrow"))
```

### Task 4: Database Tool (60 min)

```python
# database_tool.py
from openai import OpenAI
from dotenv import load_dotenv
import json
import sqlite3

load_dotenv()
client = OpenAI()

# Create a simple database
def setup_database():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            department TEXT,
            salary REAL,
            hire_date TEXT
        )
    """)

    employees = [
        (1, "Alice Smith", "Engineering", 95000, "2022-01-15"),
        (2, "Bob Johnson", "Marketing", 75000, "2021-06-01"),
        (3, "Carol Williams", "Engineering", 105000, "2020-03-20"),
        (4, "David Brown", "Sales", 85000, "2023-02-10"),
        (5, "Eve Davis", "Engineering", 115000, "2019-08-05"),
    ]

    cursor.executemany("INSERT INTO employees VALUES (?,?,?,?,?)", employees)
    conn.commit()

    return conn

# Database query tool
tools = [
    {
        "type": "function",
        "function": {
            "name": "query_database",
            "description": "Execute a SQL query on the employees table. Columns: id, name, department, salary, hire_date",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Global database connection
db_conn = setup_database()

def query_database(query: str) -> list:
    """Execute a SQL query."""
    # Safety: only allow SELECT
    if not query.strip().upper().startswith("SELECT"):
        return {"error": "Only SELECT queries are allowed"}

    try:
        cursor = db_conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return {"error": str(e)}

available_functions = {"query_database": query_database}

def chat(message: str) -> str:
    messages = [
        {"role": "system", "content": "You help users query the employee database. Generate SQL queries to answer their questions."},
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        messages.append(msg)

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"🔍 SQL: {args['query']}")

            result = query_database(args['query'])

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result)
            })

        final = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
        return final.choices[0].message.content

    return msg.content

# Test
if __name__ == "__main__":
    queries = [
        "Who are the engineers?",
        "What's the average salary?",
        "Who was hired most recently?",
        "List employees earning over 100k"
    ]

    for q in queries:
        print(f"\n👤 {q}")
        print(f"🤖 {chat(q)}")
```

### Task 5: Tool Calling Agent Class (45 min)

```python
# tool_agent.py
from openai import OpenAI
from dotenv import load_dotenv
from typing import Callable
import json

load_dotenv()

class ToolAgent:
    """A reusable agent that can use tools."""

    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self.client = OpenAI()
        self.system_prompt = system_prompt
        self.tools = []
        self.functions = {}
        self.conversation = []

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: dict,
        function: Callable
    ):
        """Register a tool."""
        self.tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        })
        self.functions[name] = function

    def chat(self, message: str, max_rounds: int = 5) -> str:
        """Chat with the agent."""

        self.conversation.append({"role": "user", "content": message})

        for _ in range(max_rounds):
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation
                ],
                tools=self.tools if self.tools else None
            )

            msg = response.choices[0].message

            if not msg.tool_calls:
                self.conversation.append(msg)
                return msg.content

            self.conversation.append(msg)

            for tc in msg.tool_calls:
                func = self.functions[tc.function.name]
                args = json.loads(tc.function.arguments)
                result = func(**args)

                self.conversation.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result)
                })

        return "Max tool rounds reached"

    def reset(self):
        """Reset conversation."""
        self.conversation = []

# Usage
if __name__ == "__main__":
    agent = ToolAgent("You are a helpful assistant with access to tools.")

    # Register tools
    agent.register_tool(
        name="get_weather",
        description="Get weather for a city",
        parameters={
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        },
        function=lambda city: {"temp": 20, "city": city}
    )

    agent.register_tool(
        name="calculate",
        description="Calculate a math expression",
        parameters={
            "type": "object",
            "properties": {"expr": {"type": "string"}},
            "required": ["expr"]
        },
        function=lambda expr: eval(expr)
    )

    print(agent.chat("What's 25 * 4 and the weather in Berlin?"))
```

---

## 🎯 Optional Challenges

*Tools are the building blocks of agents. Master them here.*

### Challenge 1: Database Query Tool
Build a tool that converts natural language to SQL:
```python
def query_database(question: str) -> dict:
    # User: "How many users signed up this month?"
    # → Generate SQL, execute, return results
```

### Challenge 2: Real API Integration
Create a tool that calls a real external API:
- Weather API (OpenWeatherMap)
- Stock prices (Alpha Vantage)
- News headlines (NewsAPI)
Handle errors, rate limits, and missing data gracefully.

### Challenge 3: File Management Tools
Build a set of tools for file operations:
```python
tools = [
    list_files(directory),
    read_file(path),
    write_file(path, content),
    search_in_files(pattern, directory)
]
```
Create an AI that can "Find all Python files containing 'TODO'".

### Challenge 4: Tool Error Recovery
Create a tool that randomly fails 30% of the time. Build retry logic:
```python
def flaky_tool(input: str) -> str:
    if random.random() < 0.3:
        raise Exception("Service unavailable")
    return "Success!"
```
Make your ToolAgent handle failures gracefully with retries.

### Challenge 5: Tool Usage Analytics
Track all tool calls:
- Which tools are called most?
- Average execution time per tool?
- Which tools fail most?
Build a dashboard or report.

---

## Knowledge Checklist

- [ ] I understand how tool calling works
- [ ] I can define tool schemas
- [ ] I can execute tools and return results to the AI
- [ ] I can handle multiple tools in one conversation
- [ ] I built a reusable ToolAgent class

---

## Deliverables

1. `first_tool.py` — Basic tool calling
2. `multi_tools.py` — Multiple tools
3. `pydantic_tools.py` — Tools with Pydantic
4. `database_tool.py` — SQL query tool
5. `tool_agent.py` — Reusable agent class

---

## What's Next?

Next week: **Agent Frameworks** — LangGraph and CrewAI for building sophisticated agent systems!

---

## Resources

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Tool Use Best Practices](https://docs.anthropic.com/claude/docs/tool-use)
