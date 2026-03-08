"""
Unified model configuration for OpenAI and Ollama.

Set AI_PROVIDER=ollama to use local models instead of OpenAI API.

Usage:
    from scripts.model_config import get_client, CHAT_MODEL, EMBED_MODEL

    client = get_client()
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": "Hello!"}]
    )
"""

import os
from openai import OpenAI

PROVIDER = os.getenv("AI_PROVIDER", "openai")  # "openai" or "ollama"

if PROVIDER == "ollama":
    CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.1:8b")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
    CODE_MODEL = os.getenv("CODE_MODEL", "qwen2.5-coder:7b")
    VISION_MODEL = os.getenv("VISION_MODEL", "llama3.2-vision:11b")
    REASON_MODEL = os.getenv("REASON_MODEL", "deepseek-r1:8b")
    STRUCTURED_MODEL = os.getenv("STRUCTURED_MODEL", "qwen2.5:7b")
    SAFETY_MODEL = os.getenv("SAFETY_MODEL", "granite3-guardian:2b")
else:
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5-mini")
    EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    CODE_MODEL = os.getenv("CODE_MODEL", "gpt-5-mini")
    VISION_MODEL = os.getenv("VISION_MODEL", "gpt-5")
    REASON_MODEL = os.getenv("REASON_MODEL", "gpt-5-mini")
    STRUCTURED_MODEL = os.getenv("STRUCTURED_MODEL", "gpt-5-mini")
    SAFETY_MODEL = os.getenv("SAFETY_MODEL", "gpt-5-mini")


def get_client() -> OpenAI:
    """Return an OpenAI-compatible client for the configured provider."""
    if PROVIDER == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434") + "/v1"
        return OpenAI(base_url=base_url, api_key="ollama")
    return OpenAI()


def get_embeddings_client() -> OpenAI:
    """Return client for embedding requests (same as get_client)."""
    return get_client()
