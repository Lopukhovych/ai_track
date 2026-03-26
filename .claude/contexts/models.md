# Model Reference Context

Imported by CLAUDE.md. Quick reference for model choices used throughout the curriculum.

## OpenAI Models (default provider)

| Model | Use case | Context | Notes |
|-------|----------|---------|-------|
| `gpt-4o-mini` | **Default for all labs** | 128k | Best cost/quality for learning |
| `gpt-4o` | Complex reasoning exercises | 128k | Use when mini struggles |
| `text-embedding-3-small` | Embeddings (weeks 3-6) | — | 1536 dims, fast |
| `text-embedding-3-large` | High-quality embeddings | — | 3072 dims, slower |

## Anthropic Models (optional, weeks 9-16)

| Model | Use case | Notes |
|-------|----------|-------|
| `claude-sonnet-4-6` | Agent tasks, code review | Strong reasoning, good tools |
| `claude-haiku-4-5` | Subagents, simple tasks | Fast and cheap |
| `claude-opus-4-6` | Architecture decisions | Expensive, use sparingly |

## Local Models via Ollama

Set `AI_PROVIDER=ollama` in `.env`. The `scripts/model_config.py` client handles routing.

| Task | Ollama model |
|------|-------------|
| Chat | `llama3.2` or `qwen2.5` |
| Embeddings | `nomic-embed-text` |
| Code | `codellama` or `qwen2.5-coder` |

## Model Config Helper

```python
# scripts/model_config.py — use this throughout the course
from scripts.model_config import get_client, get_model

client = get_client()          # Returns OpenAI or Ollama client
model = get_model("chat")      # Returns correct model name for provider
```
