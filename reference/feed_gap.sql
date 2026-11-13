SELECT ts, source, count() AS ticks
FROM energy_quotes
WHERE ts IN '2026-11-11T08:42;8m' AND source IN ('EEX', 'ICE_ENDEX')
SAMPLE BY 1m
ORDER BY source, ts;
