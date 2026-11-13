WITH f AS ((
  SELECT trade_ts, left(counterparty, length(counterparty) - 3) AS cp_type, symbol, qty, px
  FROM (energy_trade_events WHERE booked_ts IN '2026-11-[10..12]' LATEST ON booked_ts PARTITION BY trade_id)
  WHERE channel = 'BROKER' AND curve = 'WTI' AND status != 'CANCELLED' AND trade_ts IN '2026-11-11'
  ORDER BY trade_ts
) timestamp(trade_ts)),
m AS (
  SELECT t.cp_type, h.offset / 1000000 AS sec,
         sign(t.qty) * ((q.bid + q.ask) / 2 - t.px) / t.px * 10000 AS bps
  FROM f t
  HORIZON JOIN energy_quotes q ON (t.symbol = q.symbol AND q.source = 'CME')
  LIST (300s) AS h
)
SELECT cp_type, count() AS trades, round(avg(bps), 2) AS markout_5m_bps
FROM m
ORDER BY markout_5m_bps;
