# Portfolio Project #2: AI Agent

**Week 11 Milestone** | Combines skills from Weeks 7-11

Build an AI agent that uses tools, reasons through multi-step problems, and logs its behavior for observability.

---

## Requirements

### Core Features (Weeks 7-8)
- [ ] Tool definitions — 3+ tools with JSON Schema
- [ ] Tool execution loop with result handling
- [ ] ReAct-style reasoning (Thought → Action → Observation)
- [ ] Multi-step task completion
- [ ] Conversation memory

### Agent Quality (Week 9-10)
- [ ] LangGraph state machine OR custom ReAct loop
- [ ] Checkpointing / session persistence
- [ ] Structured logging of every agent step
- [ ] Observable traces (LangSmith or Langfuse)

### Data Engineering (Week 11)
- [ ] SQL logging of agent runs (queries, tool calls, outcomes)
- [ ] Data quality checks on tool inputs/outputs
- [ ] Pipeline for processing any documents the agent needs

### Production Quality
- [ ] Tool error handling with fallbacks
- [ ] Max iterations limit (prevent infinite loops)
- [ ] Timeout handling
- [ ] Step-by-step logging

### Suggested Tools (pick 3+)
- Web search (SerpAPI, Tavily, or DuckDuckGo)
- Calculator / code execution
- File reader/writer
- Database query
- Weather or other external API
- RAG search over documents

---

## Suggested Structure

```
02_ai_agent/
├── README.md
├── .env.example
├── src/
│   ├── __init__.py
│   ├── agent.py            # Main agent loop (ReAct or LangGraph)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── calculator.py
│   │   └── file_ops.py
│   ├── memory.py           # Conversation history
│   ├── logger.py           # Step logging and SQL storage
│   └── main.py             # Entry point
├── tests/
│   └── test_agent.py
└── notebooks/
    └── agent_demo.ipynb
```

---

## Getting Started

```bash
# 1. Install dependencies
uv sync

# 2. Configure
cp .env.example .env
# Add OPENAI_API_KEY (or AI_PROVIDER=ollama)
# Add tool API keys as needed

# 3. Run agent
uv run python src/main.py "Research the latest Python version and calculate the years since Python 2.0"
```

---

## Model Options

| Task | OpenAI | Ollama |
|------|--------|--------|
| Agent reasoning | `gpt-4o-mini` | `deepseek-r1:7b` (strong reasoning) |
| Tool calls | `gpt-4o-mini` | `llama3.1:8b` |

```bash
ollama pull deepseek-r1:7b
export AI_PROVIDER=ollama
```

---

## Example Agent Flow

```
User: "What's 15% tip on a $47.50 bill?"

Agent Thought: I need to calculate 15% of 47.50
Agent Action: calculator({"expression": "47.50 * 0.15"})
Observation: 7.125

Agent Thought: The tip is $7.125, I should round it
Agent Action: calculator({"expression": "round(7.125, 2)"})
Observation: 7.13

Agent Response: A 15% tip on $47.50 would be $7.13, making your total $54.63.
```

---

## Interview Talking Points

1. **ReAct pattern** — Explain the Thought → Action → Observation cycle
2. **Tool design** — How did you define tool schemas? What makes a good tool?
3. **Error handling** — What happens when a tool fails or returns unexpected data?
4. **Infinite loops** — How do you prevent them? What's your max iterations strategy?
5. **Observability** — How do you debug agent behavior? What do your traces look like?
6. **LangGraph vs custom** — Why did you choose your agent architecture?
