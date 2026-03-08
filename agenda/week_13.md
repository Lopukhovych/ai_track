# Week 13: Production Hardening

**Month:** 4 (Production & Career) | **Duration:** 6-8 hours

---

## Overview

**Connection to previous weeks:** You have MCP for external tools and observability for monitoring. Now ensure the system doesn't fail under pressure — this is what separates demo projects from production-ready applications.

Your AI application works, but is it production-ready? This week you'll learn **reliability patterns** that make AI applications robust: rate limiting, caching, retries, and failover.

---

## Learning Objectives

By the end of this week, you will:
- Implement rate limiting for API calls
- Build caching layers for AI responses
- Handle retries with exponential backoff
- Set up failover between providers
- Build a resilient AI client

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| Primary provider | `gpt-5-mini` | `llama3.1:8b` |
| Failover / backup provider | OpenAI → Azure OpenAI | OpenAI → Ollama (local fallback) |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b
```

```python
from scripts.model_config import get_client, CHAT_MODEL
# Ollama as local failover: if OpenAI is down, switch AI_PROVIDER=ollama
# This week's caching and retry patterns apply equally to both providers
```

> A major benefit of Ollama: use it as a **local failover** when cloud APIs have outages or you hit rate limits.

---

## Theory (2 hours)

### 1. Why Production Hardening? (30 min)

**Production challenges:**
- API rate limits
- Network failures
- Cost control
- Latency requirements
- Provider outages

**The goal:** Your app keeps working even when things go wrong.

### 2. Rate Limiting (30 min)

**Problem:** APIs have limits (e.g., 500 RPM for OpenAI)

**Solutions:**
- **Token bucket** — Smooth rate limiting
- **Sliding window** — Track requests over time
- **Queue-based** — Buffer requests

```
Request → [Rate Limiter] → API
           ↓ (if over limit)
         Wait or Queue
```

### 3. Caching Strategies (30 min)

**Why cache?**
- Reduce API costs (same question = same answer)
- Lower latency
- Handle rate limits gracefully

**Cache levels:**
| Level | Use Case |
|-------|----------|
| Exact match | Identical prompts |
| Semantic | Similar questions |
| Result | Computed outputs (RAG results) |

### 4. Reliability Patterns (30 min)

**Retries with backoff:**
```
Attempt 1: Fail
Wait 1s
Attempt 2: Fail
Wait 2s
Attempt 3: Fail
Wait 4s
Attempt 4: Success!
```

**Circuit breaker:**
```
Closed (normal) → Too many failures → Open (reject all)
                                          ↓ (after timeout)
                                    Half-Open (test)
                                          ↓ (success)
                                       Closed
```

### 5. Secrets Management (30 min)

**Never hardcode credentials!** API keys, connection strings, and secrets must be managed securely.

**Levels of secret management:**

| Level | When to Use | Example |
|-------|-------------|---------|
| **Environment variables** | Local development | `export OPENAI_API_KEY=sk-...` |
| **.env files** | Local + shared config | `.env` file (in .gitignore!) |
| **Azure Key Vault / AWS Secrets Manager** | Production | Managed secret storage |
| **Managed Identity** | Azure resources | No secrets needed |

**Pattern: Environment-based configuration:**

```python
# config.py
import os
from dataclasses import dataclass

@dataclass
class Config:
    openai_api_key: str
    azure_connection_string: str
    environment: str
    
    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            openai_api_key=os.environ["OPENAI_API_KEY"],
            azure_connection_string=os.environ.get("AZURE_CONN_STR", ""),
            environment=os.environ.get("ENVIRONMENT", "development")
        )

# Azure Key Vault integration
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def get_secret_from_keyvault(vault_url: str, secret_name: str) -> str:
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)
    return client.get_secret(secret_name).value
```

**Interview tip:** Know the difference between Managed Identity (no secrets) vs Service Principal (client ID + secret).

### 6. Role-Based Access Control (RBAC) (30 min)

**RBAC principle:** Users get minimum permissions needed for their role.

**AI system RBAC considerations:**
- **Admin** — Full access, can modify prompts/tools
- **Developer** — Test access, view logs
- **User** — Run queries, limited scope
- **Auditor** — Read-only logs, no execution

**RBAC in Azure OpenAI:**

```
User → [RBAC Check] → Azure OpenAI
         ↓
   Cognitive Services OpenAI User (read/use)
   Cognitive Services OpenAI Contributor (modify)
```

**Implementing RBAC in your app:**

```python
from enum import Enum
from typing import Set
from functools import wraps

class Role(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    AUDITOR = "auditor"

class Permission(Enum):
    QUERY = "query"
    VIEW_LOGS = "view_logs"
    MODIFY_PROMPTS = "modify_prompts"
    MANAGE_USERS = "manage_users"
    DELETE_DATA = "delete_data"

ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {Permission.QUERY, Permission.VIEW_LOGS, Permission.MODIFY_PROMPTS, 
                 Permission.MANAGE_USERS, Permission.DELETE_DATA},
    Role.DEVELOPER: {Permission.QUERY, Permission.VIEW_LOGS, Permission.MODIFY_PROMPTS},
    Role.USER: {Permission.QUERY},
    Role.AUDITOR: {Permission.VIEW_LOGS},
}

def require_permission(permission: Permission):
    """Decorator to check user permissions."""
    def decorator(func):
        @wraps(func)
        def wrapper(user_role: Role, *args, **kwargs):
            if permission not in ROLE_PERMISSIONS.get(user_role, set()):
                raise PermissionError(f"Role {user_role.value} lacks {permission.value}")
            return func(user_role, *args, **kwargs)
        return wrapper
    return decorator

@require_permission(Permission.QUERY)
def run_ai_query(user_role: Role, query: str) -> str:
    return f"Processing: {query}"

@require_permission(Permission.MODIFY_PROMPTS)
def update_prompt(user_role: Role, prompt_id: str, new_prompt: str):
    return f"Updated prompt {prompt_id}"
```

---

## Hands-On Practice (4-6 hours)

### Task 1: Rate Limiter (60 min)

```python
# rate_limiter.py
import time
from collections import deque
from threading import Lock
from typing import Optional

class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, requests_per_minute: int):
        self.rpm = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = time.time()
        self.lock = Lock()
    
    def _refill(self):
        """Refill tokens based on time passed."""
        now = time.time()
        time_passed = now - self.last_update
        
        # Add tokens based on time (RPM / 60 per second)
        new_tokens = time_passed * (self.rpm / 60)
        self.tokens = min(self.rpm, self.tokens + new_tokens)
        self.last_update = now
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Try to acquire a token."""
        deadline = time.time() + timeout if timeout else None
        
        while True:
            with self.lock:
                self._refill()
                
                if self.tokens >= 1:
                    self.tokens -= 1
                    return True
            
            if deadline and time.time() >= deadline:
                return False
            
            # Wait a bit before retrying
            time.sleep(0.1)
    
    def wait(self):
        """Block until a token is available."""
        while not self.acquire(timeout=0.1):
            pass

class SlidingWindowRateLimiter:
    """Sliding window rate limiter."""
    
    def __init__(self, requests_per_minute: int):
        self.rpm = requests_per_minute
        self.window: deque = deque()
        self.lock = Lock()
    
    def _clean_old_requests(self):
        """Remove requests older than 1 minute."""
        cutoff = time.time() - 60
        while self.window and self.window[0] < cutoff:
            self.window.popleft()
    
    def acquire(self) -> bool:
        """Try to make a request."""
        with self.lock:
            self._clean_old_requests()
            
            if len(self.window) < self.rpm:
                self.window.append(time.time())
                return True
            
            return False
    
    def wait_time(self) -> float:
        """Time until next request is allowed."""
        with self.lock:
            self._clean_old_requests()
            
            if len(self.window) < self.rpm:
                return 0
            
            # Wait until oldest request expires
            return max(0, 60 - (time.time() - self.window[0]))

# Decorator
def rate_limited(limiter: RateLimiter):
    """Decorator to rate limit a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            limiter.wait()
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Test
if __name__ == "__main__":
    limiter = RateLimiter(requests_per_minute=10)
    
    print("Making 15 requests with 10 RPM limit...")
    for i in range(15):
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start
        print(f"Request {i+1}: waited {elapsed:.2f}s")
```

### Task 2: Response Caching (60 min)

```python
# caching.py
import hashlib
import json
import time
from typing import Optional, Any
from dataclasses import dataclass
from functools import wraps

@dataclass
class CacheEntry:
    value: Any
    created_at: float
    ttl: float
    
    @property
    def is_expired(self) -> bool:
        return time.time() > self.created_at + self.ttl

class SimpleCache:
    """Simple in-memory cache."""
    
    def __init__(self, default_ttl: float = 3600):
        self.cache: dict = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, *args, **kwargs) -> str:
        """Create a cache key from arguments."""
        data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        entry = self.cache.get(key)
        
        if entry is None:
            self.misses += 1
            return None
        
        if entry.is_expired:
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set a value in cache."""
        self.cache[key] = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl=ttl or self.default_ttl
        )
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
    
    @property
    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hits / total * 100, 1) if total > 0 else 0,
            "size": len(self.cache)
        }

def cached(cache: SimpleCache, ttl: Optional[float] = None):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = cache._make_key(func.__name__, *args, **kwargs)
            
            # Check cache
            result = cache.get(key)
            if result is not None:
                return result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

# Semantic cache (for similar questions)
class SemanticCache:
    """Cache that matches similar prompts."""
    
    def __init__(self, similarity_threshold: float = 0.95):
        self.entries: list = []
        self.threshold = similarity_threshold
    
    def _get_embedding(self, text: str) -> list:
        """Get embedding for text."""
        from openai import OpenAI
        client = OpenAI()
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def _similarity(self, a: list, b: list) -> float:
        """Calculate cosine similarity."""
        import numpy as np
        a, b = np.array(a), np.array(b)
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def get(self, prompt: str) -> Optional[str]:
        """Find a cached response for similar prompt."""
        if not self.entries:
            return None
        
        query_emb = self._get_embedding(prompt)
        
        best_match = None
        best_score = 0
        
        for entry in self.entries:
            score = self._similarity(query_emb, entry["embedding"])
            if score > best_score and score >= self.threshold:
                best_score = score
                best_match = entry
        
        if best_match:
            print(f"  Cache hit! Similarity: {best_score:.3f}")
            return best_match["response"]
        
        return None
    
    def set(self, prompt: str, response: str):
        """Cache a response."""
        embedding = self._get_embedding(prompt)
        self.entries.append({
            "prompt": prompt,
            "response": response,
            "embedding": embedding
        })

# Test
if __name__ == "__main__":
    cache = SimpleCache(default_ttl=60)
    
    @cached(cache)
    def expensive_operation(x):
        print(f"  Computing {x}...")
        time.sleep(0.1)
        return x * 2
    
    print("First calls (cache miss):")
    print(f"  Result: {expensive_operation(5)}")
    print(f"  Result: {expensive_operation(10)}")
    
    print("\nSecond calls (cache hit):")
    print(f"  Result: {expensive_operation(5)}")
    print(f"  Result: {expensive_operation(10)}")
    
    print(f"\nCache stats: {cache.stats}")
```

### Task 3: Retry Logic (45 min)

```python
# retries.py
import time
import random
from typing import TypeVar, Callable, Optional
from functools import wraps

T = TypeVar('T')

class RetryError(Exception):
    """Raised when all retries are exhausted."""
    def __init__(self, message: str, last_error: Exception):
        super().__init__(message)
        self.last_error = last_error

def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
) -> float:
    """Calculate delay with exponential backoff."""
    delay = min(base_delay * (2 ** attempt), max_delay)
    
    if jitter:
        delay = delay * (0.5 + random.random())
    
    return delay

def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
):
    """Decorator for retrying functions."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_error = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_error = e
                    
                    if attempt == max_attempts - 1:
                        raise RetryError(
                            f"Failed after {max_attempts} attempts",
                            last_error
                        )
                    
                    delay = exponential_backoff(attempt, base_delay, max_delay)
                    
                    if on_retry:
                        on_retry(attempt + 1, delay, e)
                    else:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
                    
                    time.sleep(delay)
            
            raise RetryError(f"Failed after {max_attempts} attempts", last_error)
        return wrapper
    return decorator

# Specific retry for OpenAI
from openai import RateLimitError, APIError, APITimeoutError

def retry_openai(max_attempts: int = 3):
    """Retry decorator specifically for OpenAI calls."""
    return retry(
        max_attempts=max_attempts,
        base_delay=1.0,
        max_delay=30.0,
        exceptions=(RateLimitError, APIError, APITimeoutError)
    )

# Test
if __name__ == "__main__":
    call_count = 0
    
    @retry(max_attempts=5, base_delay=0.5)
    def flaky_function():
        global call_count
        call_count += 1
        
        if call_count < 3:
            raise ConnectionError(f"Failed on attempt {call_count}")
        
        return "Success!"
    
    try:
        result = flaky_function()
        print(f"Result: {result}")
        print(f"Total attempts: {call_count}")
    except RetryError as e:
        print(f"All retries failed: {e.last_error}")
```

### Task 4: Circuit Breaker (45 min)

```python
# circuit_breaker.py
import time
from enum import Enum
from threading import Lock
from typing import Callable, TypeVar
from functools import wraps

T = TypeVar('T')

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject all
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_limit: int = 1
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_limit = half_open_limit
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.half_open_calls = 0
        self.lock = Lock()
    
    def can_proceed(self) -> bool:
        """Check if a call can proceed."""
        with self.lock:
            if self.state == CircuitState.CLOSED:
                return True
            
            if self.state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if time.time() - self.last_failure_time >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    return True
                return False
            
            # HALF_OPEN
            if self.half_open_calls < self.half_open_limit:
                self.half_open_calls += 1
                return True
            return False
    
    def record_success(self):
        """Record a successful call."""
        with self.lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print("Circuit CLOSED (recovered)")
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed call."""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                print("Circuit OPEN (failed during recovery)")
            elif self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"Circuit OPEN (threshold reached: {self.failure_count})")
    
    @property
    def status(self) -> dict:
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time
        }

class CircuitOpenError(Exception):
    """Raised when circuit is open."""
    pass

def circuit_breaker(breaker: CircuitBreaker):
    """Decorator to apply circuit breaker."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            if not breaker.can_proceed():
                raise CircuitOpenError("Circuit is open, call rejected")
            
            try:
                result = func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise
        return wrapper
    return decorator

# Test
if __name__ == "__main__":
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=5)
    call_count = 0
    
    @circuit_breaker(breaker)
    def unreliable_service():
        global call_count
        call_count += 1
        
        # Fail for first 5 calls
        if call_count <= 5:
            raise ConnectionError(f"Service unavailable (call {call_count})")
        
        return "Success!"
    
    print("Testing circuit breaker...")
    
    for i in range(10):
        try:
            result = unreliable_service()
            print(f"  Call {i+1}: {result}")
        except CircuitOpenError:
            print(f"  Call {i+1}: Rejected (circuit open)")
        except ConnectionError as e:
            print(f"  Call {i+1}: Failed - {e}")
        
        print(f"    State: {breaker.status['state']}")
        time.sleep(1)
```

### Task 5: Provider Failover (45 min)

```python
# failover.py
"""
Failover between multiple AI providers.
"""
from typing import List, Optional
from dataclasses import dataclass
import time

@dataclass
class Provider:
    name: str
    client: any
    model: str
    priority: int = 0
    is_healthy: bool = True
    last_failure: float = 0

class MultiProviderClient:
    """Client that fails over between providers."""
    
    def __init__(self):
        self.providers: List[Provider] = []
        self.unhealthy_timeout = 60  # Seconds before retrying unhealthy provider
    
    def add_provider(self, name: str, client, model: str, priority: int = 0):
        """Add a provider."""
        self.providers.append(Provider(
            name=name,
            client=client,
            model=model,
            priority=priority
        ))
        # Sort by priority
        self.providers.sort(key=lambda p: p.priority, reverse=True)
    
    def _get_healthy_providers(self) -> List[Provider]:
        """Get list of healthy providers."""
        now = time.time()
        healthy = []
        
        for p in self.providers:
            if p.is_healthy:
                healthy.append(p)
            elif now - p.last_failure >= self.unhealthy_timeout:
                # Give unhealthy provider another chance
                p.is_healthy = True
                healthy.append(p)
        
        return healthy
    
    def chat(self, message: str) -> dict:
        """Make a chat request with failover."""
        
        healthy = self._get_healthy_providers()
        
        if not healthy:
            raise Exception("No healthy providers available")
        
        for provider in healthy:
            try:
                print(f"  Trying {provider.name}...")
                
                response = provider.client.chat.completions.create(
                    model=provider.model,
                    messages=[{"role": "user", "content": message}]
                )
                
                return {
                    "provider": provider.name,
                    "content": response.choices[0].message.content,
                    "model": provider.model
                }
            
            except Exception as e:
                print(f"  {provider.name} failed: {e}")
                provider.is_healthy = False
                provider.last_failure = time.time()
                continue
        
        raise Exception("All providers failed")

# Test with mock providers
class MockClient:
    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
    
    class Completions:
        def __init__(self, parent):
            self.parent = parent
        
        def create(self, **kwargs):
            if self.parent.should_fail:
                raise ConnectionError(f"{self.parent.name} is down")
            
            class Choice:
                class Message:
                    content = f"Response from {self.parent.name}"
                message = Message()
            
            class Response:
                choices = [Choice()]
            
            return Response()
    
    @property
    def chat(self):
        return MockClient.Completions(self)

if __name__ == "__main__":
    client = MultiProviderClient()
    
    # Add providers with different priorities
    client.add_provider("OpenAI", MockClient("OpenAI", should_fail=True), "gpt-4", priority=3)
    client.add_provider("Anthropic", MockClient("Anthropic"), "claude-3", priority=2)
    client.add_provider("Local", MockClient("Local"), "llama-3", priority=1)
    
    print("Testing failover...")
    result = client.chat("Hello!")
    print(f"Response from {result['provider']}: {result['content']}")
```

### Task 6: Resilient AI Client (60 min)

```python
# resilient_client.py
"""
Production-ready AI client with all reliability patterns.
"""
from openai import OpenAI
from dotenv import load_dotenv
from rate_limiter import RateLimiter
from caching import SimpleCache, cached
from retries import retry
from circuit_breaker import CircuitBreaker, circuit_breaker, CircuitOpenError
import time

load_dotenv()

class ResilientAIClient:
    """AI client with rate limiting, caching, retries, and circuit breaker."""
    
    def __init__(
        self,
        requests_per_minute: int = 50,
        cache_ttl: int = 3600,
        max_retries: int = 3,
        circuit_threshold: int = 5
    ):
        self.client = OpenAI()
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.cache = SimpleCache(default_ttl=cache_ttl)
        self.breaker = CircuitBreaker(failure_threshold=circuit_threshold)
        self.max_retries = max_retries
        
        # Metrics
        self.total_calls = 0
        self.cache_hits = 0
        self.retries = 0
        self.failures = 0
    
    def chat(self, message: str, use_cache: bool = True) -> str:
        """Make a resilient chat request."""
        
        self.total_calls += 1
        
        # Check cache
        if use_cache:
            cache_key = self.cache._make_key("chat", message)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                self.cache_hits += 1
                return cached_response
        
        # Rate limit
        self.rate_limiter.wait()
        
        # Make call with circuit breaker and retries
        try:
            response = self._call_with_resilience(message)
            
            # Cache response
            if use_cache:
                self.cache.set(cache_key, response)
            
            return response
        
        except CircuitOpenError:
            self.failures += 1
            raise
    
    def _call_with_resilience(self, message: str) -> str:
        """Internal method with circuit breaker and retries."""
        
        last_error = None
        
        for attempt in range(self.max_retries):
            # Check circuit breaker
            if not self.breaker.can_proceed():
                raise CircuitOpenError("Circuit is open")
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": message}]
                )
                
                self.breaker.record_success()
                return response.choices[0].message.content
            
            except Exception as e:
                last_error = e
                self.breaker.record_failure()
                self.retries += 1
                
                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt
                    print(f"Retry {attempt + 1} in {delay}s...")
                    time.sleep(delay)
        
        self.failures += 1
        raise last_error
    
    @property
    def stats(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": f"{self.cache_hits / self.total_calls * 100:.1f}%" if self.total_calls > 0 else "0%",
            "retries": self.retries,
            "failures": self.failures,
            "circuit_state": self.breaker.status["state"]
        }

# Test
if __name__ == "__main__":
    client = ResilientAIClient(
        requests_per_minute=60,
        cache_ttl=300
    )
    
    print("Testing resilient client...")
    
    # Make some calls
    messages = [
        "Hello!",
        "What is AI?",
        "Hello!",  # Should be cached
        "What is AI?",  # Should be cached
        "Tell me about Python"
    ]
    
    for msg in messages:
        start = time.time()
        try:
            response = client.chat(msg)
            elapsed = (time.time() - start) * 1000
            print(f"✓ '{msg[:20]}...' ({elapsed:.0f}ms)")
        except Exception as e:
            print(f"✗ '{msg[:20]}...' - {e}")
    
    print(f"\nStats: {client.stats}")
```

### Task 7: Secrets & RBAC Implementation (45 min)

```python
# secrets_and_rbac.py
import os
from dataclasses import dataclass
from enum import Enum
from typing import Set, Optional
from functools import wraps
from datetime import datetime

# ============ Secrets Management ============

@dataclass
class AppConfig:
    """Application configuration from environment."""
    openai_api_key: str
    database_url: str
    environment: str
    log_level: str
    
    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load config from environment variables."""
        required = ["OPENAI_API_KEY"]
        missing = [var for var in required if var not in os.environ]
        if missing:
            raise ValueError(f"Missing required env vars: {missing}")
        
        return cls(
            openai_api_key=os.environ["OPENAI_API_KEY"],
            database_url=os.environ.get("DATABASE_URL", "sqlite:///local.db"),
            environment=os.environ.get("ENVIRONMENT", "development"),
            log_level=os.environ.get("LOG_LEVEL", "INFO")
        )
    
    def is_production(self) -> bool:
        return self.environment == "production"

class SecretManager:
    """Abstract secret manager with multiple backends."""
    
    def __init__(self, backend: str = "env"):
        self.backend = backend
        self._cache: dict = {}
    
    def get_secret(self, name: str) -> Optional[str]:
        """Get a secret by name."""
        if name in self._cache:
            return self._cache[name]
        
        if self.backend == "env":
            value = os.environ.get(name)
        elif self.backend == "keyvault":
            # In production, use Azure Key Vault
            value = self._get_from_keyvault(name)
        else:
            raise ValueError(f"Unknown backend: {self.backend}")
        
        if value:
            self._cache[name] = value
        return value
    
    def _get_from_keyvault(self, name: str) -> Optional[str]:
        """Get secret from Azure Key Vault (stub)."""
        # In real implementation:
        # from azure.identity import DefaultAzureCredential
        # from azure.keyvault.secrets import SecretClient
        # credential = DefaultAzureCredential()
        # client = SecretClient(vault_url=os.environ["KEYVAULT_URL"], credential=credential)
        # return client.get_secret(name).value
        print(f"  [KeyVault] Getting secret: {name}")
        return os.environ.get(name)  # Fallback for demo

# ============ RBAC Implementation ============

class Role(Enum):
    ADMIN = "admin"
    DEVELOPER = "developer"
    USER = "user"
    AUDITOR = "auditor"

class Permission(Enum):
    QUERY = "query"
    VIEW_LOGS = "view_logs"
    MODIFY_PROMPTS = "modify_prompts"
    MANAGE_USERS = "manage_users"
    DELETE_DATA = "delete_data"
    ACCESS_SENSITIVE = "access_sensitive"

ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: {p for p in Permission},  # All permissions
    Role.DEVELOPER: {
        Permission.QUERY, 
        Permission.VIEW_LOGS, 
        Permission.MODIFY_PROMPTS
    },
    Role.USER: {Permission.QUERY},
    Role.AUDITOR: {Permission.VIEW_LOGS},
}

@dataclass
class User:
    id: str
    email: str
    role: Role
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def has_permission(self, permission: Permission) -> bool:
        return permission in ROLE_PERMISSIONS.get(self.role, set())

class RBACError(Exception):
    """Raised when permission is denied."""
    pass

def require_permission(permission: Permission):
    """Decorator to enforce permission checks."""
    def decorator(func):
        @wraps(func)
        def wrapper(user: User, *args, **kwargs):
            if not user.has_permission(permission):
                raise RBACError(
                    f"Permission denied: {user.email} ({user.role.value}) "
                    f"lacks {permission.value}"
                )
            print(f"  [RBAC] {user.email} authorized for {permission.value}")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

def audit_log(action: str):
    """Decorator to log actions for audit."""
    def decorator(func):
        @wraps(func)
        def wrapper(user: User, *args, **kwargs):
            result = func(user, *args, **kwargs)
            print(f"  [AUDIT] {datetime.now().isoformat()} | {user.email} | {action}")
            return result
        return wrapper
    return decorator

# ============ AI Service with RBAC ============

class SecureAIService:
    """AI service with authentication and authorization."""
    
    def __init__(self, secret_manager: SecretManager):
        self.secrets = secret_manager
        self._api_key = None
    
    def _get_api_key(self) -> str:
        if not self._api_key:
            self._api_key = self.secrets.get_secret("OPENAI_API_KEY")
        return self._api_key
    
    @require_permission(Permission.QUERY)
    @audit_log("ai_query")
    def query(self, user: User, prompt: str) -> str:
        """Run an AI query (requires QUERY permission)."""
        # In real app, use self._get_api_key() to make API call
        return f"Response to: {prompt[:30]}..."
    
    @require_permission(Permission.MODIFY_PROMPTS)
    @audit_log("modify_prompt")
    def update_system_prompt(self, user: User, prompt_id: str, content: str) -> bool:
        """Update a system prompt (requires MODIFY_PROMPTS permission)."""
        print(f"  Updated prompt {prompt_id}")
        return True
    
    @require_permission(Permission.VIEW_LOGS)
    def get_logs(self, user: User, limit: int = 100) -> list:
        """Get audit logs (requires VIEW_LOGS permission)."""
        return [f"Log entry {i}" for i in range(limit)]
    
    @require_permission(Permission.DELETE_DATA)
    @audit_log("delete_data")
    def delete_user_data(self, user: User, target_user_id: str) -> bool:
        """Delete user data (requires DELETE_DATA permission - admin only)."""
        print(f"  Deleted data for user {target_user_id}")
        return True

# ============ Test ============

if __name__ == "__main__":
    # Set up
    os.environ["OPENAI_API_KEY"] = "sk-test-key"
    secrets = SecretManager(backend="env")
    service = SecureAIService(secrets)
    
    # Create test users
    admin = User(id="1", email="admin@company.com", role=Role.ADMIN)
    dev = User(id="2", email="dev@company.com", role=Role.DEVELOPER)
    user = User(id="3", email="user@company.com", role=Role.USER)
    auditor = User(id="4", email="auditor@company.com", role=Role.AUDITOR)
    
    print("=== Admin (all permissions) ===")
    print(service.query(admin, "What is the meaning of life?"))
    service.update_system_prompt(admin, "sys-001", "You are helpful...")
    
    print("\n=== Developer (query + modify) ===")
    print(service.query(dev, "Explain quantum computing"))
    service.update_system_prompt(dev, "sys-002", "New prompt...")
    
    print("\n=== User (query only) ===")
    print(service.query(user, "Hello!"))
    
    print("\n=== User trying to modify (should fail) ===")
    try:
        service.update_system_prompt(user, "sys-003", "Hacked!")
    except RBACError as e:
        print(f"  ✗ {e}")
    
    print("\n=== Auditor (view logs only) ===")
    logs = service.get_logs(auditor, limit=3)
    print(f"  Got {len(logs)} log entries")
    
    print("\n=== Auditor trying to query (should fail) ===")
    try:
        service.query(auditor, "Hello!")
    except RBACError as e:
        print(f"  ✗ {e}")
```

---

## 🎯 Optional Challenges

*Production skills separate demos from real systems. Practice here.*

### Challenge 1: Cost Tracker
Build a real-time cost tracking system:
```python
class CostTracker:
    def __init__(self, budget_limit: float):
        self.total_cost = 0
        self.budget_limit = budget_limit
    
    def track(self, response):
        # Calculate cost from token usage
        # Alert if approaching budget
        # Block if over budget
```

### Challenge 2: Graceful Degradation
Build a system that works (limited) when the API is down:
- Return cached responses for common queries
- Show "AI temporarily unavailable" message
- Queue requests for later processing
- Send notification to admin

### Challenge 3: A/B Testing Framework
Implement A/B testing for prompts:
```python
class PromptABTest:
    def __init__(self, prompt_a, prompt_b, split=0.5):
        pass
    
    def get_prompt(self, user_id):
        # Consistently assign users to A or B
        pass
    
    def record_result(self, user_id, metric):
        # Track which prompt performs better
        pass
```

### Challenge 4: Auto-Scaling Simulation
Simulate load and test your rate limiting:
```python
import asyncio
import random

async def simulate_load(requests_per_second, duration_seconds):
    # Send requests at specified rate
    # Measure: latency, success rate, queue depth
    pass

# Test: What happens at 10/s? 100/s? 1000/s?
```

### Challenge 5: Incident Response Playbook
Create an automated incident response:
1. Detect: Error rate > 10%
2. Alert: Send Slack/email notification
3. Mitigate: Switch to backup provider automatically
4. Log: Record incident details
5. Report: Generate post-incident summary

---

## Knowledge Checklist

- [ ] I can implement rate limiting
- [ ] I can cache AI responses effectively
- [ ] I understand exponential backoff retries
- [ ] I can implement a circuit breaker
- [ ] I can set up provider failover
- [ ] I built a production-ready resilient client
- [ ] I understand secrets management patterns
- [ ] I can implement RBAC for AI services

---

## Deliverables

1. `rate_limiter.py` — Token bucket rate limiting
2. `caching.py` — Response caching with TTL
3. `retries.py` — Exponential backoff retries
4. `circuit_breaker.py` — Circuit breaker pattern
5. `failover.py` — Multi-provider failover
6. `resilient_client.py` — Combined resilient client
7. `secrets_and_rbac.py` — Secrets management + RBAC

---

## What's Next?

Next week: **Deployment & Fine-Tuning** — deploying your AI apps and when/how to fine-tune!

---

## Resources

- [OpenAI Rate Limits](https://platform.openai.com/docs/guides/rate-limits)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Resilience Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/category/resiliency)
