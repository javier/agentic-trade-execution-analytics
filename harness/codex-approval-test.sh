#!/usr/bin/env bash
# Check that codex exec can call a QuestDB MCP tool when the server's tools are pre-approved.
set -euo pipefail
S="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
codex exec --skip-git-repo-check --ephemeral -s read-only -C "$S/codexcheck" \
  -c 'mcp_servers.questdb.env.CONSOLE_ORIGIN="http://codexcheck.localhost:19000"' \
  -c 'mcp_servers.questdb.default_tools_approval_mode="approve"' \
  -c 'mcp_servers.node_repl.enabled=false' \
  -c 'notify=[]' \
  "Call the questdb MCP tool get_pairing_credentials once and print only the hostname in its deepLink. Do nothing else and do not wait for pairing."
