#!/bin/bash
# PostToolUse hook — validate notebook JSON structure after edits
# Fires on: Write (matched by *.ipynb pattern in settings)

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.path // empty')

[[ "$FILE" != *.ipynb ]] && exit 0
[ -z "$FILE" ] && exit 0
[ ! -f "$FILE" ] && exit 0

# Check that the file is valid JSON and has required nbformat fields
if ! jq -e '.nbformat and .cells and .metadata' "$FILE" > /dev/null 2>&1; then
    echo "Warning: $FILE may have invalid notebook structure" >&2
    exit 0
fi

# Count TODO cells remaining
TODO_COUNT=$(jq '[.cells[].source | join("") | select(contains("# TODO"))] | length' "$FILE" 2>/dev/null || echo 0)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "Note: $FILE still has $TODO_COUNT TODO cell(s) remaining" >&2
fi

exit 0
