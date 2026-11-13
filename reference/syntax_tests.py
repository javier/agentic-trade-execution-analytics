"""Check which syntax forms QuestDB 10.2.0 accepts, for the skill feedback."""
import json
import time
import urllib.parse
import urllib.request

TESTS = {
    "tick date..date": "SELECT count() FROM energy_fills WHERE ts IN '2026-11-10..2026-11-12'",
    "tick date..dateThh": "SELECT count() FROM energy_fills WHERE ts IN '2026-11-10..2026-11-12T12'",
    "tick [date..date]": "SELECT count() FROM energy_fills WHERE ts IN '[2026-11-10..2026-11-11]'",
    "tick day bracket": "SELECT count() FROM energy_fills WHERE ts IN '2026-11-[10..11]'",
    "tick date;2d": "SELECT count() FROM energy_fills WHERE ts IN '2026-11-10;2d'",
    "tick dateT00;60h": "SELECT count() FROM energy_fills WHERE ts IN '2026-11-10T00:00;60h'",
    "tick $today-2d..$today": "SELECT count() FROM energy_fills WHERE ts IN '$today-2d..$today'",
    "tick list of days": "SELECT count() FROM energy_fills WHERE ts IN '[2026-11-10, 2026-11-11]'",
    "horizon 100ms": "SELECT h.offset, count() FROM (energy_fills WHERE ts IN '2026-11-11') f HORIZON JOIN (energy_quotes WHERE ts IN '2026-11-11') q ON (f.symbol = q.symbol) LIST (0, 100ms) AS h",
    "horizon 100T": "SELECT h.offset, count() FROM (energy_fills WHERE ts IN '2026-11-11') f HORIZON JOIN (energy_quotes WHERE ts IN '2026-11-11') q ON (f.symbol = q.symbol) LIST (0, 100T) AS h",
    "horizon 100U": "SELECT h.offset, count() FROM (energy_fills WHERE ts IN '2026-11-11') f HORIZON JOIN (energy_quotes WHERE ts IN '2026-11-11') q ON (f.symbol = q.symbol) LIST (0, 100U) AS h",
    "horizon 100u": "SELECT h.offset, count() FROM (energy_fills WHERE ts IN '2026-11-11') f HORIZON JOIN (energy_quotes WHERE ts IN '2026-11-11') q ON (f.symbol = q.symbol) LIST (0, 100u) AS h",
    "in subquery uuid": "SELECT count() FROM energy_trade_events WHERE trade_id IN (SELECT trade_id FROM energy_fills WHERE ts IN '2026-11-11')",
    "in subquery symbol": "SELECT count() FROM energy_fills WHERE symbol IN (SELECT symbol FROM energy_listings WHERE is_primary)",
    "in subquery long": "SELECT count() FROM energy_trade_events WHERE version IN (SELECT version FROM energy_trade_events WHERE version > 1)",
    "case uuid is null": "SELECT sum(CASE WHEN trade_id IS NULL THEN 1 ELSE 0 END) FROM energy_fills WHERE ts IN '2026-11-11'",
    "case uuid is null left join": "SELECT sum(CASE WHEN e.trade_id IS NULL THEN 1 ELSE 0 END) FROM energy_fills f LEFT JOIN (SELECT trade_id FROM energy_trade_events WHERE version = 1) e ON e.trade_id = f.trade_id WHERE f.ts IN '2026-11-11'",
    "case varchar is null": "SELECT sum(CASE WHEN trader IS NULL THEN 1 ELSE 0 END) FROM energy_fills WHERE ts IN '2026-11-11'",
    "uuid is null no case": "SELECT count() FROM energy_fills f LEFT JOIN (SELECT trade_id FROM energy_trade_events WHERE version = 1) e ON e.trade_id = f.trade_id WHERE f.ts IN '2026-11-11' AND e.trade_id IS NULL",
    "horizon right unbounded": "SELECT count() FROM energy_fills f HORIZON JOIN energy_quotes q ON (f.symbol = q.symbol AND f.venue = q.source) LIST (0, 5m) AS h WHERE f.ts IN '2026-11-11'",
    "horizon right bounded": "SELECT count() FROM (energy_fills WHERE ts IN '2026-11-11') f HORIZON JOIN (energy_quotes WHERE ts IN '2026-11-11T00:00;24h10m') q ON (f.symbol = q.symbol AND f.venue = q.source) LIST (0, 5m) AS h",
}

for name, sql in TESTS.items():
    url = "http://127.0.0.1:19000/exec?" + urllib.parse.urlencode({"query": sql, "timings": "true"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(url, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        data = json.loads(e.read())
    ms = int((time.time() - t0) * 1000)
    if "error" in data:
        print(f"FAIL {name:28} {data['error']}")
    else:
        print(f"OK   {name:28} {data['dataset'][:3]} ({ms} ms)")
