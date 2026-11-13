"""Summarise a codex exec --json transcript: tool calls, failures, final message."""
import collections
import json
import sys

calls = collections.Counter()
failures = []
messages = []
usage = []
for line in open(sys.argv[1]):
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    if ev.get("type") == "turn.completed":
        usage.append(ev.get("usage"))
    if ev.get("type") != "item.completed":
        continue
    item = ev["item"]
    kind = item.get("type")
    if kind == "mcp_tool_call":
        calls[item["tool"]] += 1
        res = json.dumps(item.get("result"))
        if item.get("status") == "failed" or item.get("error") or '\\"error\\"' in res[:120]:
            args = json.dumps(item.get("arguments"))[:220]
            failures.append((item["tool"], (item.get("error") or {}).get("message") or res[:220], args))
    elif kind == "command_execution":
        calls["shell"] += 1
    elif kind == "agent_message":
        messages.append(item["text"])

print("TOOL CALLS", sum(calls.values()), dict(calls.most_common()))
print("FAILURES", len(failures))
for f in failures:
    print("  -", f[0], "|", f[1][:220].replace("\\n", " "), "| ARGS:", f[2])
print("TURNS", len(usage), "USAGE", usage[-1] if usage else None)
print("--- final message ---")
print(messages[-1] if messages else "(none)")
