# /tdd — Test-Driven Development Workflow

Enforce the red → green → refactor cycle. Tests are written BEFORE implementation.

## Target

`$ARGUMENTS` — the feature, function, or bug fix to implement.

## Current test state

```
!`uv run pytest --collect-only -q 2>/dev/null | tail -20`
```

## TDD Cycle

### Phase 1 — RED: Write failing tests first

Before touching any implementation code:

1. Identify the function or class to implement
2. Write tests covering:
   - **Happy path** — expected inputs produce expected outputs
   - **Edge cases** — empty input, None, zero, max values
   - **Error cases** — invalid types, out-of-range values, missing fields
3. Run tests and verify they **fail** (red is required — if tests pass already, they're wrong)
4. Report: `Tests written: N | Failing: N | Coverage target: 80%+`

### Phase 2 — GREEN: Minimal implementation

Write the **minimum code** to make tests pass. Do not over-engineer.

Rules:
- No premature abstraction
- No extra parameters not needed by tests
- No docstrings or comments yet
- Run tests after each function — stop if anything unexpected passes

Report: `Tests passing: N/N`

### Phase 3 — REFACTOR: Clean without breaking

Now improve the code with tests as your safety net:
- Remove duplication
- Improve naming
- Add type hints
- Extract helpers if logic is repeated 3+ times

After every change: `uv run pytest -q` must stay green.

Report: `Final: N tests passing | Coverage: X%`

## Coverage requirements

| Code type | Minimum coverage |
|-----------|-----------------|
| Business logic | 100% |
| Authentication / security | 100% |
| API endpoints | 90%+ |
| Utility functions | 80%+ |
| Lab exercises | 70%+ |

Run coverage: `uv run pytest --cov=. --cov-report=term-missing -q`
