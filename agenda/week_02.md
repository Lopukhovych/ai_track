# Week 2: Build a Chatbot with Memory

**Month:** 1 (First Steps) | **Duration:** 6-8 hours

---

## Overview

Last week you made single API calls. This week you'll build a real chatbot that **remembers the conversation**. You'll learn about conversation history, system prompts, and how to give the AI a personality.

---

## Learning Objectives

By the end of this week, you will:
- Understand how conversation memory works
- Use system prompts to control AI behavior
- Build a chatbot that remembers what you said
- Create different chatbot personalities
- Save conversations to files

---

## Theory (2 hours)

### 1. Why Doesn't the AI Remember? (30 min)

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

### 2. The Three Message Roles (30 min)

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

### 3. System Prompts (30 min)

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

### 4. Context Window Limits (30 min)

**Problem:** You can't send infinite history. Models have limits.

| Model | Context Window |
|-------|----------------|
| GPT-4o-mini | 128,000 tokens |
| GPT-4o | 128,000 tokens |
| Claude Sonnet | 200,000 tokens |

**Strategies when history gets too long:**
1. **Truncate old messages:** Keep only recent N messages
2. **Summarize:** Compress old conversation into a summary
3. **Start fresh:** Clear history when switching topics

### 5. Streaming Responses (20 min)

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
    model="gpt-4o-mini",
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
        model="gpt-4o-mini",
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

## Hands-On Practice (4-6 hours)

### Task 1: Simple Memory Chatbot (60 min)

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
        model="gpt-4o-mini",
        messages=messages
    )
    
    # Get AI response
    ai_message = response.choices[0].message.content
    
    # Add AI response to history
    messages.append({"role": "assistant", "content": ai_message})
    
    print(f"AI: {ai_message}\n")
```

**Test it:**
```
You: My name is Bob
AI: Nice to meet you, Bob!

You: What's my name?
AI: Your name is Bob!

You: quit
Goodbye!
```

### Task 2: Chatbot Class (60 min)

Refactor into a reusable class:

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
            model="gpt-4o-mini",
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

### Task 3: Different Personalities (45 min)

Create chatbots with different personalities:

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

### Task 4: Save and Load Conversations (45 min)

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
    # Create and have a conversation
    bot = PersistentChatbot("You are a storyteller.")
    
    bot.chat("Start a story about a dragon")
    bot.chat("What happens next?")
    
    # Save it
    filename = bot.save_conversation()
    
    # Load it later
    bot2 = PersistentChatbot.load_conversation(filename)
    print(bot2.chat("Continue the story from where you left off"))
```

### Task 5: Conversation Summary (60 min)

When conversation gets long, summarize it:

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
        # Get all messages except system prompt
        history = self.messages[1:]
        
        # Create summary prompt
        history_text = "\n".join([
            f"{m['role']}: {m['content']}" 
            for m in history
        ])
        
        summary_response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Summarize this conversation in 2-3 sentences."},
                {"role": "user", "content": history_text}
            ]
        )
        
        summary = summary_response.choices[0].message.content
        
        # Replace history with summary
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

### Task 6: Interactive CLI Chat (60 min)

Build a polished command-line interface:

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

## Knowledge Checklist

- [ ] I understand why I need to send conversation history
- [ ] I know the three message roles (system, user, assistant)
- [ ] I can write effective system prompts
- [ ] I built a chatbot that remembers conversations
- [ ] I can create different chatbot personalities
- [ ] I can save and load conversations
- [ ] I understand context window limits

---

## Deliverables

1. `chatbot.py` — Simple memory chatbot
2. `chatbot_class.py` — Reusable Chatbot class
3. `personalities.py` — Multiple chatbot personalities
4. `cli_chat.py` — Polished CLI chat interface

---

## What's Next?

Next week, you'll learn how to make the chatbot return **structured data** (like JSON) reliably. This is essential for building real applications.

---

## Resources

- [OpenAI Chat Completions Guide](https://platform.openai.com/docs/guides/chat)
- [Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
