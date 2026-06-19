#!/bin/bash
# PostToolUse hook — auto-format Python files after Claude edits them
# Async: runs in background, never blocks Claude
# Fires on: Edit, Write (matched by settings.json)

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.path // empty')

# Only act on Python files
[[ "$FILE" != *.py ]] && exit 0
[ -z "$FILE" ] && exit 0
[ ! -f "$FILE" ] && exit 0

# Find repo root (where pyproject.toml lives)
REPO_ROOT=$(git -C "$(dirname "$FILE")" rev-parse --show-toplevel 2>/dev/null)
[ -z "$REPO_ROOT" ] && REPO_ROOT=$(dirname "$FILE")

# Run ruff format + lint fix (quiet — errors go to /dev/null)
cd "$REPO_ROOT" || exit 0
uv run ruff format "$FILE" --quiet 2>/dev/null || true
uv run ruff check "$FILE" --fix --quiet 2>/dev/null || true

exit 0
