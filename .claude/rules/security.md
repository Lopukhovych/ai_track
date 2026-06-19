# Security Rules

## Secrets and credentials
- Never hardcode API keys, tokens, or passwords in source files
- All secrets must come from environment variables via `os.environ` or `python-dotenv`
- `.env` files are gitignored — never commit them
- Use `.env.example` as the template — it contains only key names, never values

## Input validation
- Validate all user inputs at system boundaries (API endpoints, CLI args)
- Use Pydantic models for structured input validation
- Sanitize any user content before including it in prompts (prompt injection risk)
- Limit prompt injection surface: never directly concatenate user input into system prompts

## Prompt injection defense
- Separate system instructions from user content with clear delimiters
- Treat all LLM output as untrusted before acting on it programmatically
- Don't execute code returned by an LLM without review in development

## Dependencies
- Pin dependency versions in `pyproject.toml` for reproducibility
- Run `uv audit` (or `pip-audit`) before any production deployment
- Review changelogs when updating packages that handle auth or I/O

## File operations
- Validate file paths against a whitelist before reading/writing
- Use `Path.resolve()` and check the result is within expected directories
- Never `eval()` or `exec()` dynamically constructed strings
