"""Third round: literal timestamp ranges in TICK, and what U means in TICK."""
import json
import urllib.parse
import urllib.request

TESTS = {
    "full ts..ts": "SELECT count() FROM energy_fills WHERE ts IN '2026-11-10T00:00:00Z..2026-11-12T00:00:00Z'",
    "full ts..ts no Z": "SELECT count() FROM energy_fills WHERE ts IN '2026-11-10T00:00..2026-11-12T00:00'",
    "date..$today": "SELECT count() FROM energy_fills WHERE ts IN '2026-11-10..$today'",
    "$now-1U bounds": "SELECT min(ts), max(ts), count() FROM energy_fills WHERE ts IN '$now-1U..$now'",
    "$now-100U..$now-99U": "SELECT count() FROM energy_fills WHERE ts IN '$now-100U..$now-99U'",
    "interval() literal": "SELECT count() FROM energy_fills WHERE ts IN interval('2026-11-10', '2026-11-12')",
}
for name, sql in TESTS.items():
    url = "http://127.0.0.1:19000/exec?" + urllib.parse.urlencode({"query": sql})
    try:
        with urllib.request.urlopen(url, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        data = json.loads(e.read())
    print(("FAIL " if "error" in data else "OK   ") + f"{name:22} " + str(data.get("error", data.get("dataset", [])[:2])))
