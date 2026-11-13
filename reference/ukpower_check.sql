WITH m AS (
  SELECT timestamp_floor('d', t.ts) AS d,
         CASE WHEN t.ts IN '2026-11-11T09:15;75m' THEN 'spike'
              WHEN t.ts IN '2026-11-11T10:30;14h' THEN 'after'
              ELSE 'other' END AS win,
         10000 * CASE WHEN t.qty > 0 THEN 1 ELSE -1 END * ((q.bid + q.ask) / 2 - t.px) / t.px AS bps
  FROM (energy_fills WHERE curve = 'UKPWR' AND venue = 'ICE' AND NOT passive) AS t
  HORIZON JOIN energy_quotes q ON (t.symbol = q.symbol AND t.venue = q.source)
  LIST (5m) AS h
)
SELECT d, win, count() AS n, round(avg(bps), 2) AS markout_5m_bps,
       round(avg(bps) / (stddev_samp(bps) / sqrt(count())), 1) AS t_stat
FROM m
ORDER BY d, win;
