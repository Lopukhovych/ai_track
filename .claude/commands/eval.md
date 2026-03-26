# /eval — Eval-Driven Development for AI Systems

Systematic evaluation for AI-powered features. Replaces "it looks right" with measurable pass rates.

**Usage:** `/eval [define|check|report|list|clean] [feature-name]`

**Arguments:** `$ARGUMENTS`

Parse `$ARGUMENTS`: the first word is the operation (`define`, `check`, `report`, `list`, `clean`), everything after is the feature name.

---

## `define <feature-name>`

Create the directory `.claude/evals/` if it does not exist, then create `.claude/evals/<feature-name>.md` with this exact template (replace `<feature-name>` with the actual name):

```markdown
# Eval: <feature-name>

## Capability tests
<!-- What should this feature DO? -->
- [ ] Test 1: [specific input] → [expected output or behavior]
- [ ] Test 2: ...

## Regression tests
<!-- What must NOT break? -->
- [ ] Regression 1: [existing behavior that must still work]

## Success criteria
- pass@1: 80% minimum
- Latency p95: < 2000ms
- Cost: < $0.01 per call

## Baseline
<!-- Fill in after first /eval check run. -->
| Metric | Baseline | Current |
|--------|---------|---------|
| pass@1 | — | — |
| latency p95 | — | — |
```

After creating the file, report: `Created .claude/evals/<feature-name>.md — edit it to add your test cases, then run /eval check <feature-name>`

---

## `check <feature-name>`

Read `.claude/evals/<feature-name>.md`. If it does not exist, say so and stop.

For each test case listed under `## Capability tests` and `## Regression tests`:
1. Run the scenario against the current implementation
2. Compare result to expected output
3. Mark pass/fail with one-line justification

Report:
```
pass@1: X/N | Regressions: 0/N | vs baseline: first run (no baseline yet)
```

Update the `## Baseline` table if this is the first run.

---

## `report`

List all files in `.claude/evals/`. If the directory is empty, say "No evals defined — run /eval define <feature-name> first."

For each eval file: read it, report capability pass rate and regression status.

Final recommendation: **SHIP** / **DO NOT SHIP** / **NEEDS WORK**

Criteria for SHIP: all regression tests pass, pass@1 ≥ 80%, no latency regression > 20%.

---

## `list`

List all files in `.claude/evals/`. For each, show name and whether a baseline exists.

---

## `clean`

Keep the last 10 eval runs per feature. Remove older entries from `.claude/evals/logs/` if that directory exists.
