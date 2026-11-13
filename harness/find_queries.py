"""Print queries (and a slice of their results) whose SQL matches any of the given words."""
import json
import sys

path, words = sys.argv[1], [w.lower() for w in sys.argv[2:]]
uses, results = [], {}
for line in open(path):
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    for b in (ev.get("message") or {}).get("content") or []:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "tool_use":
            uses.append((b["id"], b["name"], b.get("input") or {}))
        elif b.get("type") == "tool_result":
            results[b["tool_use_id"]] = json.dumps(b.get("content"))
for uid, name, inp in uses:
    sql = inp.get("query") or inp.get("sql") or ""
    if sql and any(w in sql.lower() for w in words):
        print("=" * 80)
        print(sql)
        print("RESULT:", results.get(uid, "")[:900])
