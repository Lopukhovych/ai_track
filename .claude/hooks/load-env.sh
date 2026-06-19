#!/bin/bash
# SessionStart hook — inject project environment variables
# Writes exports to CLAUDE_ENV_FILE so they persist in Claude's shell context
# Fires on: SessionStart

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty')

[ -z "$CLAUDE_ENV_FILE" ] && exit 0

REPO_ROOT=$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null)
[ -z "$REPO_ROOT" ] && REPO_ROOT="$CWD"

# Load project .env if it exists (export key=value lines only, skip comments)
ENV_FILE="$REPO_ROOT/.env"
if [ -f "$ENV_FILE" ]; then
    while IFS= read -r line; do
        # Skip comments and blank lines
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        # Only export valid KEY=VALUE lines
        if [[ "$line" =~ ^[A-Z_][A-Z0-9_]*= ]]; then
            echo "export $line" >> "$CLAUDE_ENV_FILE"
        fi
    done < "$ENV_FILE"
fi

# Always set project-specific vars
echo "export AI_TRACK_ROOT=$REPO_ROOT" >> "$CLAUDE_ENV_FILE"
echo "export PYTHONPATH=$REPO_ROOT" >> "$CLAUDE_ENV_FILE"

exit 0
