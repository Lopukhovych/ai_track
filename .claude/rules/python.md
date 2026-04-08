---
paths:
  - "**/*.py"
  - "scripts/**/*"
---

# Python Rules

## Tooling
- Use `uv run <cmd>` for all Python execution — never call `python` or `pip` directly
- Add dependencies with `uv add <pkg>`, not `pip install`
- Import order: stdlib → third-party → local (ruff enforces this automatically)

## Style
- Max line length: 100 characters (ruff default for this project)
- Use f-strings over `.format()` or `%`
- Prefer `pathlib.Path` over `os.path` for file operations
- Use `|` union syntax for type hints: `str | None`, not `Optional[str]`

## Error handling
- Never use bare `except:` — always catch a specific exception type
- Don't swallow exceptions silently — log or re-raise
- Use `contextlib.suppress(ExceptionType)` for intentional suppression

## APIs and I/O
- All OpenAI client calls must check `OPENAI_API_KEY` is set before creating `OpenAI()`
- Load env vars with `load_dotenv()` before any API instantiation
- Use `client.chat.completions.create(...)` — not the deprecated `client.ChatCompletion.create`

## Testing
- Test file naming: `tests/test_<module>.py`
- Use `pytest` fixtures over `setUp`/`tearDown`
- Mock external API calls — never hit real endpoints in tests
