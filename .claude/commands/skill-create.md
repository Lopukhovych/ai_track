# /skill-create — Generate Skills from Git History

Analyze git history to extract repeating workflows and generate SKILL.md files encoding your team's actual practices.

## Analysis scope

`$ARGUMENTS` — optional: commit depth (default: last 50 commits), output directory (default: `.claude/skills/`)

## Current git history

```
!`git log --oneline -50 2>/dev/null`
```

## Step 1 — Pattern extraction

Analyze the git log above for:

1. **Commit message conventions** — what prefixes appear? (`feat:`, `fix:`, `docs:`, etc.)
2. **File co-change patterns** — which files change together most often?
3. **Workflow sequences** — which commit types follow each other? (e.g., `feat:` → `test:` → `fix:`)
4. **Testing patterns** — what fraction of commits touch test files?
5. **Hotspot files** — which files change most frequently?

Report the top 3 patterns found in each category.

## Step 2 — Skill candidates

For each repeating workflow pattern (minimum 3 occurrences), propose a skill:

| Pattern | Frequency | Proposed skill | Slash command |
|---------|-----------|---------------|---------------|
| ... | N | ... | /... |

## Step 3 — Generate SKILL.md files

For each approved pattern, write a `SKILL.md` in `.claude/skills/<name>/`:

```yaml
---
name: <name>
description: <one-line description matching the detected pattern>
argument-hint: <what arguments it takes>
disable-model-invocation: true
---

# /<name>

Detected from git history: this workflow appears N times in the last 50 commits.

## When to use
<derived from commit messages and context>

## Steps
<steps derived from the actual commit sequence pattern>
```

## Step 4 — Summary

Report:
- Patterns analyzed: N
- Skills generated: N
- Saved to: `.claude/skills/<name>/SKILL.md`
- Next: run `/commit` to add the new skills to git
