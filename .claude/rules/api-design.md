---
paths:
  - "projects/**/*.py"
  - "src/**/*.py"
---

# API Design Rules

## Endpoint conventions
- Use RESTful resource naming: `/users/{id}/messages`, not `/getUserMessages`
- HTTP verbs: GET=read, POST=create, PUT=replace, PATCH=update, DELETE=remove
- Return 200 for success, 201 for created, 204 for deleted (no body)
- Never return 200 with `{"success": false}` — use the right status code

## Request/response format
- All endpoints validate input with a Pydantic model
- All error responses use this format:
  ```json
  {"error": "Human-readable message", "code": "MACHINE_READABLE_CODE"}
  ```
- Paginated responses include: `{"items": [...], "total": N, "page": N, "per_page": N}`

## LLM API wrappers
- Always expose `model`, `temperature`, and `max_tokens` as optional parameters with sensible defaults
- Stream long responses — don't make callers wait for full completion
- Include request/response logging for debugging (redact sensitive content)
- Implement retry with exponential backoff for rate limit errors (429)

## Documentation
- Every public function needs a docstring with: what it does, parameters, return type, example
- FastAPI endpoints use Pydantic models — FastAPI generates OpenAPI docs automatically
