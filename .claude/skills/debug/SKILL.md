---
name: debug
description: Systematic debugging for errors, test failures, and unexpected output. Use when encountering any error message, stack trace, or wrong output.
argument-hint: "[error-or-description]"
context: fork
agent: general-purpose
---

Debug the issue: `$ARGUMENTS`

## Systematic debugging process

### Step 1 — Capture the full context
```bash
# Get the complete error with traceback
# Check recent git changes that might have caused this
git diff HEAD --stat
git log --oneline -5
```

### Step 2 — Reproduce it
Identify the minimal reproducer:
- What exact command triggers the error?
- Does it happen every time or intermittently?
- Did it work before? What changed?

### Step 3 — Form hypotheses
List 3 possible causes, ranked by likelihood. For each:
- What evidence supports this hypothesis?
- What would disprove it?
- What's the simplest test?

### Step 4 — Investigate
Read the relevant code. Use Grep to find where the failing function is called. Check:
- Input values at the point of failure
- Any recent changes to that code path (`git log -p -- <file>`)
- Similar patterns in other files that work

### Step 5 — Fix and verify
- Implement the minimal fix (don't over-engineer)
- Run the specific failing test: `uv run pytest -k "<test name>" -v`
- Run the full test suite: `uv run pytest`
- Explain what the root cause was and why the fix works

### Output format
```
Root cause: <one sentence>
Evidence: <what confirmed the hypothesis>
Fix: <what was changed and why>
Prevention: <how to avoid this class of bug in the future>
```
