---
name: commit
description: Create a conventional commit with a well-structured message. Use when the user asks to commit, save changes, or create a checkpoint.
argument-hint: "[message]"
disable-model-invocation: true
allowed-tools: Bash(git *)
---

Create a git commit following Conventional Commits format.

## Steps

1. Check what's staged and unstaged:
   ```bash
   git status --short
   git diff --stat HEAD
   ```

2. If nothing is staged, stage relevant changes (ask if ambiguous):
   ```bash
   git add -p  # interactive, or
   git add <specific-files>
   ```

3. Analyze the changes to determine commit type:
   - `feat:` — new feature or capability
   - `fix:` — bug fix
   - `docs:` — documentation only
   - `refactor:` — code restructuring, no behavior change
   - `test:` — adding or fixing tests
   - `chore:` — tooling, deps, config

4. Write the commit message:
   ```
   <type>(<optional-scope>): <short summary under 72 chars>

   <optional body: what changed and why, not how>

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   ```

5. If `$ARGUMENTS` is provided, use it as the summary (still apply the type prefix).

6. Create the commit:
   ```bash
   git commit -m "$(cat <<'EOF'
   <message here>
   EOF
   )"
   ```

7. Show the result: `git log --oneline -1`

**Never use `--no-verify`. Never amend published commits.**
