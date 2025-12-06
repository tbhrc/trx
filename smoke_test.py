"""Smoke test for AI Trading Copilot v1.0.

This script:

1. Loads synthetic EURUSD Daily and H4 data from the `data/` folder.
2. Runs the StrategyEngine.generate_signals pipeline.
3. Prints any generated signals to the console.

Run from repo root with:

    python smoke_test.py
"""

from __future__ import annotations

from dotenv import load_dotenv
import os

from src.v1_0.core.data_feed import DataFeed, DataFeedConfig
from src.v1_0.core.strategy import StrategyEngine, StrategyConfig
from src.v1_0.core.config import load_config


def main() -> None:
    load_dotenv()
    cfg = load_config()
    pattern = os.getenv("DATA_PATH_PATTERN", cfg.data.path_pattern)
    feed = DataFeed(DataFeedConfig(path_pattern=pattern))
    sc = cfg.strategy
    engine = StrategyEngine(
        config=StrategyConfig(
            risk_percent_default=sc.risk_percent_default,
            min_rr=sc.min_rr,
            atr_stop_multiplier=sc.atr_stop_multiplier,
        )
    )

    instrument = "EURUSD"
    df_daily = feed.get_candles(instrument, "D")
    df_h4 = feed.get_candles(instrument, "H4")

    print(f"Loaded {len(df_daily)} daily candles and {len(df_h4)} H4 candles for {instrument}.")
    signals = engine.generate_signals(instrument, df_daily, df_h4)

    if not signals:
        print("No signals generated.")
        return

    print(f"Generated {len(signals)} signal(s). Showing the most recent one:\n")
    sig = signals[-1]
    print(f"Instrument : {sig.instrument}")
    print(f"Direction  : {sig.direction}")
    print(f"Trend      : {sig.trend_regime}")
    print(f"Timestamp  : {sig.timestamp}")
    print(f"Entry      : {sig.entry}")
    print(f"Stop       : {sig.stop}")
    print(f"TP1        : {sig.tp1}")
    print(f"TP2        : {sig.tp2}")
    print(f"Risk %     : {sig.risk_percent}")


if __name__ == "__main__":
    main()
