"""Second round: TICK micro-second unit casing, IN subquery on varchar, NULL-count workarounds."""
import json
import urllib.parse
import urllib.request

TESTS = {
    "tick $now-100u": "SELECT count() FROM energy_fills WHERE ts IN '$now-100u..$now'",
    "tick $now-100U": "SELECT count() FROM energy_fills WHERE ts IN '$now-100U..$now'",
    "tick $now-100T": "SELECT count() FROM energy_fills WHERE ts IN '$now-100T..$now'",
    "in subquery varchar": "SELECT count() FROM energy_fills WHERE trader IN (SELECT trader FROM energy_fills WHERE ts IN '2026-11-11' LIMIT 3)",
    "count minus count": "SELECT count() - count(e.trade_id) AS missing FROM energy_fills f LEFT JOIN (SELECT trade_id FROM energy_trade_events WHERE version = 1) e ON e.trade_id = f.trade_id WHERE f.ts IN '2026-11-11'",
    "case uuid nested if": "SELECT sum(CASE WHEN e.trade_id IS NULL AND 1 = 1 THEN 1 ELSE 0 END) FROM energy_fills f LEFT JOIN (SELECT trade_id FROM energy_trade_events WHERE version = 1) e ON e.trade_id = f.trade_id WHERE f.ts IN '2026-11-11'",
    "case uuid is not null": "SELECT sum(CASE WHEN trade_id IS NOT NULL THEN 1 ELSE 0 END) FROM energy_fills WHERE ts IN '2026-11-11'",
    "case uuid = const": "SELECT sum(CASE WHEN trade_id = '11111111-1111-1111-1111-111111111111' THEN 1 ELSE 0 END) FROM energy_fills WHERE ts IN '2026-11-11'",
    "case long is null": "SELECT sum(CASE WHEN version IS NULL THEN 1 ELSE 0 END) FROM energy_trade_events",
}
for name, sql in TESTS.items():
    url = "http://127.0.0.1:19000/exec?" + urllib.parse.urlencode({"query": sql})
    try:
        with urllib.request.urlopen(url, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        data = json.loads(e.read())
    print(("FAIL " if "error" in data else "OK   ") + f"{name:24} " + str(data.get("error", data.get("dataset", [])[:2])))
