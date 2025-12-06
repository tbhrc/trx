"""Equity curve computation for AI Trading Copilot v1.0.

This module reuses the same DataFeed, StrategyEngine and YAML config
to run a simple portfolio backtest and derive an equity curve.

Assumption (v1.0):

- Each trade outcome is measured in R (risk units).
- We treat 1R as 1% change in equity for the purpose of this curve.

This is only for visualisation / sanity checking, not a full risk engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

import pandas as pd

from .data_feed import DataFeed, DataFeedConfig
from .strategy import StrategyEngine, StrategyConfig, Signal
from .config import load_config


@dataclass
class BacktestTrade:
    instrument: str
    direction: str
    entry: float
    stop: float
    tp1: float
    open_time: pd.Timestamp
    close_time: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    outcome_r: Optional[float] = None


def _build_engine_and_feed() -> tuple[DataFeed, StrategyEngine]:
    cfg = load_config()
    feed = DataFeed(DataFeedConfig(path_pattern=cfg.data.path_pattern))
    sc = cfg.strategy
    strat_cfg = StrategyConfig(
        risk_percent_default=sc.risk_percent_default,
        min_rr=sc.min_rr,
        atr_stop_multiplier=sc.atr_stop_multiplier,
    )
    engine = StrategyEngine(config=strat_cfg)
    return feed, engine


def _backtest_instrument(instrument: str, feed: DataFeed, engine: StrategyEngine) -> List[BacktestTrade]:
    df_daily = feed.get_candles(instrument, "D")
    df_h4 = feed.get_candles(instrument, "H4")

    if df_daily.empty or df_h4.empty:
        return []

    trades: List[BacktestTrade] = []
    open_trades: List[BacktestTrade] = []

    warmup = 50
    for i in range(warmup, len(df_h4)):
        current_time = df_h4.iloc[i]["timestamp"]
        h4_slice = df_h4.iloc[: i + 1]
        daily_slice = df_daily[df_daily["timestamp"] <= current_time]
        if len(daily_slice) < 30:
            continue

        bar = df_h4.iloc[i]
        high = bar["high"]
        low = bar["low"]

        # Update open trades
        still_open: List[BacktestTrade] = []
        for trade in open_trades:
            r_per_point = abs(trade.entry - trade.stop)
            if r_per_point == 0:
                continue

            hit_sl = False
            hit_tp = False

            if trade.direction == "long":
                if low <= trade.stop:
                    hit_sl = True
                    exit_price = trade.stop
                elif high >= trade.tp1:
                    hit_tp = True
                    exit_price = trade.tp1
            else:
                if high >= trade.stop:
                    hit_sl = True
                    exit_price = trade.stop
                elif low <= trade.tp1:
                    hit_tp = True
                    exit_price = trade.tp1

            if hit_sl or hit_tp:
                trade.close_time = current_time
                trade.exit_price = exit_price
                if trade.direction == "long":
                    move = exit_price - trade.entry
                    trade.outcome_r = move / (trade.entry - trade.stop)
                else:
                    move = trade.entry - exit_price
                    trade.outcome_r = move / (trade.stop - trade.entry)
                trades.append(trade)
            else:
                still_open.append(trade)

        open_trades = still_open

        # Generate new signal if flat
        signals: List[Signal] = engine.generate_signals(instrument, daily_slice, h4_slice)
        if not signals or open_trades:
            continue

        sig = signals[-1]
        trade = BacktestTrade(
            instrument=instrument,
            direction=sig.direction,
            entry=sig.entry,
            stop=sig.stop,
            tp1=sig.tp1,
            open_time=current_time,
        )
        open_trades.append(trade)

    # Close remaining at last close
    if open_trades:
        last_bar = df_h4.iloc[-1]
        last_time = last_bar["timestamp"]
        last_close = last_bar["close"]
        for trade in open_trades:
            trade.close_time = last_time
            trade.exit_price = last_close
            if trade.direction == "long":
                move = last_close - trade.entry
                trade.outcome_r = move / (trade.entry - trade.stop)
            else:
                move = trade.entry - last_close
                trade.outcome_r = move / (trade.stop - trade.entry)
            trades.append(trade)

    return trades


EQUITY_CACHE: dict[str, Any] = {
    "points": None,
    "computed_at": None,
}


def compute_portfolio_equity_curve(
    initial_equity: float = 100.0,
    use_cache: bool = True,
    max_age_minutes: int = 30,
) -> List[Dict[str, Any]]:
    """Run a portfolio backtest and return an equity curve.

    If use_cache is True, the result is cached in memory for max_age_minutes.
    Returns a list of points:

        [{"timestamp": "...", "equity": 100.0}, ...]
    """
    global EQUITY_CACHE

    if use_cache and EQUITY_CACHE["points"] is not None and EQUITY_CACHE["computed_at"] is not None:
        age = datetime.utcnow() - EQUITY_CACHE["computed_at"]
        if age <= timedelta(minutes=max_age_minutes):
            return EQUITY_CACHE["points"]

    cfg = load_config()
    feed, engine = _build_engine_and_feed()

    all_trades: List[BacktestTrade] = []
    for inst in cfg.instruments:
        try:
            inst_trades = _backtest_instrument(inst, feed, engine)
            all_trades.extend(inst_trades)
        except FileNotFoundError:
            continue

    # Sort by close_time; ignore trades without close_time
    closed = [t for t in all_trades if t.close_time is not None and t.outcome_r is not None]
    if not closed:
        points: List[Dict[str, Any]] = []
        EQUITY_CACHE["points"] = points
        EQUITY_CACHE["computed_at"] = datetime.utcnow()
        return points

    closed.sort(key=lambda t: t.close_time)

    equity = initial_equity
    points: List[Dict[str, Any]] = []
    for trade in closed:
        # Treat 1R as 1% of equity
        equity *= 1.0 + (trade.outcome_r * 0.01)
        points.append(
            {
                "timestamp": trade.close_time.isoformat(),
                "equity": round(equity, 4),
            }
        )

    EQUITY_CACHE["points"] = points
    EQUITY_CACHE["computed_at"] = datetime.utcnow()
    return points
