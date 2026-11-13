#!/usr/bin/env bash
# Usage: run-codex.sh <run_dir> <transcript.jsonl> <console_origin> [resume_session_id message]
# Fresh headless Codex run with the user's skills, the eval QuestDB MCP target,
# and browser/computer-use tools disabled for parity with the Claude runs.
set -euo pipefail
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_DIR="$1"
OUT="$2"
ORIGIN="$3"
COMMON=(
  --skip-git-repo-check
  -s read-only
  -C "$RUN_DIR"
  --json
  -c "mcp_servers.questdb.env.CONSOLE_ORIGIN=\"$ORIGIN\""
  -c "mcp_servers.questdb.env.LOG_PATH=\"$S/mcp-logs/codex.log\""
  -c 'mcp_servers.questdb.default_tools_approval_mode="approve"'
  -c 'mcp_servers.node_repl.enabled=false'
  -c 'plugins."browser@openai-bundled".enabled=false'
  -c 'plugins."chrome@openai-bundled".enabled=false'
  -c 'plugins."computer-use@openai-bundled".enabled=false'
  -c 'plugins."unified-computer-use@openai-bundled".enabled=false'
  -c 'notify=[]'
)
if [[ -n "${CODEX_MODEL:-}" ]]; then
  COMMON+=(-m "$CODEX_MODEL")
fi
date -u +"START %Y-%m-%dT%H:%M:%SZ" >> "$OUT.times"
if [[ $# -ge 5 ]]; then
  codex exec "${COMMON[@]}" resume "$4" "$5" >> "$OUT"
else
  codex exec "${COMMON[@]}" "$(cat "$S/prompt.txt")" >> "$OUT"
fi
date -u +"END %Y-%m-%dT%H:%M:%SZ" >> "$OUT.times"
