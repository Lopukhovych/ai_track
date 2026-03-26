#!/bin/bash
# PreToolUse hook — blocks edits that introduce hardcoded secrets
# Fires on: Edit, Write, MultiEdit
# Exit 2 = block and feed error to Claude

INPUT=$(cat)

# Extract content being written
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.new_string // .tool_input.content // .tool_input.command // empty')

# Nothing to check
[ -z "$CONTENT" ] && exit 0

# Patterns: key = "literal_value" or key = 'literal_value'
# Intentionally broad — catches: password="x", api_key = 'x', TOKEN="x"
SECRET_PATTERN='(password|api_key|api_secret|secret_key|token|credential|auth_key)\s*=\s*["\x27][^"\x27${}()\[\]][^"\x27]{2,}["\x27]'

if echo "$CONTENT" | grep -iqE "$SECRET_PATTERN"; then
    # Exclude legitimate env var access patterns
    if echo "$CONTENT" | grep -qE '(os\.environ|os\.getenv|process\.env|getenv\(|settings\.|config\.|ENV\[|\$\{[A-Z])'; then
        exit 0
    fi
    MATCH=$(echo "$CONTENT" | grep -ioE "$SECRET_PATTERN" | head -1)
    echo "Blocked: Hardcoded secret detected — \"$MATCH\"" >&2
    echo "Use environment variables instead: os.environ[\"KEY\"] or os.getenv(\"KEY\")" >&2
    exit 2
fi

exit 0
