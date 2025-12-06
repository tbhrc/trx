"""Strategy engine for AI Trading Copilot v1.0.

This module wires together the data feed and indicator engine to
produce basic candidate signals according to the v1.0 Strategy Rule Sheet.

The full rule set is complex; this engine provides a clean interface
and a starting implementation that can be incrementally expanded.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from .indicators import IndicatorEngine, IndicatorConfig
from .news import NewsEngine


@dataclass
class Signal:
    instrument: str
    direction: str  # "long" or "short"
    entry: float
    stop: float
    tp1: float
    tp2: Optional[float]
    risk_percent: float
    trend_regime: str
    timestamp: pd.Timestamp
    news_blocked: bool = False
    sentiment_score: float = 0.0


@dataclass
class StrategyConfig:
    risk_percent_default: float = 0.75
    min_rr: float = 2.0  # minimum risk:reward
    atr_stop_multiplier: float = 1.25


class StrategyEngine:
    """Implements the high-level v1.0 strategy flow.

    Responsibilities:

    - Determine trend regime from Daily candles.
    - Detect pullback setups on H4.
    - Build Signal objects with entry, stop and targets.

    News filters and ML scoring are applied in higher layers.
    """

    def __init__(self, indicator_engine: Optional[IndicatorEngine] = None,
                 config: Optional[StrategyConfig] = None,
                 news_engine: Optional[NewsEngine] = None) -> None:
        self.indicators = indicator_engine or IndicatorEngine(IndicatorConfig())
        self.config = config or StrategyConfig()
        self.news_engine = news_engine

    def _trend_regime_daily(self, df_daily: pd.DataFrame) -> str:
        df = self.indicators.add_core_indicators(df_daily)
        last = df.iloc[-1]
        ema_trend = last["ema_trend"]
        ema_slow = last["ema_slow"]
        close = last["close"]

        # Simple trend regime determination based on latest bar
        if close > ema_trend and ema_slow > ema_trend:
            return "uptrend"
        if close < ema_trend and ema_slow < ema_trend:
            return "downtrend"
        return "sideways"

    def generate_signals(self, instrument: str, df_daily: pd.DataFrame, df_h4: pd.DataFrame) -> List[Signal]:
        """Generate candidate signals for a given instrument.

        This version implements a simplified subset of the full rule sheet:
        - Determine trend regime on Daily.
        - On H4, look for pullbacks into EMA zone with swing markers.
        - Suggest one signal (most recent) if conditions are met.
        """
        signals: List[Signal] = []

        regime = self._trend_regime_daily(df_daily)
        if regime == "sideways":
            return signals  # strategy does not trade sideways for v1.0

        df_h4_ind = self.indicators.enrich(df_h4)
        # We work on the last N bars for recent setups
        window = df_h4_ind.tail(50)

        # Direction filter
        if regime == "uptrend":
            direction = "long"
            # pullback: price near EMA fast/slow
            mask_zone = (window["close"] <= window["ema_slow"]) & (window["close"] >= window["ema_fast"] * 0.98)
        else:
            direction = "short"
            mask_zone = (window["close"] >= window["ema_slow"]) & (window["close"] <= window["ema_fast"] * 1.02)

        candidates = window[mask_zone]
        if candidates.empty:
            return signals

        # Use the latest bar in the zone as potential entry
        row = candidates.iloc[-1]
        atr = row["atr"]
        if pd.isna(atr) or atr <= 0:
            return signals

        entry = float(row["close"])
        if direction == "long":
            stop = float(row["low"] - self.config.atr_stop_multiplier * atr)
            tp1 = entry + self.config.min_rr * (entry - stop)
        else:
            stop = float(row["high"] + self.config.atr_stop_multiplier * atr)
            tp1 = entry - self.config.min_rr * (stop - entry)

        # v1.0: TP2 is optional; can be extended later
        tp2 = None

        # Check news filter before creating signal
        timestamp = row["timestamp"]
        news_blocked = False
        sentiment_score = 0.0
        
        if self.news_engine:
            news_blocked = self.news_engine.is_blocked(instrument, timestamp)
            sentiment_score = self.news_engine.get_sentiment_score(instrument, timestamp)
            
            # Skip signal if blocked by news
            if news_blocked:
                return signals
            
            # Skip signal if sentiment opposes direction
            if self.news_engine.should_reduce_risk(instrument, direction, timestamp):
                return signals
        
        signal = Signal(
            instrument=instrument,
            direction=direction,
            entry=entry,
            stop=stop,
            tp1=tp1,
            tp2=tp2,
            risk_percent=self.config.risk_percent_default,
            trend_regime=regime,
            timestamp=timestamp,
            news_blocked=news_blocked,
            sentiment_score=sentiment_score,
        )
        signals.append(signal)
        return signals
