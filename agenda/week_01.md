# Week 1: What is AI? Your First API Call

**Month:** 1 (First Steps) | **Duration:** 6-8 hours

---

## Overview

Welcome! This week you'll understand what AI actually is, why it matters, and make your first call to a real AI model. By the end, you'll have talked to GPT and seen it respond to you.

**No prior AI experience needed.**

---

## Learning Objectives

By the end of this week, you will:
- Understand what an LLM is and how it works (conceptually)
- Have Python and your development environment set up
- Make your first API call to ChatGPT
- See AI respond to your questions
- Understand how AI applications are billed (tokens)

---

## Theory (2 hours)

### 1. What is AI? What is an LLM? (45 min)

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

### 2. How Do You Use an LLM? (30 min)

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

### 3. Understanding Tokens and Pricing (30 min)

**What is a token?**
- A token ≈ 4 characters of English text
- "Hello world" = 2 tokens
- "Artificial Intelligence" = 2 tokens
- A page of text ≈ 400-500 tokens

**Why tokens matter:**
- You pay per token (input + output)
- Models have token limits (context window)

**Example pricing (GPT-4o-mini):**
- Input: $0.15 per 1 million tokens
- Output: $0.60 per 1 million tokens
- **Practical cost:** ~$0.001 for a typical question/answer

**Don't worry about cost yet** — you'll spend pennies while learning.

### 4. The AI Engineering Role (15 min)

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

## Hands-On Practice (4-6 hours)

### Task 1: Set Up Your Environment (45 min)

**Install Python:**

```bash
# Windows (PowerShell)
winget install Python.Python.3.12

# Verify installation
python --version
```

**Create your project:**

```bash
# Create project folder
mkdir my-ai-project
cd my-ai-project

# Create virtual environment
python -m venv .venv

# Activate it (Windows)
.venv\Scripts\activate

# Install the OpenAI library
pip install openai python-dotenv
```

**Create project structure:**
```
my-ai-project/
├── .venv/           # Virtual environment (don't edit)
├── .env             # Your API key (secret!)
├── .gitignore       # Files to ignore
└── first_call.py    # Your first script
```

### Task 2: Get Your API Key (15 min)

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

### Task 3: Your First API Call (60 min)

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
        model="gpt-4o-mini",  # The AI model to use
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

**You should see the AI's response!**

**Common errors and fixes:**
| Error | Cause | Fix |
|-------|-------|-----|
| `AuthenticationError` | Invalid API key | Check .env file has correct key |
| `RateLimitError` | Too many requests | Wait a moment, try again |
| `InsufficientQuotaError` | No credits | Add payment method at platform.openai.com |
| `Connection error` | Network issue | Check internet connection |

### Task 4: Understanding the Code (30 min)

Let's break down what each part does:

```python
from openai import OpenAI      # Import the OpenAI library
from dotenv import load_dotenv # Import tool to read .env file

load_dotenv()                  # Read the API key from .env

client = OpenAI()              # Create connection to OpenAI

response = client.chat.completions.create(
    model="gpt-4o-mini",       # Which AI model to use
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

### Task 5: Ask Different Questions (45 min)

Modify your script to ask different things:

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
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": question}]
    )
    
    print(response.choices[0].message.content)
```

**Experiment!** Ask your own questions.

### Task 6: Check Token Usage (30 min)

See how many tokens you're using:

```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
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

### Task 7: Interactive Chat (60 min)

Build a simple chat loop:

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
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}]
    )
    
    # Print AI response
    print(f"AI: {response.choices[0].message.content}\n")
```

**Try it out!** Have a conversation with the AI.

---

## Knowledge Checklist

- [ ] I understand what an LLM is (predicts text based on patterns)
- [ ] I know LLMs can hallucinate (make things up)
- [ ] I have Python installed and working
- [ ] I have an OpenAI API key
- [ ] I made my first API call successfully
- [ ] I understand what tokens are and why they matter
- [ ] I can run a simple chat loop

---

## Deliverables

1. Working Python environment with OpenAI library
2. `.env` file with your API key
3. `first_call.py` script that talks to GPT
4. Interactive chat script working

---

## Common Problems

**"ModuleNotFoundError: No module named 'openai'"**
- Make sure virtual environment is activated
- Run: `pip install openai`

**"AuthenticationError"**
- Check your API key in `.env`
- Make sure there are no extra spaces

**"RateLimitError"**
- You're sending too many requests
- Wait a few seconds and try again

---

## What's Next?

Next week, you'll build a real chatbot that remembers the conversation. You'll learn about conversation history and system prompts.

---

## Resources

- [OpenAI Quickstart](https://platform.openai.com/docs/quickstart)
- [OpenAI Pricing](https://openai.com/pricing)
- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
