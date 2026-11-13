"""List a Codex run's agent messages and run_query calls in order (SQL truncated, result head)."""
import json
import sys

path = sys.argv[1]
width = int(sys.argv[2]) if len(sys.argv) > 2 else 300
i = 0
for line in open(path):
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    if ev.get("type") != "item.completed":
        continue
    item = ev["item"]
    if item.get("type") == "agent_message":
        print(f"\n>>> {item['text'][:400]}")
    elif item.get("type") == "mcp_tool_call" and item.get("tool") == "run_query":
        i += 1
        sql = (item.get("arguments") or {}).get("sql") or (item.get("arguments") or {}).get("query") or ""
        res = json.dumps(item.get("result"))
        status = "ERR" if '\\"error\\"' in res[:150] else "ok"
        print(f"[{i:03d} {status}] {sql[:width]}".replace("\n", " "))
