"""Data feed module for AI Trading Copilot v1.0.

This module is responsible for loading and serving OHLCV candle data
for a small universe of instruments and timeframes.

It is intentionally simple for v1.0 and assumes CSV-based storage.
Later versions can swap this out for live broker APIs or databases
without changing the public interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple, Optional

import pandas as pd


SUPPORTED_TIMEFRAMES = {"D", "H4", "H1"}


@dataclass
class DataFeedConfig:
    """Configuration for a data feed source.

    path_pattern:
        A pattern like "data/{symbol}_{timeframe}.csv".
    """

    path_pattern: str = "data/{symbol}_{timeframe}.csv"


class DataFeed:
    """Provides OHLCV data access for instruments and timeframes.

    Usage:

        cfg = DataFeedConfig(path_pattern="data/{symbol}_{timeframe}.csv")
        feed = DataFeed(cfg)
        df = feed.get_candles("EURUSD", "H4", limit=500)

    CSV format (per file):

        timestamp,open,high,low,close,volume

    Timestamps are expected in ISO 8601 or a broker-specific format that
    pandas can parse.
    """

    def __init__(self, config: Optional[DataFeedConfig] = None) -> None:
        self.config = config or DataFeedConfig()
        # Cache: (symbol, timeframe) -> DataFrame
        self._cache: Dict[Tuple[str, str], pd.DataFrame] = {}

    def _resolve_path(self, symbol: str, timeframe: str) -> Path:
        if timeframe not in SUPPORTED_TIMEFRAMES:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        path_str = self.config.path_pattern.format(symbol=symbol, timeframe=timeframe)
        return Path(path_str)

    def _load_csv(self, symbol: str, timeframe: str) -> pd.DataFrame:
        path = self._resolve_path(symbol, timeframe)
        if not path.exists():
            raise FileNotFoundError(f"Data file not found: {path}")
        df = pd.read_csv(path)
        # Standardise column names
        df.columns = [c.lower() for c in df.columns]
        if "timestamp" not in df.columns:
            raise ValueError(f"CSV file {path} must contain a 'timestamp' column.")
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)
        return df

    def load(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Load candles for a symbol/timeframe into cache and return the DataFrame."""
        key = (symbol, timeframe)
        if key not in self._cache:
            self._cache[key] = self._load_csv(symbol, timeframe)
        return self._cache[key]

    def reload(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Force reload candles from disk, replacing any cached data."""
        key = (symbol, timeframe)
        self._cache[key] = self._load_csv(symbol, timeframe)
        return self._cache[key]

    def get_candles(self, symbol: str, timeframe: str, limit: Optional[int] = None) -> pd.DataFrame:
        """Return the most recent candles.

        Parameters
        ----------
        symbol:
            Instrument symbol, for example "EURUSD".
        timeframe:
            Timeframe code, for example "D", "H4", "H1".
        limit:
            Optional maximum number of most recent rows to return.

        Returns
        -------
        pandas.DataFrame
            Sorted by timestamp ascending.
        """
        df = self.load(symbol, timeframe)
        if limit is not None and limit > 0:
            return df.tail(limit).copy()
        return df.copy()
