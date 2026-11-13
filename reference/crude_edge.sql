WITH m AS (
  SELECT timestamp_floor('d', t.ts) AS d,
         (t.ts IN '2026-11-11T07:00;90m') AS breach_window,
         10000 * CASE WHEN t.qty > 0 THEN 1 ELSE -1 END * ((q.bid + q.ask) / 2 - t.px) / t.px AS bps
  FROM (energy_fills WHERE book = 'CRUDE') AS t
  HORIZON JOIN energy_quotes q ON (t.symbol = q.symbol AND t.venue = q.source)
  LIST (15m) AS h
)
SELECT d, breach_window, count() AS fills, round(avg(bps), 2) AS markout_15m_bps
FROM m
ORDER BY d, breach_window;
