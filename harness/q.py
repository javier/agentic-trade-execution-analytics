"""Run one SQL file against the eval instance and print the result table."""
import json
import sys
import urllib.parse
import urllib.request

sql = open(sys.argv[1]).read()
url = "http://127.0.0.1:19000/exec?" + urllib.parse.urlencode({"query": sql})
with urllib.request.urlopen(url, timeout=300) as r:
    data = json.load(r)
if "error" in data:
    sys.exit("ERROR: " + data["error"])
print([c["name"] + ":" + c["type"] for c in data["columns"]])
for row in data["dataset"]:
    print(row)
