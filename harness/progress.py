"""Summarise a stream-json agent transcript: tool calls, SQL errors, recent narration."""
import collections
import json
import sys

path = sys.argv[1]
n_tail = int(sys.argv[2]) if len(sys.argv) > 2 else 6
calls = collections.Counter()
errors = []
texts = []
sqls = []
pending = {}
result = None
for line in open(path):
    try:
        ev = json.loads(line)
    except json.JSONDecodeError:
        continue
    if ev.get("type") == "result":
        result = ev
    msg = ev.get("message") or {}
    for block in msg.get("content") or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use":
            name = block["name"].replace("mcp__questdb__", "qdb:")
            calls[name] += 1
            inp = block.get("input") or {}
            sql = inp.get("query") or inp.get("sql") or inp.get("content")
            pending[block["id"]] = (name, sql)
            if sql and name in ("qdb:run_query", "qdb:validate_query"):
                sqls.append(sql)
        elif block.get("type") == "tool_result":
            content = block.get("content")
            txt = json.dumps(content)[:400]
            if block.get("is_error") or '"error"' in txt.lower()[:200]:
                name, sql = pending.get(block.get("tool_use_id"), ("?", None))
                errors.append((name, txt[:300], (sql or "")[:200]))
        elif block.get("type") == "text" and ev.get("type") == "assistant":
            texts.append(block["text"])

print("TOOL CALLS", sum(calls.values()), dict(calls.most_common()))
print("ERRORS", len(errors))
for e in errors[-8:]:
    print("  -", e[0], "|", e[1].replace("\\n", " ")[:220], "| SQL:", e[2].replace("\n", " ")[:150])
print("QUERIES RUN/VALIDATED", len(sqls))
print("--- last narration ---")
for t in texts[-n_tail:]:
    print(">", t[:700].replace("\n", " "))
if result:
    print("RESULT", {k: result.get(k) for k in ("subtype", "num_turns", "duration_ms", "is_error")})
