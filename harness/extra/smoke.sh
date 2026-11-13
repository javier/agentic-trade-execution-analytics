#!/usr/bin/env bash
# Usage: smoke.sh <run_dir> [mcp_config.json]
# Isolation check: asks a fresh headless session in <run_dir> what it can see.
# Expect only the project's questdb skill plus Claude Code built-ins, and no
# CLAUDE.md, memories or hooks. Also try it with --tools "" and ask for
# CLAUDE.md, memory files, MCP servers and SessionStart messages.
set -euo pipefail
H="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUN_DIR="$1"
CFG="${2:-$H/mcp-final1.json}"
cd "$RUN_DIR"
claude -p \
  --setting-sources project \
  --strict-mcp-config --mcp-config "$CFG" \
  --no-chrome \
  --tools "Skill" \
  --output-format json \
  "Do not call any tool. List by name and one-line description every skill listed as available to you, and quote the first sentence of the questdb skill description if there is one."
