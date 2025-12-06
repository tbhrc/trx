"""Pydantic schemas for AI Trading Copilot v1.0 API."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SignalResponse(BaseModel):
    """HTTP representation of a trading signal.

    This mirrors the core `Signal` dataclass used by StrategyEngine.
    """

    instrument: str = Field(..., description="Instrument symbol, e.g. EURUSD")
    direction: str = Field(..., description="long or short")
    entry: float
    stop: float
    tp1: float
    tp2: Optional[float] = None
    risk_percent: float
    trend_regime: str
    timestamp: datetime
    news_blocked: bool = False
    sentiment_score: float = 0.0

    @classmethod
    def from_domain(cls, signal) -> "SignalResponse":
        """Build a SignalResponse from a core Signal dataclass."""
        return cls(
            instrument=signal.instrument,
            direction=signal.direction,
            entry=signal.entry,
            stop=signal.stop,
            tp1=signal.tp1,
            tp2=signal.tp2,
            risk_percent=signal.risk_percent,
            trend_regime=signal.trend_regime,
            timestamp=signal.timestamp.to_pydatetime() if hasattr(signal.timestamp, "to_pydatetime") else signal.timestamp,
            news_blocked=getattr(signal, "news_blocked", False),
            sentiment_score=getattr(signal, "sentiment_score", 0.0),
        )
