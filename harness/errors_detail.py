"""For each failed query: full SQL, error, and the next query the agent ran. Also skill reads."""
import json
import sys

events = []
for line in open(sys.argv[1]):
    try:
        events.append(json.loads(line))
    except json.JSONDecodeError:
        pass

uses = []      # (id, name, input)
results = {}   # id -> (is_error_like, text)
for ev in events:
    for b in (ev.get("message") or {}).get("content") or []:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "tool_use":
            uses.append((b["id"], b["name"], b.get("input") or {}))
        elif b.get("type") == "tool_result":
            txt = json.dumps(b.get("content"))
            results[b["tool_use_id"]] = txt

print("=== non-query tool inputs ===")
for uid, name, inp in uses:
    if name in ("Skill", "Read", "Grep", "ToolSearch"):
        print(name, json.dumps(inp)[:300])

print("\n=== failed queries and the follow-up ===")
for i, (uid, name, inp) in enumerate(uses):
    txt = results.get(uid, "")
    if name.endswith("run_query") and '\\"error\\"' in txt[:80]:
        print("----", name)
        print("ERROR:", txt[:200])
        print("SQL:\n", inp.get("query") or inp.get("sql"))
        for uid2, name2, inp2 in uses[i + 1:]:
            if name2.endswith("run_query"):
                print("NEXT SQL:\n", inp2.get("query") or inp2.get("sql"))
                print("NEXT RESULT:", results.get(uid2, "")[:160])
                break
