"""Check the column type behind the earlier VARCHAR IN-subquery test, and test a real VARCHAR."""
import json
import urllib.parse
import urllib.request

TESTS = {
    "fills column types": "SELECT column, type FROM table_columns('energy_fills') WHERE column IN ('trader', 'symbol', 'venue', 'book')",
    "varchar IN subquery": "SELECT count() FROM (SELECT trader::varchar AS t FROM energy_fills WHERE ts IN '2026-11-11') WHERE t IN (SELECT trader::varchar FROM energy_fills WHERE ts IN '2026-11-11' LIMIT 3)",
}
for name, sql in TESTS.items():
    url = "http://127.0.0.1:19000/exec?" + urllib.parse.urlencode({"query": sql})
    try:
        with urllib.request.urlopen(url, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        data = json.loads(e.read())
    print(("FAIL " if "error" in data else "OK   ") + f"{name:22} " + str(data.get("error", data.get("dataset", []))))
