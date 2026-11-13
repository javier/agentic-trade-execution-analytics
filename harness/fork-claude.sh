#!/usr/bin/env bash
# Usage: fork-claude.sh <run_dir> <session_id> <prompt_file> <console_origin> <transcript.jsonl>
# Forks a saved Claude Code session and sends one follow-up, against a fresh console origin.
set -euo pipefail
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$1"; SID="$2"; PROMPT_FILE="$3"; ORIGIN="$4"; OUT="$5"
NAME=$(basename "$OUT" .jsonl)
CFG="$S/mcp-$NAME.json"
cat > "$CFG" <<EOF
{"mcpServers": {"questdb": {"command": "npx", "args": ["-y", "@questdb/mcp-server-questdb@0.5.0"],
  "env": {"CONSOLE_ORIGIN": "$ORIGIN", "LOG_PATH": "$S/mcp-logs/$NAME.log"}}}}
EOF
cd "$RUN_DIR"
date -u +"START %Y-%m-%dT%H:%M:%SZ" >> "$OUT.times"
claude -p \
  --setting-sources project \
  --strict-mcp-config --mcp-config "$CFG" \
  --no-chrome \
  --permission-mode dontAsk \
  --allowedTools "mcp__questdb" "Skill" "Read" "Glob" "Grep" "WebFetch" "WebSearch" \
  --output-format stream-json --verbose \
  --resume "$SID" --fork-session \
  "$(cat "$PROMPT_FILE")" >> "$OUT"
date -u +"END %Y-%m-%dT%H:%M:%SZ" >> "$OUT.times"
