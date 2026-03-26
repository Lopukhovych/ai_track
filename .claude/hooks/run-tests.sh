#!/bin/bash
# Stop hook — run pytest when Claude finishes responding
# Informational only: exit 0 always (failure shown but doesn't block)
# Only runs if .py files were modified in this session

INPUT=$(cat)
TRANSCRIPT=$(echo "$INPUT" | jq -r '.transcript_path // empty')
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

[ -z "$CWD" ] && exit 0

# Check if any Python files were modified in this session
if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ]; then
    MODIFIED_PY=$(grep -o '"path":"[^"]*\.py"' "$TRANSCRIPT" 2>/dev/null | wc -l)
    # No Python files touched — skip tests
    [ "$MODIFIED_PY" -eq 0 ] && exit 0
fi

cd "$CWD" || exit 0

# Only run if tests directory exists
[ ! -d "tests" ] && [ ! -f "pytest.ini" ] && [ ! -f "pyproject.toml" ] && exit 0

echo "--- Running tests ---" >&2
uv run pytest tests/ -q --tb=short --no-header 2>&1 | tail -15 >&2

exit 0
