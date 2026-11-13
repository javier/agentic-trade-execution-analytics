#!/usr/bin/env bash
# Usage: run.sh <run_dir> <transcript.jsonl> [resume_session_id] [message]
# First call: starts a fresh session with prompt.txt.
# With a session id and a message: resumes that session (one intervention).
set -euo pipefail
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$1"
OUT="$2"
cd "$RUN_DIR"
COMMON=(
  -p
  --setting-sources project
  --strict-mcp-config --mcp-config "$S/${MCP_CONFIG:-mcp-eval.json}"
  --no-chrome
  --permission-mode dontAsk
  --allowedTools "mcp__questdb" "Skill" "Read" "Glob" "Grep" "WebFetch" "WebSearch"
  --output-format stream-json --verbose
)
if [[ -n "${MODEL:-}" ]]; then
  COMMON+=(--model "$MODEL")
fi
date -u +"START %Y-%m-%dT%H:%M:%SZ" >> "$OUT.times"
if [[ $# -ge 4 ]]; then
  claude "${COMMON[@]}" --resume "$3" "$4" >> "$OUT"
else
  claude "${COMMON[@]}" "$(cat "$S/prompt.txt")" >> "$OUT"
fi
date -u +"END %Y-%m-%dT%H:%M:%SZ" >> "$OUT.times"
