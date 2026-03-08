# Week 14: Deployment & Fine-Tuning

**Month:** 4 (Production & Career) | **Duration:** 8-10 hours

---

## Overview

Time to get your AI apps into production! This week covers **deployment strategies** and when/how to **fine-tune** models for better performance.

**Study Priority:**
- 🔴 **Core:** Docker basics, deployment patterns (2-3 hours)
- 🟡 **Recommended:** Cloud deployment setup (2-3 hours)
- 🟢 **Optional:** Fine-tuning (2-3 hours) — most teams don't need this; read for awareness

---

## Prerequisites

- Basic command line/terminal usage
- Understanding of HTTP/REST APIs (from Week 14)
- Optional: Docker Desktop installed ([docker.com](https://docker.com))

---

## Learning Objectives

By the end of this week, you will:
- Deploy AI applications with Docker
- Set up cloud deployment (basics)
- Understand when fine-tuning makes sense
- Prepare fine-tuning datasets
- Fine-tune a model with OpenAI

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| Deployed app model | `gpt-5-mini` | `llama3.1:8b` (self-hosted in Docker) |
| Fine-tuning | OpenAI fine-tuning API | Ollama + local `ollama create` from Modelfile |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b
# Deploy Ollama itself in Docker alongside your app:
# docker run -d -p 11434:11434 -v ollama:/root/.ollama ollama/ollama
```

```python
from scripts.model_config import get_client, CHAT_MODEL
# In Docker Compose, set OLLAMA_BASE_URL=http://ollama:11434 and AI_PROVIDER=ollama
```

> Running Ollama in Docker lets you self-host the entire stack — no external API dependencies in production.

---

## Theory (2 hours)

### 1. Deployment Options (30 min)

| Option | Pros | Cons |
|--------|------|------|
| **Serverless** (AWS Lambda, Vercel) | Auto-scaling, pay-per-use | Cold starts, time limits |
| **Containers** (Docker, K8s) | Portable, consistent | More to manage |
| **VMs** (EC2, GCE) | Full control | Manual scaling |
| **PaaS** (Heroku, Railway) | Easy deployment | Less control |

**For AI apps, consider:**
- Latency requirements
- Cost (compute + API calls)
- Scaling needs
- State management (vector DBs, memory)

### 2. Docker for AI (30 min)

```dockerfile
# Dockerfile for AI app
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1

# Run
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. When to Fine-Tune (30 min)

**Fine-tuning = training on your data**

**✅ Good reasons:**
- Consistent output format
- Domain-specific style/tone
- Reduce prompt size
- Specific classification tasks

**❌ Bad reasons:**
- Add new knowledge (use RAG instead)
- Simple instruction following
- Cost reduction (often not cheaper)

```
Decision tree:
Q: Can prompt engineering solve it?
  → Yes: Don't fine-tune
  → No: Q: Is it about knowledge?
         → Yes: Use RAG
         → No: Consider fine-tuning
```

### 4. Fine-Tuning Process (30 min)

```
1. Prepare dataset (JSONL format)
   ↓
2. Upload to OpenAI
   ↓
3. Create fine-tuning job
   ↓
4. Wait for training
   ↓
5. Test the model
   ↓
6. Deploy/use new model
```

### 5. Platform Integration (30 min)

**AI in enterprise communication tools:**

| Platform | Integration Method | Key Concepts |
|----------|-------------------|--------------|
| **Microsoft Teams** | Bot Framework, Power Virtual Agents | Adaptive Cards, webhooks |
| **Slack** | Bolt SDK, webhooks | Slash commands, modals |
| **Discord** | discord.py | Commands, interactions |

**Architecture for chat bots:**
```
User Message → [Chat Platform] → [Webhook/Bot API]
                                       ↓
                               [Your AI Service]
                                       ↓
                               [LLM + RAG/Tools]
                                       ↓
                               Response → User
```

**Slack Bot basics:**
```python
# slack_bot_example.py
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os

app = App(token=os.environ["SLACK_BOT_TOKEN"])

@app.message("hello")
def handle_hello(message, say):
    user = message["user"]
    say(f"Hello <@{user}>! How can I help you?")

@app.command("/ask-ai")
def handle_ask_ai(ack, command, respond):
    ack()  # Acknowledge the command
    
    query = command["text"]
    # Call your AI service here
    response = call_ai_service(query)
    
    respond({
        "response_type": "in_channel",
        "text": response
    })

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
```

**API Gateway patterns:**
```
Clients → [API Gateway] → [Rate Limiting] → [Auth] → [AI Service]
               ↓
         [Logging/Metrics]
```

**Common gateways:**
- **Azure API Management** — Enterprise, Azure integration
- **AWS API Gateway** — Serverless, AWS integration
- **Kong** — Open source, Kubernetes
- **Nginx** — Simple, widely used

### 6. 🟡 Optional: Full Fine-Tuning Deep Dive

Fine-tuning is powerful but often not needed. This content is optional but valuable for interview discussions.

**Dataset requirements:**
- Minimum: 10 examples (50-100 recommended)
- Format: JSONL with messages array
- Quality > Quantity

**Cost considerations:**
- Training: ~$0.008 per 1K tokens (GPT-3.5)
- Inference: ~3x base model cost
- Break-even analysis needed!

---

## Hands-On Practice (4-6 hours)

### Task 1: Dockerize Your AI App (60 min)

```python
# main.py - FastAPI AI application
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI(title="AI API")
client = OpenAI()

class ChatRequest(BaseModel):
    message: str
    system_prompt: str = "You are a helpful assistant."

class ChatResponse(BaseModel):
    response: str
    model: str

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": request.message}
            ]
        )
        
        return ChatResponse(
            response=response.choices[0].message.content,
            model="gpt-5-mini"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY main.py .

# Environment variables (provide at runtime)
ENV OPENAI_API_KEY=""

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```txt
# requirements.txt
fastapi==0.109.0
uvicorn==0.27.0
openai==1.12.0
python-dotenv==1.0.0
pydantic==2.6.0
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  ai-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Task 2: Environment Configuration (30 min)

```python
# config.py - Production configuration
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings from environment."""
    
    # API Keys
    openai_api_key: str
    
    # App settings
    app_name: str = "AI API"
    debug: bool = False
    log_level: str = "INFO"
    
    # AI settings
    default_model: str = "gpt-5-mini"
    max_tokens: int = 1000
    temperature: float = 0.7
    
    # Rate limiting
    rate_limit_rpm: int = 60
    
    # Caching
    cache_ttl: int = 3600
    
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()

# Usage in FastAPI
from fastapi import Depends

def get_openai_client(settings: Settings = Depends(get_settings)):
    """Dependency to get OpenAI client."""
    from openai import OpenAI
    return OpenAI(api_key=settings.openai_api_key)
```

```bash
# .env.example
OPENAI_API_KEY=sk-...
APP_NAME=AI API
DEBUG=false
LOG_LEVEL=INFO
DEFAULT_MODEL=gpt-5-mini
RATE_LIMIT_RPM=60
```

### Task 3: Prepare Fine-Tuning Data (60 min)

```python
# prepare_finetuning_data.py
"""
Prepare data for fine-tuning.
Format: JSONL with {"messages": [...]} format
"""
import json
from typing import List, Dict

def create_training_example(
    system: str,
    user: str,
    assistant: str
) -> dict:
    """Create a single training example."""
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant}
        ]
    }

def prepare_customer_support_data() -> List[dict]:
    """Example: Customer support tone training."""
    
    system_prompt = "You are a friendly customer support agent for TechCo. Be helpful, empathetic, and professional."
    
    examples = [
        # Example 1: Order status
        {
            "user": "Where is my order?",
            "assistant": "I'd be happy to help you track your order! Could you please share your order number? It starts with 'TC-' followed by 8 digits. You can find it in your confirmation email. 📦"
        },
        # Example 2: Refund request
        {
            "user": "I want a refund",
            "assistant": "I understand, and I'm here to help make this as smooth as possible. Could you tell me a bit more about what happened? This helps me ensure we get you the right solution. What product would you like to return?"
        },
        # Example 3: Technical issue
        {
            "user": "The app keeps crashing",
            "assistant": "I'm sorry you're experiencing this frustration! Let's get this sorted out quickly. Could you tell me:\n\n1. What device are you using?\n2. When did this start happening?\n3. What were you doing when it crashed?\n\nThis helps me pinpoint the issue faster. 🔧"
        },
        # Example 4: Positive feedback
        {
            "user": "Your product is amazing!",
            "assistant": "Thank you so much for the kind words! 🎉 It truly makes our day to hear that you're enjoying the product. Is there anything else I can help you with, or any features you'd love to see in the future?"
        },
        # Example 5: Complaint
        {
            "user": "This is the worst service ever",
            "assistant": "I'm really sorry to hear about your experience, and I understand your frustration. Your feedback matters to us. Could you share more details about what happened? I want to personally make sure we address this and make things right for you."
        }
    ]
    
    training_data = []
    for ex in examples:
        training_data.append(create_training_example(
            system=system_prompt,
            user=ex["user"],
            assistant=ex["assistant"]
        ))
    
    return training_data

def save_jsonl(data: List[dict], filename: str):
    """Save data as JSONL file."""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    print(f"Saved {len(data)} examples to {filename}")

def validate_format(filename: str) -> bool:
    """Validate JSONL format for fine-tuning."""
    errors = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                
                # Check required fields
                if "messages" not in data:
                    errors.append(f"Line {i}: Missing 'messages' field")
                    continue
                
                # Check messages format
                for msg in data["messages"]:
                    if "role" not in msg or "content" not in msg:
                        errors.append(f"Line {i}: Invalid message format")
                
                # Check roles
                roles = [m["role"] for m in data["messages"]]
                if "assistant" not in roles:
                    errors.append(f"Line {i}: Missing assistant message")
                    
            except json.JSONDecodeError:
                errors.append(f"Line {i}: Invalid JSON")
    
    if errors:
        print("Validation errors:")
        for e in errors:
            print(f"  - {e}")
        return False
    
    print("✓ Validation passed!")
    return True

# Generate sample data
if __name__ == "__main__":
    # Create training data
    training_data = prepare_customer_support_data()
    
    # We need at least 10 examples for fine-tuning
    # Let's duplicate and modify for demonstration
    expanded_data = training_data * 3  # 15 examples
    
    # Save
    save_jsonl(expanded_data, "training_data.jsonl")
    
    # Validate
    validate_format("training_data.jsonl")
```

### Task 4: Fine-Tune a Model (60 min)

```python
# fine_tune.py
"""
Fine-tune an OpenAI model.
Note: Fine-tuning costs money. Use with real projects only.
"""
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()
client = OpenAI()

def upload_training_file(filename: str) -> str:
    """Upload training file to OpenAI."""
    
    with open(filename, 'rb') as f:
        file = client.files.create(
            file=f,
            purpose="fine-tune"
        )
    
    print(f"Uploaded file: {file.id}")
    return file.id

def create_fine_tune_job(file_id: str, model: str = "gpt-5-mini-2024-07-18") -> str:
    """Create a fine-tuning job."""
    
    job = client.fine_tuning.jobs.create(
        training_file=file_id,
        model=model,
        hyperparameters={
            "n_epochs": 3  # Usually 3-5 is enough
        }
    )
    
    print(f"Created fine-tuning job: {job.id}")
    return job.id

def check_job_status(job_id: str) -> dict:
    """Check the status of a fine-tuning job."""
    
    job = client.fine_tuning.jobs.retrieve(job_id)
    
    return {
        "status": job.status,
        "model": job.fine_tuned_model,
        "created_at": job.created_at,
        "finished_at": job.finished_at,
        "error": job.error
    }

def wait_for_completion(job_id: str, poll_interval: int = 30):
    """Wait for fine-tuning to complete."""
    
    print("Waiting for fine-tuning to complete...")
    
    while True:
        status = check_job_status(job_id)
        print(f"  Status: {status['status']}")
        
        if status["status"] == "succeeded":
            print(f"✓ Fine-tuning complete!")
            print(f"  Model: {status['model']}")
            return status
        
        if status["status"] == "failed":
            print(f"✗ Fine-tuning failed: {status['error']}")
            return status
        
        time.sleep(poll_interval)

def test_fine_tuned_model(model_name: str, test_messages: list):
    """Test the fine-tuned model."""
    
    print(f"\nTesting model: {model_name}")
    
    for test in test_messages:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a friendly customer support agent for TechCo."},
                {"role": "user", "content": test}
            ]
        )
        
        print(f"\nUser: {test}")
        print(f"Bot: {response.choices[0].message.content}")

def list_fine_tuned_models():
    """List all fine-tuned models."""
    
    jobs = client.fine_tuning.jobs.list(limit=10)
    
    print("\nFine-tuning jobs:")
    for job in jobs.data:
        print(f"  {job.id}: {job.status} -> {job.fine_tuned_model or 'N/A'}")

# Main workflow (comment out parts you don't want to run)
if __name__ == "__main__":
    # Step 1: Upload training file
    # file_id = upload_training_file("training_data.jsonl")
    
    # Step 2: Create fine-tuning job
    # job_id = create_fine_tune_job(file_id)
    
    # Step 3: Wait for completion
    # result = wait_for_completion(job_id)
    
    # Step 4: Test the model
    # test_fine_tuned_model(
    #     "ft:gpt-5-mini-2024-07-18:your-org::xxx",
    #     [
    #         "I need help with my account",
    #         "Your app is broken",
    #         "Thanks for the quick response!"
    #     ]
    # )
    
    # List existing jobs
    list_fine_tuned_models()
```

### Task 5: Compare Base vs Fine-Tuned (30 min)

```python
# compare_models.py
"""
Compare base model vs fine-tuned model responses.
"""
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def compare_responses(
    base_model: str,
    fine_tuned_model: str,
    system_prompt: str,
    test_messages: list
):
    """Compare responses from two models."""
    
    print("=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)
    
    for msg in test_messages:
        print(f"\n📝 User: {msg}")
        print("-" * 40)
        
        # Base model
        base_response = client.chat.completions.create(
            model=base_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg}
            ]
        )
        print(f"🔵 Base ({base_model}):")
        print(f"   {base_response.choices[0].message.content[:200]}...")
        
        # Fine-tuned model
        ft_response = client.chat.completions.create(
            model=fine_tuned_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg}
            ]
        )
        print(f"🟢 Fine-tuned ({fine_tuned_model.split(':')[1]}):")
        print(f"   {ft_response.choices[0].message.content[:200]}...")

# Example usage (uncomment with your model)
if __name__ == "__main__":
    # compare_responses(
    #     base_model="gpt-5-mini",
    #     fine_tuned_model="ft:gpt-5-mini-2024-07-18:your-org::xxx",
    #     system_prompt="You are a customer support agent for TechCo.",
    #     test_messages=[
    #         "My order is late",
    #         "I hate this product",
    #         "Can I get a discount?"
    #     ]
    # )
    
    print("To run comparison, uncomment the code with your fine-tuned model name")
```

### Task 6: Deployment Script (45 min)

```python
# deploy.py
"""
Simple deployment script for AI applications.
"""
import subprocess
import sys
import os

def run_command(cmd: str, description: str = ""):
    """Run a shell command."""
    if description:
        print(f"\n→ {description}")
    
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"  ✗ Error: {result.stderr}")
        return False
    
    if result.stdout.strip():
        print(f"  {result.stdout[:200]}")
    
    return True

def build_docker_image(tag: str = "ai-api:latest"):
    """Build Docker image."""
    return run_command(
        f"docker build -t {tag} .",
        "Building Docker image"
    )

def run_docker_local(tag: str = "ai-api:latest", port: int = 8000):
    """Run Docker container locally."""
    return run_command(
        f"docker run -d -p {port}:8000 --env-file .env {tag}",
        f"Running container on port {port}"
    )

def push_to_registry(tag: str, registry: str):
    """Push image to container registry."""
    full_tag = f"{registry}/{tag}"
    
    run_command(f"docker tag {tag} {full_tag}", "Tagging image")
    return run_command(f"docker push {full_tag}", "Pushing to registry")

def deploy_checklist():
    """Print deployment checklist."""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║               AI APPLICATION DEPLOYMENT CHECKLIST         ║
╠══════════════════════════════════════════════════════════╣
║                                                           ║
║  PRE-DEPLOYMENT:                                          ║
║  □ Environment variables configured                       ║
║  □ API keys secured (not in code)                         ║
║  □ Rate limiting configured                               ║
║  □ Logging enabled                                        ║
║  □ Health check endpoint working                          ║
║                                                           ║
║  SECURITY:                                                ║
║  □ Input validation implemented                           ║
║  □ Content moderation active                              ║
║  □ CORS configured correctly                              ║
║  □ Authentication required (if needed)                    ║
║                                                           ║
║  MONITORING:                                              ║
║  □ Error tracking set up                                  ║
║  □ Cost monitoring enabled                                ║
║  □ Performance metrics configured                         ║
║                                                           ║
║  TESTING:                                                 ║
║  □ Unit tests pass                                        ║
║  □ Integration tests pass                                 ║
║  □ Load tested                                            ║
║                                                           ║
╚══════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    deploy_checklist()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "build":
            build_docker_image()
        elif action == "run":
            run_docker_local()
        elif action == "push":
            if len(sys.argv) > 2:
                push_to_registry("ai-api:latest", sys.argv[2])
            else:
                print("Usage: python deploy.py push <registry>")
        else:
            print(f"Unknown action: {action}")
            print("Available: build, run, push")
```

### Task 7: Build a Chat Bot Integration (45 min)

```python
# chatbot_framework.py
"""
Framework for building AI chat bots that integrate with 
Slack, Teams, or other platforms.

This is a platform-agnostic core - you'd add platform adapters.
"""
from dataclasses import dataclass
from typing import Callable, Optional, Dict, Any
from abc import ABC, abstractmethod
import json
import re

# ============ Core Bot Framework ============

@dataclass
class Message:
    """Platform-agnostic message."""
    user_id: str
    channel_id: str
    text: str
    platform: str  # "slack", "teams", "discord"
    raw: Dict[str, Any] = None  # Platform-specific data

@dataclass
class Response:
    """Bot response."""
    text: str
    attachments: list = None
    ephemeral: bool = False  # Only visible to sender

class CommandHandler:
    """Handler for slash commands."""
    
    def __init__(self, name: str, handler: Callable, description: str = ""):
        self.name = name
        self.handler = handler
        self.description = description

class AIBot:
    """AI-powered chat bot framework."""
    
    def __init__(self, ai_service: Callable):
        self.ai_service = ai_service
        self.commands: Dict[str, CommandHandler] = {}
        self.middleware: list = []
        self.conversation_history: Dict[str, list] = {}
    
    def command(self, name: str, description: str = ""):
        """Decorator to register a command."""
        def decorator(func):
            self.commands[name] = CommandHandler(name, func, description)
            return func
        return decorator
    
    def add_middleware(self, func: Callable):
        """Add middleware to process messages."""
        self.middleware.append(func)
    
    async def process_message(self, message: Message) -> Response:
        """Process an incoming message."""
        # Run middleware
        for mw in self.middleware:
            message = mw(message)
            if message is None:  # Middleware blocked
                return None
        
        # Check for commands
        if message.text.startswith("/"):
            return await self._handle_command(message)
        
        # Regular conversation
        return await self._handle_conversation(message)
    
    async def _handle_command(self, message: Message) -> Response:
        """Handle slash commands."""
        parts = message.text.split(" ", 1)
        cmd_name = parts[0][1:]  # Remove /
        args = parts[1] if len(parts) > 1 else ""
        
        handler = self.commands.get(cmd_name)
        if not handler:
            return Response(
                text=f"Unknown command: /{cmd_name}",
                ephemeral=True
            )
        
        return await handler.handler(message, args)
    
    async def _handle_conversation(self, message: Message) -> Response:
        """Handle regular conversation with AI."""
        # Get or create conversation history
        history = self.conversation_history.get(message.channel_id, [])
        
        # Add user message
        history.append({"role": "user", "content": message.text})
        
        # Keep last 10 messages
        history = history[-10:]
        
        # Call AI service
        response_text = await self.ai_service(history)
        
        # Add assistant response
        history.append({"role": "assistant", "content": response_text})
        self.conversation_history[message.channel_id] = history
        
        return Response(text=response_text)
    
    def clear_history(self, channel_id: str):
        """Clear conversation history for a channel."""
        self.conversation_history.pop(channel_id, None)

# ============ Platform Adapters (Stubs) ============

class PlatformAdapter(ABC):
    """Base class for platform adapters."""
    
    @abstractmethod
    def parse_message(self, raw: dict) -> Message:
        pass
    
    @abstractmethod
    def format_response(self, response: Response) -> dict:
        pass

class SlackAdapter(PlatformAdapter):
    """Slack-specific adapter."""
    
    def parse_message(self, raw: dict) -> Message:
        return Message(
            user_id=raw.get("user", ""),
            channel_id=raw.get("channel", ""),
            text=raw.get("text", ""),
            platform="slack",
            raw=raw
        )
    
    def format_response(self, response: Response) -> dict:
        result = {"text": response.text}
        if response.ephemeral:
            result["response_type"] = "ephemeral"
        if response.attachments:
            result["attachments"] = response.attachments
        return result

class TeamsAdapter(PlatformAdapter):
    """Microsoft Teams adapter."""
    
    def parse_message(self, raw: dict) -> Message:
        return Message(
            user_id=raw.get("from", {}).get("id", ""),
            channel_id=raw.get("conversation", {}).get("id", ""),
            text=raw.get("text", ""),
            platform="teams",
            raw=raw
        )
    
    def format_response(self, response: Response) -> dict:
        # Teams uses Adaptive Cards for rich formatting
        return {
            "type": "message",
            "text": response.text
        }

# ============ Usage Example ============

async def mock_ai_service(messages: list) -> str:
    """Mock AI service for testing."""
    last_message = messages[-1]["content"]
    return f"AI response to: {last_message[:50]}..."

# Create bot
bot = AIBot(ai_service=mock_ai_service)

# Register commands
@bot.command("help", "Show available commands")
async def help_command(message: Message, args: str) -> Response:
    commands_list = "\n".join([
        f"/{cmd.name} - {cmd.description}"
        for cmd in bot.commands.values()
    ])
    return Response(text=f"Available commands:\n{commands_list}")

@bot.command("clear", "Clear conversation history")
async def clear_command(message: Message, args: str) -> Response:
    bot.clear_history(message.channel_id)
    return Response(text="Conversation history cleared!", ephemeral=True)

@bot.command("ask", "Ask the AI a question")
async def ask_command(message: Message, args: str) -> Response:
    if not args:
        return Response(text="Please provide a question: /ask <question>", ephemeral=True)
    
    history = [{"role": "user", "content": args}]
    response = await mock_ai_service(history)
    return Response(text=response)

# Middleware example
def logging_middleware(message: Message) -> Message:
    print(f"[{message.platform}] {message.user_id}: {message.text}")
    return message

bot.add_middleware(logging_middleware)

# Test
if __name__ == "__main__":
    import asyncio
    
    async def test_bot():
        print("=== Testing Bot Framework ===\n")
        
        # Simulate messages
        test_messages = [
            Message("user1", "channel1", "Hello!", "slack"),
            Message("user1", "channel1", "What is AI?", "slack"),
            Message("user1", "channel1", "/help", "slack"),
            Message("user1", "channel1", "/ask What is Python?", "slack"),
            Message("user1", "channel1", "/clear", "slack"),
        ]
        
        for msg in test_messages:
            print(f"\n> {msg.text}")
            response = await bot.process_message(msg)
            if response:
                print(f"< {response.text}")
    
    asyncio.run(test_bot())
```

---

## Knowledge Checklist

- [ ] I can containerize an AI application with Docker
- [ ] I understand deployment options and trade-offs
- [ ] I know when fine-tuning is appropriate
- [ ] I can prepare fine-tuning datasets
- [ ] I understand the fine-tuning process
- [ ] I can deploy and test AI applications
- [ ] I understand chat bot integration patterns (Slack/Teams)
- [ ] I know about API Gateway options and patterns

---

## Deliverables

1. `main.py` — FastAPI AI application
2. `Dockerfile` — Container configuration
3. `docker-compose.yml` — Multi-container setup
4. `prepare_finetuning_data.py` — Data preparation
5. `fine_tune.py` — Fine-tuning workflow
6. `deploy.py` — Deployment helper script
7. `chatbot_framework.py` — Chat bot integration

---

## What's Next?

Next week: **Capstone Project & Interview Prep** — put it all together and prepare for your AI career!

---

## Resources

- [Docker Getting Started](https://docs.docker.com/get-started/)
- [OpenAI Fine-Tuning Guide](https://platform.openai.com/docs/guides/fine-tuning)
- [Slack Bolt Python SDK](https://slack.dev/bolt-python/concepts)
- [Microsoft Bot Framework](https://docs.microsoft.com/en-us/azure/bot-service/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
