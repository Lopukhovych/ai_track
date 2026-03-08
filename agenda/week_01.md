# Week 1: API Fundamentals, Chatbot & Structured Output

**Month:** 1 (First Steps) | **Duration:** 18-24 hours

---

## Overview

This week covers everything you need to go from zero to a working, production-quality chatbot. You'll make your first API call, build a chatbot that remembers conversations, and learn to get structured (JSON) outputs reliably.

**No prior AI experience needed.**

---

## Learning Objectives

By the end of this week, you will:
- Understand what an LLM is and how it works (conceptually)
- Have Python and your development environment set up
- Make your first API call to ChatGPT
- Understand how AI applications are billed (tokens)
- Understand how conversation memory works
- Use system prompts to control AI behavior
- Build a chatbot that remembers what you said
- Create different chatbot personalities
- Save conversations to files
- Understand prompt engineering patterns (zero-shot, few-shot, chain-of-thought)
- Get the AI to return valid JSON consistently
- Use Pydantic to validate AI outputs
- Build retry logic for when outputs fail validation
- Handle hallucinations and reduce them

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| Chat / Chatbot | `gpt-5-mini` | `llama3.1:8b` |
| Structured JSON output | `gpt-5-mini` | `qwen2.5:7b` (better JSON compliance) |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b   # general chat
ollama pull qwen2.5:7b    # structured output / JSON
```

```python
# Use scripts/model_config.py for a drop-in replacement:
# AI_PROVIDER=ollama python your_script.py
from scripts.model_config import get_client, CHAT_MODEL, STRUCTURED_MODEL
```

---

## Theory

### Part 1: What is AI? Your First API Call

#### 1. What is AI? What is an LLM? (45 min)

**Artificial Intelligence (AI):** Software that can perform tasks that typically require human intelligence.

**Large Language Model (LLM):** A specific type of AI that understands and generates text. Examples: ChatGPT, Claude, Gemini.

**How does an LLM work? (Simplified)**
```
You type: "What is the capital of France?"
     ↓
The LLM predicts the most likely next words based on patterns it learned
     ↓
Output: "The capital of France is Paris."
```

**Key insight:** LLMs don't "know" things like humans do. They predict likely text based on patterns from training data. This is why they sometimes make things up (called "hallucinations").

**What can LLMs do?**
- Answer questions
- Write text (emails, code, stories)
- Summarize documents
- Translate languages
- Analyze data
- Have conversations

**What can't they do well?**
- Math (they guess, don't calculate)
- Access real-time information (unless connected to the internet)
- Remember previous conversations (unless you tell them to)
- Be 100% accurate

#### 2. How Do You Use an LLM? (30 min)

**Two ways to use LLMs:**

| Method | Description | Example |
|--------|-------------|---------|
| **Chat interface** | Type in a web browser | ChatGPT.com, Claude.ai |
| **API** | Send requests from code | What we'll learn |

**Why use the API?**
- Build your own applications
- Process data automatically
- Integrate with other systems
- Customize behavior

**The basic flow:**
```
Your Code  →  API Request  →  OpenAI Servers  →  Response  →  Your Code
```

#### 3. Understanding Tokens and Pricing (30 min)

**What is a token?**
- A token ≈ 4-6 characters of English text
- "Hello world" = 2 tokens
- "Artificial Intelligence" = 2 tokens
- A page of text ≈ 400-500 tokens

**Why tokens matter:**
- You pay per token (input + output)
- Models have token limits (context window)

**Example pricing (gpt-5-mini):**
- Input: $0.25 per 1 million tokens
- Output: $2.00 per 1 million tokens
- **Practical cost:** ~$0.001 for a typical question/answer
- [Check here](https://developers.openai.com/api/docs/models/gpt-5-mini)

**Don't worry about cost yet** — you'll spend pennies while learning.

#### 4. The AI Engineering Role (15 min)

**What is AI Engineering?**
- Building applications that use LLMs
- Not training models from scratch (that's ML Engineering)
- Focus: prompts, APIs, reliability, user experience

**What you'll learn in this course:**
- How to talk to AI models (APIs)
- How to get reliable outputs (prompting)
- How to connect AI to your data (RAG)
- How to make AI take actions (agents)
- How to deploy to production

---

### Part 2: Build a Chatbot with Memory

#### 1. Why Doesn't the AI Remember? (30 min)

**Important insight:** Each API call is independent. The AI doesn't remember previous calls.

```python
# Call 1
"My name is Alice"  →  "Nice to meet you, Alice!"

# Call 2 (new request - AI doesn't remember!)
"What's my name?"  →  "I don't know your name."
```

**Solution:** You must send the entire conversation history with each request.

```python
# Call 1
messages = [{"role": "user", "content": "My name is Alice"}]
# Response: "Nice to meet you, Alice!"

# Call 2 - Include previous messages!
messages = [
    {"role": "user", "content": "My name is Alice"},
    {"role": "assistant", "content": "Nice to meet you, Alice!"},
    {"role": "user", "content": "What's my name?"}
]
# Response: "Your name is Alice!"
```

#### 2. The Three Message Roles (30 min)

| Role | Who | Purpose |
|------|-----|---------|
| **system** | You (hidden) | Instructions, personality, rules |
| **user** | The human | Questions and requests |
| **assistant** | The AI | AI's responses |

**Example conversation:**
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello! How can I help?"},
    {"role": "user", "content": "What's the weather?"}
]
```

#### 3. System Prompts (30 min)

The system prompt sets the AI's behavior for the entire conversation.

**Basic system prompt:**
```
You are a helpful assistant.
```

**Detailed system prompt:**
```
You are a friendly customer support agent for TechCorp.

Rules:
- Be helpful and concise
- If you don't know, say "I don't know"
- Never make up information about products
- Keep responses under 3 sentences unless asked for more
```

**System prompts can define:**
- Role and personality
- Knowledge boundaries
- Response format
- Rules and constraints

#### 4. Context Window Limits (30 min)

**Problem:** You can't send infinite history. Models have limits.

| Model         | Context Window   |
|---------------|------------------|
| gpt-5-mini    | 128,000 tokens   |
| GPT-5         | 128,000 tokens   |
| GPT-5.4       | 1,050,000 tokens |
| Claude Sonnet | 200,000 tokens   |

**Strategies when history gets too long:**
1. **Truncate old messages:** Keep only recent N messages
2. **Summarize:** Compress old conversation into a summary
3. **Start fresh:** Clear history when switching topics

#### 5. Streaming Responses (20 min)

**Why streaming matters:**
- Better UX — users see text appearing immediately
- Production apps use streaming (ChatGPT, Claude, etc.)
- Doesn't block while waiting for full response

**Basic streaming:**
```python
from openai import OpenAI
client = OpenAI()

# Enable streaming with stream=True
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True  # This enables streaming
)

# Process chunks as they arrive
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()  # Newline at the end
```

**Streaming with full message collection:**
```python
def stream_chat(messages: list) -> str:
    """Stream response to console, return full message."""
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        stream=True
    )

    full_response = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="", flush=True)
            full_response += content
    print()

    return full_response

# Use it
message = stream_chat([
    {"role": "system", "content": "You are helpful."},
    {"role": "user", "content": "Explain Python in 3 sentences."}
])
# Text streams to screen, and message contains the full response
```

**When to use streaming:**
- ✅ Interactive chat applications
- ✅ Long responses where users wait
- ❌ Batch processing (adds complexity)
- ❌ When you need to validate full response before showing

---

### Part 3: Better Prompts & Structured Output

#### 1. Why Prompts Matter (30 min)

**Prompting is programming.** The better your prompt, the better the output.

**Bad prompt:**
```
Tell me about this product
```

**Good prompt:**
```
You are a product analyst. Analyze this product and return:
- Name
- Category
- Price range (low/medium/high)
- Key features (list of 3-5)

Product description: {description}

Return JSON format only.
```

#### 2. Prompting Techniques (45 min)

| Technique | Description | Example |
|-----------|-------------|---------|
| **Zero-shot** | Just describe what you want | "Summarize this text in 3 sentences" |
| **Few-shot** | Give examples | "Input: X → Output: Y. Now do: Z" |
| **Chain-of-thought** | Ask for reasoning | "Think step by step, then give final answer" |
| **Role prompting** | Assign expertise | "You are an expert lawyer..." |

**Few-shot example:**
```
Extract the sentiment from these reviews:

Review: "I love this product!" → Sentiment: positive
Review: "Terrible, waste of money" → Sentiment: negative
Review: "It's okay, nothing special" → Sentiment: neutral

Review: "Best purchase ever!" → Sentiment:
```

#### 3. Structured Output (30 min)

**Why JSON?**
- Predictable format for code to process
- Can be validated
- Easy to integrate with databases/APIs

**Methods to get JSON:**

| Method | Reliability | How |
|--------|-------------|-----|
| **Ask nicely** | 70% | "Return JSON..." |
| **JSON mode** | 95% | `response_format={"type": "json_object"}` |
| **Structured outputs** | 99% | Provide Pydantic schema |

#### 4. Validation with Pydantic (15 min)

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool
```

**Pydantic validates:**
- Required fields are present
- Types are correct
- Values are within constraints

#### 5. Human-in-the-Loop Patterns (30 min)

**Why human-in-the-loop?**
AI isn't perfect. For high-stakes decisions, you need human approval:

```
User Request → [AI Processes] → [Human Reviews] → [Action Executed]
                                      ↓
                              Approve / Reject / Edit
```

**When to use:**

| Scenario | Reliability |
|--------|-------------|
| Sending emails | AI might write inappropriate content |
| Financial transactions | Errors could be costly |
| Customer responses | Brand reputation at stake |
| Content publishing | Legal/compliance requirements |
| Data deletion | Irreversible action |

**Confidence-based escalation:**
```python
if response.confidence > 0.9:
    execute_automatically()
elif response.confidence > 0.7:
    execute_with_notification()  # Human can review after
else:
    require_human_approval()     # Wait for human
```

**Design patterns:**
1. **Approval queue** — AI drafts, human approves before sending
2. **Suggestion mode** — AI suggests, human decides
3. **Confidence thresholds** — Auto-approve high confidence, escalate low
4. **Audit trail** — Log all AI decisions for human review

---

## Hands-On Practice

### Part 1: API Basics

#### Task 1: Set Up Your Environment (45 min)

**Install Python:**

```bash
# Windows (PowerShell)
winget install Python.Python.3.12

# macOS (Homebrew)
brew install python@3.12

# Verify installation
python --version
```

**Create your project:**

****We don't need to do it in our labs****

```bash
# Install uv (once, globally)
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project folder and initialise with uv
uv init my-ai-project
cd my-ai-project

# Add dependencies (creates .venv and installs automatically)
uv add openai python-dotenv

# Run any script inside the managed environment
uv run python your_script.py
```

**Create project structure:**
```
my-ai-project/
├── .venv/           # Virtual environment (don't edit)
├── .env             # Your API key (secret!)
├── .gitignore       # Files to ignore
└── first_call.py    # Your first script
```

#### Task 2: Get Your API Key (15 min)

1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to API Keys section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-`)

**Create `.env` file:**
```
OPENAI_API_KEY=sk-your-key-here
```

**Create `.gitignore` file:**
```
.env
.venv/
__pycache__/
```

**Important:** Never share your API key or commit it to Git!

#### Task 3: Your First API Call (60 min)

Create `first_call.py`:

```python
# first_call.py - Your first conversation with AI!

from openai import OpenAI
from dotenv import load_dotenv

# Load your API key from .env file
load_dotenv()

# Create the client
client = OpenAI()

# Send a message to the AI
try:
    response = client.chat.completions.create(
        model="gpt-5-mini",  # The AI model to use
        messages=[
            {"role": "user", "content": "Hello! What is artificial intelligence?"}
        ]
    )
    # Print the AI's response
    print(response.choices[0].message.content)

except Exception as e:
    print(f"Error: {e}")
    print("\nCommon fixes:")
    print("- Check your OPENAI_API_KEY in .env file")
    print("- Make sure you have credits at platform.openai.com")
    print("- Check your internet connection")
```

**Run it:**
```bash
python first_call.py
```

**Common errors and fixes:**
| Error | Cause | Fix |
|-------|-------|-----|
| `AuthenticationError` | Invalid API key | Check .env file has correct key |
| `RateLimitError` | Too many requests | Wait a moment, try again |
| `InsufficientQuotaError` | No credits | Add payment method at platform.openai.com |
| `Connection error` | Network issue | Check internet connection |

#### Task 4: Understanding the Code (30 min)

Let's break down what each part does:

```python
from openai import OpenAI      # Import the OpenAI library
from dotenv import load_dotenv # Import tool to read .env file

load_dotenv()                  # Read the API key from .env

client = OpenAI()              # Create connection to OpenAI

response = client.chat.completions.create(
    model="gpt-5-mini",       # Which AI model to use
    messages=[                 # The conversation
        {"role": "user", "content": "Your question here"}
    ]
)

# Get the AI's reply
answer = response.choices[0].message.content
print(answer)
```

**The `messages` list:**
- Each message has a `role` and `content`
- `role` can be: `user` (you), `assistant` (AI), `system` (instructions)
- This is how you have a conversation

#### Task 5: Ask Different Questions (45 min)

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Try different questions!
questions = [
    "What is Python?",
    "Write a haiku about coding",
    "Explain APIs like I'm 10 years old",
    "What's 2 + 2?",  # Try math
]

for question in questions:
    print(f"\n--- Question: {question} ---")

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": question}]
    )

    print(response.choices[0].message.content)
```

#### Task 6: Check Token Usage (30 min)

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Tell me a short joke"}]
)

# Print the response
print("Response:", response.choices[0].message.content)

# Print token usage
print("\n--- Token Usage ---")
print(f"Input tokens: {response.usage.prompt_tokens}")
print(f"Output tokens: {response.usage.completion_tokens}")
print(f"Total tokens: {response.usage.total_tokens}")

# Calculate cost
input_cost = response.usage.prompt_tokens * 0.15 / 1_000_000
output_cost = response.usage.completion_tokens * 0.60 / 1_000_000
print(f"Estimated cost: ${input_cost + output_cost:.6f}")
```

#### Task 7: Interactive Chat (60 min)

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

print("Chat with AI! Type 'quit' to exit.\n")

while True:
    # Get user input
    user_input = input("You: ")

    # Check if user wants to quit
    if user_input.lower() == 'quit':
        print("Goodbye!")
        break

    # Send to AI
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": user_input}]
    )

    # Print AI response
    print(f"AI: {response.choices[0].message.content}\n")
```

---

### Part 2: Chatbot with Memory

#### Task 1: Simple Memory Chatbot (60 min)

Create `chatbot.py`:

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Store conversation history
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]

print("Chatbot ready! Type 'quit' to exit.\n")

while True:
    # Get user input
    user_input = input("You: ")

    if user_input.lower() == 'quit':
        print("Goodbye!")
        break

    # Add user message to history
    messages.append({"role": "user", "content": user_input})

    # Send entire conversation to AI
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages
    )

    # Get AI response
    ai_message = response.choices[0].message.content

    # Add AI response to history
    messages.append({"role": "assistant", "content": ai_message})

    print(f"AI: {ai_message}\n")
```

#### Task 2: Chatbot Class (60 min)

```python
# chatbot_class.py
from openai import OpenAI
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Chatbot:
    def __init__(self, system_prompt: str = "You are a helpful assistant."):
        self.client = OpenAI()
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]

    def chat(self, user_message: str) -> str:
        """Send a message and get a response."""
        # Add user message
        self.messages.append({"role": "user", "content": user_message})

        # Get AI response
        response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=self.messages
        )

        ai_message = response.choices[0].message.content

        # Add to history
        self.messages.append({"role": "assistant", "content": ai_message})

        return ai_message

    def clear_history(self):
        """Reset conversation, keeping system prompt."""
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def get_history(self) -> list:
        """Return conversation history."""
        return self.messages[1:]  # Exclude system prompt

# Test it
if __name__ == "__main__":
    bot = Chatbot("You are a friendly assistant who loves jokes.")

    print(bot.chat("Tell me a joke"))
    print(bot.chat("Another one!"))
    print(bot.chat("What jokes did you tell me?"))
```

#### Task 3: Different Personalities (45 min)

```python
# personalities.py
from chatbot_class import Chatbot

# Pirate assistant
pirate = Chatbot("""
You are a pirate assistant. You:
- Speak like a pirate (arrr, matey, etc.)
- Are helpful but always in character
- Love treasure and the sea
""")

# Professional assistant
professional = Chatbot("""
You are a professional business consultant. You:
- Use formal language
- Give structured, actionable advice
- Focus on efficiency and results
""")

# Teacher assistant
teacher = Chatbot("""
You are a patient teacher. You:
- Explain things step by step
- Use simple language and examples
- Ask if the student understands
- Encourage questions
""")

# Test each one
question = "How do I learn to code?"

print("=== PIRATE ===")
print(pirate.chat(question))

print("\n=== PROFESSIONAL ===")
print(professional.chat(question))

print("\n=== TEACHER ===")
print(teacher.chat(question))
```

#### Task 4: Save and Load Conversations (45 min)

```python
# save_conversations.py
import json
from datetime import datetime
from chatbot_class import Chatbot

class PersistentChatbot(Chatbot):
    def save_conversation(self, filename: str = None):
        """Save conversation to a JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"

        data = {
            "system_prompt": self.system_prompt,
            "messages": self.messages,
            "saved_at": datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Saved to {filename}")
        return filename

    @classmethod
    def load_conversation(cls, filename: str):
        """Load a conversation from a JSON file."""
        with open(filename, 'r') as f:
            data = json.load(f)

        bot = cls(data["system_prompt"])
        bot.messages = data["messages"]

        print(f"Loaded conversation with {len(bot.messages)-1} messages")
        return bot

# Test it
if __name__ == "__main__":
    bot = PersistentChatbot("You are a storyteller.")

    bot.chat("Start a story about a dragon")
    bot.chat("What happens next?")

    filename = bot.save_conversation()

    bot2 = PersistentChatbot.load_conversation(filename)
    print(bot2.chat("Continue the story from where you left off"))
```

#### Task 5: Conversation Summary (60 min)

```python
# summarize.py
from chatbot_class import Chatbot

class SmartChatbot(Chatbot):
    def __init__(self, system_prompt: str, max_messages: int = 20):
        super().__init__(system_prompt)
        self.max_messages = max_messages

    def chat(self, user_message: str) -> str:
        # Check if we need to summarize
        if len(self.messages) > self.max_messages:
            self._summarize_history()

        # Normal chat
        return super().chat(user_message)

    def _summarize_history(self):
        """Compress conversation history into a summary."""
        history = self.messages[1:]

        history_text = "\n".join([
            f"{m['role']}: {m['content']}"
            for m in history
        ])

        summary_response = self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "Summarize this conversation in 2-3 sentences."},
                {"role": "user", "content": history_text}
            ]
        )

        summary = summary_response.choices[0].message.content

        self.messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"Previous conversation summary: {summary}"}
        ]

        print(f"[Summarized {len(history)} messages]")

# Test
if __name__ == "__main__":
    bot = SmartChatbot("You are a helpful assistant.", max_messages=6)

    for i in range(10):
        response = bot.chat(f"Message number {i+1}")
        print(f"Bot: {response[:50]}...")
```

#### Task 6: Interactive CLI Chat (60 min)

```python
# cli_chat.py
from chatbot_class import Chatbot
import sys

def print_help():
    print("""
Commands:
  /clear     - Clear conversation history
  /history   - Show conversation history
  /system    - Change system prompt
  /quit      - Exit the chatbot

Just type normally to chat!
""")

def main():
    print("=" * 50)
    print("  Welcome to AI Chatbot!")
    print("=" * 50)
    print("Type /help for commands\n")

    bot = Chatbot("You are a helpful and friendly assistant.")

    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input.startswith("/"):
            command = user_input.lower()

            if command == "/quit":
                print("Goodbye!")
                break
            elif command == "/clear":
                bot.clear_history()
                print("Conversation cleared.\n")
            elif command == "/history":
                history = bot.get_history()
                if not history:
                    print("No conversation yet.\n")
                else:
                    for msg in history:
                        role = "You" if msg["role"] == "user" else "AI"
                        print(f"{role}: {msg['content'][:100]}...")
                    print()
            elif command == "/help":
                print_help()
            elif command.startswith("/system "):
                new_prompt = user_input[8:]
                bot = Chatbot(new_prompt)
                print(f"System prompt changed.\n")
            else:
                print(f"Unknown command: {command}")
                print_help()
        else:
            # Normal chat
            response = bot.chat(user_input)
            print(f"AI: {response}\n")

if __name__ == "__main__":
    main()
```

---

### Part 3: Better Prompts & Structured Output

#### Task 1: Basic JSON Responses (45 min)

```python
# json_basics.py
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

def analyze_product(description: str) -> dict:
    """Get structured analysis of a product."""
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": """Analyze the product and return JSON with:
{
    "name": "product name",
    "category": "category",
    "sentiment": "positive/negative/neutral",
    "key_features": ["feature1", "feature2", "feature3"]
}
Return ONLY valid JSON, no other text."""
            },
            {"role": "user", "content": description}
        ],
        response_format={"type": "json_object"}  # Enforce JSON
    )

    return json.loads(response.choices[0].message.content)

# Test
product = """
The new iPhone 15 Pro has an amazing camera system with 48MP resolution.
The titanium design makes it lighter than ever. Great battery life too!
"""

result = analyze_product(product)
print(json.dumps(result, indent=2))
```

#### Task 2: Pydantic Validation (60 min)

```python
# pydantic_validation.py
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

# Define your data structure
class ProductAnalysis(BaseModel):
    name: str = Field(description="Product name")
    category: str = Field(description="Product category")
    price_estimate: Optional[float] = Field(None, description="Estimated price in USD")
    sentiment: str = Field(description="positive, negative, or neutral")
    key_features: List[str] = Field(description="3-5 key features")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")

def analyze_product_validated(description: str) -> ProductAnalysis:
    """Get validated product analysis."""

    schema = ProductAnalysis.model_json_schema()

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": f"""Analyze the product. Return valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Return ONLY the JSON object."""
            },
            {"role": "user", "content": description}
        ],
        response_format={"type": "json_object"}
    )

    data = json.loads(response.choices[0].message.content)
    return ProductAnalysis(**data)

# Test
product = "The Sony WH-1000XM5 headphones offer industry-leading noise cancellation."
result = analyze_product_validated(product)
print(f"Name: {result.name}")
print(f"Category: {result.category}")
print(f"Sentiment: {result.sentiment}")
print(f"Features: {result.key_features}")
```

#### Task 3: Retry on Failure (60 min)

```python
# retry_logic.py
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import List
from dotenv import load_dotenv
import json
import time

load_dotenv()
client = OpenAI()

class EmailExtraction(BaseModel):
    sender: str
    subject: str
    is_urgent: bool
    action_items: List[str]
    sentiment: str  # positive, negative, neutral

def extract_with_retry(email_text: str, max_retries: int = 3) -> EmailExtraction:
    """Extract email data with retry logic."""

    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Extract data from the email. Return JSON:
{
    "sender": "name or email",
    "subject": "email subject/topic",
    "is_urgent": true or false,
    "action_items": ["item1", "item2"],
    "sentiment": "positive/negative/neutral"
}"""
                    },
                    {"role": "user", "content": email_text}
                ],
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)
            result = EmailExtraction(**data)
            return result

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(0.5)  # Brief pause before retry

    raise Exception(f"Failed after {max_retries} attempts: {last_error}")

# Test
email = """
From: boss@company.com
Subject: URGENT: Q4 Report Needed

Hi team,

Please complete the Q4 report by tomorrow. Also schedule a review meeting.
This is top priority!

Thanks,
John
"""

result = extract_with_retry(email)
print(f"Sender: {result.sender}")
print(f"Urgent: {result.is_urgent}")
print(f"Actions: {result.action_items}")
```

#### Task 4: Few-Shot Prompting (45 min)

```python
# few_shot.py
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def classify_intent(message: str) -> str:
    """Classify user intent using few-shot prompting."""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": """Classify the user's intent. Examples:

Message: "I want to cancel my subscription"
Intent: cancellation

Message: "How do I reset my password?"
Intent: support

Message: "What plans do you offer?"
Intent: pricing

Message: "Your product is amazing!"
Intent: feedback

Message: "I can't login to my account"
Intent: support

Respond with only the intent category."""
            },
            {"role": "user", "content": message}
        ]
    )

    return response.choices[0].message.content.strip().lower()

# Test various messages
messages = [
    "I want a refund",
    "How much does the pro plan cost?",
    "I love using your app!",
    "My payment didn't go through",
    "Please delete my account"
]

for msg in messages:
    intent = classify_intent(msg)
    print(f"'{msg}' → {intent}")
```

#### Task 5: Chain-of-Thought (45 min)

```python
# chain_of_thought.py
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class ReasonedAnswer(BaseModel):
    reasoning: str
    answer: str
    confidence: float

def answer_with_reasoning(question: str) -> ReasonedAnswer:
    """Get an answer with step-by-step reasoning."""

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": """Think through the problem step by step before answering.

Return JSON:
{
    "reasoning": "Step 1: ... Step 2: ... Step 3: ...",
    "answer": "Your final answer",
    "confidence": 0.0 to 1.0
}"""
            },
            {"role": "user", "content": question}
        ],
        response_format={"type": "json_object"}
    )

    data = json.loads(response.choices[0].message.content)
    return ReasonedAnswer(**data)

# Test
questions = [
    "If a train leaves at 9am going 60mph, and another leaves at 10am going 80mph, when do they meet?",
    "Should I use Python or JavaScript for a machine learning project?",
    "A bat and ball cost $1.10 total. The bat costs $1 more than the ball. How much is the ball?"
]

for q in questions:
    result = answer_with_reasoning(q)
    print(f"\nQ: {q}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Answer: {result.answer}")
    print(f"Confidence: {result.confidence}")
```

#### Task 6: Upgrade Your Chatbot (60 min)

```python
# structured_chatbot.py
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class ChatResponse(BaseModel):
    message: str
    mood: str  # helpful, curious, apologetic, enthusiastic
    follow_up_questions: List[str] = []
    topic: str
    confidence: float

class StructuredChatbot:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.messages = []

    def chat(self, user_message: str) -> ChatResponse:
        """Get a structured response from the chatbot."""

        self.messages.append({"role": "user", "content": user_message})

        system = f"""{self.system_prompt}

Always respond with JSON:
{{
    "message": "your response to the user",
    "mood": "helpful/curious/apologetic/enthusiastic",
    "follow_up_questions": ["suggested question 1", "suggested question 2"],
    "topic": "the main topic discussed",
    "confidence": 0.0 to 1.0 (how confident you are)
}}"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": system},
                *self.messages
            ],
            response_format={"type": "json_object"}
        )

        data = json.loads(response.choices[0].message.content)
        result = ChatResponse(**data)

        # Store just the message in history
        self.messages.append({"role": "assistant", "content": result.message})

        return result

# Interactive test
if __name__ == "__main__":
    bot = StructuredChatbot("You are a helpful coding assistant.")

    print("Structured Chatbot! Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break

        response = bot.chat(user_input)

        print(f"AI [{response.mood}]: {response.message}")
        if response.follow_up_questions:
            print(f"   You could ask: {response.follow_up_questions[0]}")
        print()
```

#### Task 7: Human-in-the-Loop Approval (60 min)

```python
# human_in_loop.py
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class EmailDraft(BaseModel):
    to: str
    subject: str
    body: str
    confidence: float
    risk_level: Literal["low", "medium", "high"]
    needs_review: bool

class ApprovalResult(BaseModel):
    approved: bool
    edited_body: str | None = None
    reason: str | None = None

def draft_email(request: str) -> EmailDraft:
    """AI drafts an email based on user request."""
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": """Draft a professional email based on the request.
Return JSON:
{
    "to": "recipient email",
    "subject": "email subject",
    "body": "email body",
    "confidence": 0.0-1.0,
    "risk_level": "low/medium/high",
    "needs_review": true if sensitive content or low confidence
}"""
            },
            {"role": "user", "content": request}
        ],
        response_format={"type": "json_object"}
    )
    return EmailDraft(**json.loads(response.choices[0].message.content))

def get_human_approval(draft: EmailDraft) -> ApprovalResult:
    """Present draft to human for approval."""
    print("\n" + "="*50)
    print("📧 EMAIL DRAFT FOR APPROVAL")
    print("="*50)
    print(f"To: {draft.to}")
    print(f"Subject: {draft.subject}")
    print(f"Risk Level: {draft.risk_level}")
    print(f"AI Confidence: {draft.confidence:.0%}")
    print("-"*50)
    print(draft.body)
    print("-"*50)

    choice = input("\n[A]pprove / [E]dit / [R]eject: ").strip().lower()

    if choice == 'a':
        return ApprovalResult(approved=True)
    elif choice == 'e':
        edited = input("Enter corrected body: ")
        return ApprovalResult(approved=True, edited_body=edited)
    else:
        reason = input("Rejection reason: ")
        return ApprovalResult(approved=False, reason=reason)

def send_email(draft: EmailDraft):
    """Simulate sending email."""
    print(f"\n✅ Email sent to {draft.to}!")

def email_with_approval(request: str):
    """Complete flow: draft → approval → send."""
    draft = draft_email(request)

    # Auto-approve low risk + high confidence
    if draft.risk_level == "low" and draft.confidence > 0.9 and not draft.needs_review:
        print("Auto-approved (low risk, high confidence)")
        send_email(draft)
        return

    # Otherwise, get human approval
    approval = get_human_approval(draft)

    if approval.approved:
        if approval.edited_body:
            draft.body = approval.edited_body
        send_email(draft)
    else:
        print(f"❌ Email rejected: {approval.reason}")

# Test
if __name__ == "__main__":
    email_with_approval("Write an email to john@company.com apologizing for the delayed shipment")
```

---

## Knowledge Checklist

**API Basics**
- [ ] I understand what an LLM is (predicts text based on patterns)
- [ ] I know LLMs can hallucinate (make things up)
- [ ] I have Python installed and working
- [ ] I have an OpenAI API key
- [ ] I made my first API call successfully
- [ ] I understand what tokens are and why they matter
- [ ] I can run a simple chat loop

**Chatbot with Memory**
- [ ] I understand why I need to send conversation history
- [ ] I know the three message roles (system, user, assistant)
- [ ] I can write effective system prompts
- [ ] I built a chatbot that remembers conversations
- [ ] I can create different chatbot personalities
- [ ] I can save and load conversations
- [ ] I understand context window limits

**Structured Output**
- [ ] I understand zero-shot, few-shot, and chain-of-thought prompting
- [ ] I can get JSON responses using `response_format`
- [ ] I can validate AI outputs with Pydantic
- [ ] I can build retry logic for failed validations
- [ ] I can use few-shot examples to improve accuracy
- [ ] I upgraded my chatbot to return structured data
- [ ] I understand when and how to implement human-in-the-loop patterns
- [ ] I can build confidence-based approval workflows

---

## Deliverables

**API Basics**
1. Working Python environment with OpenAI library
2. `.env` file with your API key
3. `first_call.py` script that talks to GPT
4. Interactive chat script working

**Chatbot with Memory**
1. `chatbot.py` — Simple memory chatbot
2. `chatbot_class.py` — Reusable Chatbot class
3. `personalities.py` — Multiple chatbot personalities
4. `cli_chat.py` — Polished CLI chat interface

**Structured Output**
1. `json_basics.py` — Basic JSON extraction
2. `pydantic_validation.py` — Validated extraction
3. `retry_logic.py` — Retry on validation failure
4. `few_shot.py` — Intent classifier with examples
5. `structured_chatbot.py` — Chatbot with structured responses
6. `human_in_loop.py` — Email assistant with approval workflow

---

## Common Problems

**"ModuleNotFoundError: No module named 'openai'"**
- Make sure virtual environment is activated
- Run: `uv add openai`

**"AuthenticationError"**
- Check your API key in `.env`
- Make sure there are no extra spaces

**"RateLimitError"**
- You're sending too many requests
- Wait a few seconds and try again

---

## What's Next?

Next week, you'll connect your chatbot to your own documents! This is called RAG (Retrieval-Augmented Generation) — the most important technique in AI engineering.

---

## Resources

- [OpenAI Quickstart](https://platform.openai.com/docs/quickstart)
- [OpenAI Chat Completions Guide](https://platform.openai.com/docs/guides/chat)
- [OpenAI JSON Mode](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [OpenAI Pricing](https://openai.com/pricing)
