SELECT trade_ts, channel, symbol, qty, px, book
FROM energy_trade_events
WHERE counterparty = 'UTILITY_02' AND version = 1 AND trade_ts IN '2026-11-11'
ORDER BY trade_ts;
