# Data directory

This directory contains example OHLCV data files and the format
expected by the `DataFeed` in `core.data_feed`.

## File naming

- `{SYMBOL}_{TIMEFRAME}.csv`

Examples:

- `EURUSD_D.csv`  – Daily candles for EURUSD
- `EURUSD_H4.csv` – 4-hour candles for EURUSD

## CSV format

Columns (header row required):

- `timestamp` – ISO 8601 datetime string in UTC or broker time
- `open`      – open price
- `high`      – high price
- `low`       – low price
- `close`     – close price
- `volume`    – volume (or tick volume)

Rows must be sorted by timestamp ascending.

The synthetic EURUSD files here are only for pipeline testing and
do not represent real market data.
