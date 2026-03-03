# Portfolio Project #2: AI Agent

**Weeks 9-12 Milestone Project**

Build an AI agent that can use tools, reason through multi-step problems, and take actions.

---

## Requirements

### Core Features
- [ ] Tool definitions (3+ tools minimum)
- [ ] Tool execution loop
- [ ] ReAct-style reasoning (Thought → Action → Observation)
- [ ] Multi-step task completion
- [ ] Conversation memory

### Suggested Tools
Pick 3+ from:
- Web search (via API)
- Calculator
- File reader/writer
- Database query
- API calls (weather, stocks, etc.)
- Code execution

### Production Quality
- [ ] Tool error handling
- [ ] Max iterations limit
- [ ] Timeout handling
- [ ] Logging of agent steps

---

## Suggested Structure

```
02_ai_agent/
├── README.md
├── requirements.txt
├── .env
├── src/
│   ├── __init__.py
│   ├── agent.py          # Main agent loop
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── calculator.py
│   │   └── file_ops.py
│   ├── memory.py         # Conversation history
│   └── main.py           # Entry point
├── tests/
│   └── test_agent.py
└── notebooks/
    └── agent_demo.ipynb
```

---

## Getting Started

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Add API keys

# 3. Run agent
python src/main.py "Research the weather in Paris and convert the temperature to Fahrenheit"
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

Agent Response: A 15% tip on $47.50 would be $7.13, 
               making your total $54.63.
```

---

## Interview Talking Points

1. **ReAct pattern** - Explain Thought → Action → Observation cycle
2. **Tool design** - How did you define tool schemas?
3. **Error handling** - What happens when a tool fails?
4. **Infinite loops** - How do you prevent them?
5. **Observability** - How do you debug agent behavior?
6. **Autonomy vs Control** - How much freedom should the agent have?
