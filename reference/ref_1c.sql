DECLARE @demo_day := '2026-11-11'
SELECT h.offset / 1000000 AS horizon_s,
       t.book,
       count() AS fills,
       round(avg(10000 * CASE WHEN t.qty > 0 THEN 1 ELSE -1 END * (mid(q.bid, q.ask) - t.px) / t.px), 2)::decimal(8,2) AS markout_bps
FROM (energy_fills WHERE ts IN @demo_day) AS t
HORIZON JOIN (energy_quotes WHERE ts >= @demo_day::timestamp AND ts < dateadd('m', 16, dateadd('d', 1, @demo_day::timestamp))) AS q
  ON (t.symbol = q.symbol AND t.venue = q.source)
LIST (0, 1s, 10s, 1m, 5m, 15m) AS h
ORDER BY t.book, horizon_s;
