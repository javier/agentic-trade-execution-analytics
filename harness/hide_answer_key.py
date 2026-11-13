"""Save energy_demo_events as the private answer key, then drop it from the eval instance."""
import json
import sys
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:19000"
OUT = "answer_key.json"


def q(sql):
    url = BASE + "/exec?" + urllib.parse.urlencode({"query": sql})
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.load(r)


key = q("SELECT * FROM energy_demo_events ORDER BY 1")
if "error" in key:
    sys.exit("answer key query failed: " + key["error"])
with open(OUT, "w") as f:
    json.dump(key, f, indent=1)
print("saved", len(key["dataset"]), "rows to", OUT)
print([c["name"] for c in key["columns"]])
for row in key["dataset"]:
    print(row)

if "--drop" in sys.argv:
    print(q("DROP TABLE energy_demo_events"))

tables = q("SELECT table_name FROM tables() ORDER BY table_name")
print("tables now:", [r[0] for r in tables["dataset"]])
views = q("SELECT view_name FROM views() ORDER BY view_name")
print("views:", views.get("dataset", views))
