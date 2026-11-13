DECLARE @demo_day := '2026-11-11'
WITH t AS (
  (SELECT trade_ts AS ts, symbol, qty, px, counterparty
   FROM energy_trade_events
   WHERE version = 1 AND channel != 'EXCH'
     AND booked_ts >= dateadd('d', -2, @demo_day::timestamp) AND trade_ts >= dateadd('d', -2, @demo_day::timestamp))
  ORDER BY ts
)
SELECT h.offset / 60000000 AS horizon_min,
       regexp_replace(t.counterparty, '_.*$', '') AS counterparty_type,
       count() AS deals,
       round(avg(10000 * CASE WHEN t.qty > 0 THEN 1 ELSE -1 END * (mid(q.last_bid, q.last_ask) - t.px) / t.px), 2)::decimal(8,2) AS markout_bps
FROM (t TIMESTAMP(ts)) AS t
HORIZON JOIN (energy_quotes_1m WHERE ts >= dateadd('d', -2, @demo_day::timestamp)) AS q ON (symbol)
LIST (1m, 5m, 15m, 1h, 4h) AS h
ORDER BY counterparty_type, horizon_min;
