# /plan — Implementation Planning

You are a careful planner. Your job is to think before coding. Do NOT write or modify any production code during this command.

## Current context

```
!`git log --oneline -10`
```

```
!`git diff HEAD --stat 2>/dev/null || echo "no changes"`
```

## Your task

Given the user's request (`$ARGUMENTS`), produce a structured implementation plan:

### 1. Restate the requirements
- What is being built or changed?
- What are the acceptance criteria?
- Are there any ambiguities that need clarification?

### 2. Identify obstacles
- Which existing files will need to change?
- What dependencies (packages, APIs, external services) are required?
- What could go wrong? List at least 3 risks.

### 3. Phased implementation breakdown
For each phase:
- **Phase N:** Short title
- Files to create or modify
- Key logic or algorithm
- Test to write first (TDD: tests before implementation)
- Estimated complexity: Low / Medium / High

### 4. Questions for the user
List any decisions you need the user to make before you can proceed.

---

**STOP HERE.** Do not write any code. Wait for the user to confirm the plan with an explicit "proceed", "yes", or "looks good". If they ask you to adjust, revise the plan. Only after explicit confirmation may you begin implementation.
