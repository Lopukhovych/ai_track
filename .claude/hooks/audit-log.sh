#!/bin/bash
# PostToolUse hook — append every tool call to ~/.claude/audit.jsonl
# Async: never blocks. Useful for reviewing what Claude did in a session.

INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE="$HOME/.claude/audit.jsonl"

# Build a compact log entry
echo "$INPUT" | jq -c \
    --arg ts "$TIMESTAMP" \
    '{
        ts: $ts,
        session: .session_id,
        event: .hook_event_name,
        tool: .tool_name,
        path: (.tool_input.path // .tool_input.command // null | if . then .[0:120] else null end),
        cwd: (.cwd | split("/") | last)
    }' >> "$LOG_FILE" 2>/dev/null

exit 0
