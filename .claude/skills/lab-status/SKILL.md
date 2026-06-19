---
name: lab-status
description: Show current lab progress — which notebooks are complete, which have open TODOs, and what to work on next.
context: fork
agent: Explore
allowed-tools: Bash(ls *), Bash(git *), Bash(grep *), Bash(jq *), Read
---

## Live environment data

**Notebooks:**
```
!`ls -1 labs/*.ipynb 2>/dev/null | sort`
```

**Git status:**
```
!`git status --short`
```

**Open TODOs in lab code cells:**
```
!`grep -rn "# TODO" labs/ --include="*.ipynb" 2>/dev/null | grep -v "solution\|hint" | head -20 || echo "none"`
```

**Recent commits:**
```
!`git log --oneline -8`
```

## Your task

1. For each lab notebook, determine completion status:
   - **Complete:** has saved cell outputs, no `# TODO` in code cells
   - **In Progress:** has some outputs but remaining TODOs
   - **Not Started:** no outputs or empty cells

2. Map each notebook to its curriculum week topic.

3. Identify the **single best next exercise** to work on with a brief reason (what skill it builds, how it connects to the curriculum).

4. Flag any environment issues visible in the git status (e.g., uncommitted `.env` file, conflicted files).

Keep the response to: one-table summary + "Next recommended exercise" section (3-4 sentences max).
