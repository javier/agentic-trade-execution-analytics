import json
import sys
import urllib.parse
import urllib.request

QUERIES = {
    "tables": "SELECT table_name FROM tables() WHERE table_name IN ('fx_trades','market_data','core_price')",
    "trade_volume_1h": """
SELECT count() n, count_distinct(ecn) ecns, count_distinct(counterparty) cps,
       min(timestamp), max(timestamp)
FROM fx_trades WHERE timestamp IN '$now-1h..$now'""",
    "markout_by_ecn_passive": """
SELECT t.ecn, t.passive, h.offset / 1000000000 AS horizon_sec, count() AS n,
  round(avg(CASE t.side
    WHEN 'buy'  THEN ((m.best_bid + m.best_ask) / 2 - t.price) / t.price * 10000
    WHEN 'sell' THEN (t.price - (m.best_bid + m.best_ask) / 2) / t.price * 10000
  END), 3) AS bps
FROM fx_trades t
HORIZON JOIN market_data m ON (symbol)
  LIST (0, 5s, 30s) AS h
WHERE t.timestamp IN '$now-1h..$now'
GROUP BY t.ecn, t.passive, horizon_sec
ORDER BY t.ecn, t.passive, horizon_sec""",
    "markout_by_cp_30s": """
SELECT t.counterparty, count() AS n, sum(t.quantity) vol,
  round(avg(CASE t.side
    WHEN 'buy'  THEN ((m.best_bid + m.best_ask) / 2 - t.price) / t.price * 10000
    WHEN 'sell' THEN (t.price - (m.best_bid + m.best_ask) / 2) / t.price * 10000
  END), 3) AS bps_30s
FROM fx_trades t
HORIZON JOIN market_data m ON (symbol)
  LIST (30s) AS h
WHERE t.timestamp IN '$now-1h..$now'
GROUP BY t.counterparty
ORDER BY bps_30s""",
    "markout_by_symbol_30s": """
SELECT t.symbol, count() AS n,
  round(avg(CASE t.side
    WHEN 'buy'  THEN ((m.best_bid + m.best_ask) / 2 - t.price) / t.price * 10000
    WHEN 'sell' THEN (t.price - (m.best_bid + m.best_ask) / 2) / t.price * 10000
  END), 3) AS bps_30s
FROM fx_trades t
HORIZON JOIN market_data m ON (symbol)
  LIST (30s) AS h
WHERE t.timestamp IN '$now-1h..$now'
GROUP BY t.symbol
ORDER BY bps_30s""",
}

names = sys.argv[1:] or list(QUERIES)
for name in names:
    url = "https://demo.questdb.io/exec?" + urllib.parse.urlencode({"query": QUERIES[name]})
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.7.1"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        print("==", name, "HTTP", e.code, e.read()[:500])
        continue
    print("==", name, "timings:", data.get("timings"))
    if "error" in data:
        print("ERROR", data["error"])
        continue
    print([c["name"] for c in data["columns"]])
    for row in data["dataset"][:60]:
        print(row)
