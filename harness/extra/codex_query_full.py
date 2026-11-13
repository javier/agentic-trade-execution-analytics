"""Print full SQL and a result excerpt for selected run_query indices of a Codex transcript."""
import json
import sys

path = sys.argv[1]
wanted = {int(x) for x in sys.argv[2].split(",")}
i = 0
for line in open(path):
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    if ev.get("type") != "item.completed":
        continue
    item = ev["item"]
    if item.get("type") == "mcp_tool_call" and item.get("tool") == "run_query":
        i += 1
        if i in wanted:
            args = item.get("arguments") or {}
            print(f"===== [{i}]")
            print(args.get("sql") or args.get("query"))
            res = item.get("result") or {}
            text = ""
            for c in res.get("content") or []:
                text += c.get("text", "")
            print("RESULT:", text[:1500])
