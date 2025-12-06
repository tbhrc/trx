"""Indicator engine for AI Trading Copilot v1.0.

This module computes the technical indicators required by the v1.0
strategy rule sheet: EMA, RSI, ATR and basic swing structure markers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import pandas as pd


@dataclass
class IndicatorConfig:
    ema_fast: int = 20
    ema_slow: int = 50
    ema_trend: int = 200
    rsi_period: int = 14
    atr_period: int = 14


class IndicatorEngine:
    """Computes indicators on OHLC dataframes.

    All methods are pure functions on DataFrame copies to avoid
    side effects on the original feed.
    """

    def __init__(self, config: IndicatorConfig | None = None) -> None:
        self.config = config or IndicatorConfig()

    @staticmethod
    def ema(series: pd.Series, period: int) -> pd.Series:
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def rsi(series: pd.Series, period: int) -> pd.Series:
        delta = series.diff()
        gain = (delta.clip(lower=0)).rolling(window=period).mean()
        loss = (-delta.clip(upper=0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def atr(df: pd.DataFrame, period: int) -> pd.Series:
        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    def add_core_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Return a new DataFrame with EMA, RSI and ATR columns added."""
        df = df.copy()
        df["ema_fast"] = self.ema(df["close"], self.config.ema_fast)
        df["ema_slow"] = self.ema(df["close"], self.config.ema_slow)
        df["ema_trend"] = self.ema(df["close"], self.config.ema_trend)
        df["rsi"] = self.rsi(df["close"], self.config.rsi_period)
        df["atr"] = self.atr(df, self.config.atr_period)
        return df

    @staticmethod
    def mark_swings(df: pd.DataFrame, lookback: int = 2) -> pd.DataFrame:
        """Mark swing highs and lows.

        A swing high is a bar whose high is greater than highs of `lookback`
        bars on both sides. Swing low is the inverse for lows.
        """
        df = df.copy()
        highs = df["high"]
        lows = df["low"]

        swing_high = (highs == highs.rolling(window=lookback * 2 + 1, center=True).max())
        swing_low = (lows == lows.rolling(window=lookback * 2 + 1, center=True).min())

        df["swing_high"] = swing_high.fillna(False)
        df["swing_low"] = swing_low.fillna(False)
        return df

    def enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """Convenience method: add all indicators used by v1.0 strategy."""
        df = self.add_core_indicators(df)
        df = self.mark_swings(df)
        return df
