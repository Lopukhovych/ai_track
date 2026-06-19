# /orchestrate — Sequential Multi-Agent Coordination

Coordinate specialized subagents through a predefined workflow for complex tasks.

## Task

`$ARGUMENTS`

## Current project state

```
!`git log --oneline -5`
```

```
!`git diff HEAD --stat 2>/dev/null | head -20`
```

## Select workflow type

Choose the workflow that matches the task:

### `feature` — New feature implementation
1. **doc-researcher** → Find related curriculum content and prior art
2. **Plan agent** → Design implementation (waits for confirmation)
3. **code-reviewer** → Review implementation after completion
4. **notebook-validator** → Validate any notebooks affected

### `bugfix` — Debugging a regression
1. **doc-researcher** → Find where the failing behavior is documented
2. **python-linter** → Identify static issues in affected files
3. **code-reviewer** → Root cause analysis with git blame context

### `refactor` — Code cleanup
1. **python-linter** → Baseline lint report before changes
2. **code-reviewer** → Review refactored code
3. **notebook-validator** → Ensure no notebooks broke

### `review` — Pre-merge quality gate
Run all agents in parallel (independent checks):
- **python-linter** (static analysis)
- **code-reviewer** (logic and AI/ML patterns)
- **notebook-validator** (lab integrity)

## Agent handoff format

Each agent produces a structured handoff for the next:

```markdown
## Handoff: <agent-name> → <next-agent-name>
**Status:** PASS / FAIL / NEEDS ATTENTION
**Findings:** [bullet list]
**Files changed:** [list]
**Recommended focus for next agent:** [specific areas]
```

## Final orchestration report

After all agents complete, produce:

```
## Orchestration Summary
Workflow: <type>
Agents run: <list>
Overall status: APPROVED / BLOCKED / NEEDS REVIEW

### Agent results
| Agent | Status | Key finding |
|-------|--------|-------------|

### Files changed
### Recommendation
```
