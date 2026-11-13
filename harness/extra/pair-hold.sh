#!/usr/bin/env bash
# Usage: pair-hold.sh [mcp_config.json]
# Pairs a QuestDB MCP server with a console and keeps it connected for 15
# minutes, e.g. to take screenshots that show "MCP connected". Pair it from the
# tab you will screenshot, and close the tab the server opens by itself.
set -euo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="${1:-$H/mcp-fable1.json}"
WORK="${TMPDIR:-/tmp}/pairhold"
mkdir -p "$WORK"
cd "$WORK"
claude -p \
  --model haiku \
  --setting-sources project \
  --strict-mcp-config --mcp-config "$CFG" \
  --no-chrome \
  --permission-mode dontAsk \
  --allowedTools "mcp__questdb__get_pairing_credentials" "mcp__questdb__wait_for_pairing" "Bash(sleep:*)" \
  --output-format stream-json --verbose \
  "Call the questdb tool get_pairing_credentials, then call wait_for_pairing until it reports paired (retry on timeout). Once paired, run the shell command 'sleep 900' and then reply DONE. Do not call any other tool." > "$WORK/pairhold.jsonl"
