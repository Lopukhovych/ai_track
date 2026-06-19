---
name: review
description: Run a structured code review on recent changes or a specific file. Covers correctness, security, performance, and test coverage.
argument-hint: "[file-or-directory]"
disable-model-invocation: true
allowed-tools: Read, Bash(git *), Grep, Glob
---

Run a structured code review.

**Target:** Use `$ARGUMENTS` if provided, otherwise review recent git changes:
```bash
git diff HEAD -- $ARGUMENTS 2>/dev/null || git diff HEAD
```

If the diff is empty, check staged changes: `git diff --cached`

## Review checklist (for each changed file)

1. **Correctness** — Logic errors, edge cases not handled, off-by-one, None/null derefs
2. **Security** — Hardcoded secrets, injection risks, missing input validation, unsafe file ops
3. **Performance** — N+1 patterns, unnecessary re-computation, missing batching, unbounded loops
4. **Test coverage** — Are changed code paths tested? Are error paths tested?
5. **Style consistency** — Naming, formatting, import order (check against `.claude/rules/python.md`)
6. **Documentation** — New public functions need docstrings; complex logic needs inline comments

## Output format

### Critical (block merge)
- `file.py:42` — **[Security]** Hardcoded API key — replace with `os.environ["KEY"]`

### Warnings (tech debt, fix soon)
- `file.py:17` — **[Performance]** Getting embedding inside loop — batch with `get_embeddings_batch()`

### Suggestions (optional)
- `file.py:88` — Consider extracting to a helper function for reuse

### Summary
Overall: `approve` / `approve with minor changes` / `request changes`
Confidence: `high` / `medium` / `low` (low if diff is too large to review thoroughly)
