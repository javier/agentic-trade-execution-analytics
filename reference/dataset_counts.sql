SELECT table_name, table_row_count, table_min_timestamp, table_max_timestamp
FROM tables()
WHERE table_name IN ('energy_quotes', 'energy_fills', 'energy_trade_events', 'energy_curve_marks', 'energy_model_prices', 'energy_iv_marks')
ORDER BY table_name;
