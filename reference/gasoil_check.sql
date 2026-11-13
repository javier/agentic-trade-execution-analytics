WITH m AS (
  SELECT t.symbol, timestamp_floor('d', t.ts) AS d, h.offset / 1000000000 AS sec,
         10000 * CASE WHEN t.qty > 0 THEN 1 ELSE -1 END * ((q.bid + q.ask) / 2 - t.px) / t.px AS bps
  FROM (energy_fills WHERE curve = 'GASOIL' AND NOT passive) AS t
  HORIZON JOIN energy_quotes q ON (t.symbol = q.symbol AND t.venue = q.source)
  LIST (0, 5m) AS h
)
SELECT symbol, d, sec, count() AS n, round(avg(bps), 2) AS markout_bps,
       round(avg(bps) / (stddev_samp(bps) / sqrt(count())), 1) AS t_stat
FROM m
WHERE symbol IN ('GASOIL_Mar-27', 'GASOIL_Apr-27', 'GASOIL_Dec-26', 'GASOIL_Jan-27')
ORDER BY symbol, d, sec;
