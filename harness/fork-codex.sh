#!/usr/bin/env bash
# Usage: fork-codex.sh <thread_id> <prompt_file> <console_origin> <transcript.jsonl>
# Forks a saved Codex session and sends one follow-up, against a fresh console origin.
set -euo pipefail
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TID="$1"; PROMPT_FILE="$2"; ORIGIN="$3"; OUT="$4"
NAME=$(basename "$OUT" .jsonl)
# codex exec fork has no -C option: start in the original empty run folder,
# where none of your own hooks or AGENTS.md rules apply.
cd "${CODEX_RUN_DIR:?set CODEX_RUN_DIR to the original Codex run folder}"
date -u +"START %Y-%m-%dT%H:%M:%SZ" >> "$OUT.times"
codex exec fork \
  --skip-git-repo-check --json \
  -c 'sandbox_mode="read-only"' \
  -c "mcp_servers.questdb.env.CONSOLE_ORIGIN=\"$ORIGIN\"" \
  -c "mcp_servers.questdb.env.LOG_PATH=\"$S/mcp-logs/$NAME.log\"" \
  -c 'mcp_servers.questdb.default_tools_approval_mode="approve"' \
  -c 'mcp_servers.node_repl.enabled=false' \
  -c 'plugins."browser@openai-bundled".enabled=false' \
  -c 'plugins."chrome@openai-bundled".enabled=false' \
  -c 'plugins."computer-use@openai-bundled".enabled=false' \
  -c 'plugins."unified-computer-use@openai-bundled".enabled=false' \
  -c 'notify=[]' \
  "$TID" "$(cat "$PROMPT_FILE")" >> "$OUT"
date -u +"END %Y-%m-%dT%H:%M:%SZ" >> "$OUT.times"
