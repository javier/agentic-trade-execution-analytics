"""Does BETWEEN work on DOUBLE columns and expressions?"""
import json
import urllib.parse
import urllib.request

TESTS = {
    "double column between": "SELECT count() FROM energy_fills WHERE px BETWEEN 1 AND 100",
    "double expr between": "SELECT count() FROM energy_fills WHERE px / 2 BETWEEN 1.0 AND 100.0",
    "between in select": "SELECT (px BETWEEN 1 AND 100) AS ok FROM energy_fills LIMIT 1",
    "between in case": "SELECT sum(CASE WHEN px BETWEEN 1 AND 100 THEN 1 ELSE 0 END) FROM energy_fills",
}
for name, sql in TESTS.items():
    url = "http://127.0.0.1:19000/exec?" + urllib.parse.urlencode({"query": sql})
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        data = json.loads(e.read())
    print(("FAIL " if "error" in data else "OK   ") + f"{name:22} " + str(data.get("error", data.get("dataset", [])[:1])))
