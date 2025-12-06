"""Basic backtest example for AI Trading Copilot v1.0.

This script:

1. Uses the same DataFeed and StrategyEngine as live trading.
2. Walks through H4 EURUSD candles bar by bar.
3. On each bar (after a warm-up period), generates signals using
   all data up to that bar.
4. Manages at most one open trade at a time with SL / TP1 exits.
5. Calculates results in R and prints a summary at the end.

This is a deliberately simple first-pass backtest to validate the
strategy logic and execution flow. It is not yet a full portfolio
backtester or walk-forward engine.
"""

from __future__ import annotations

from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from src.v1_0.core.data_feed import DataFeed, DataFeedConfig
from src.v1_0.core.strategy import StrategyEngine, StrategyConfig, Signal
from src.v1_0.core.config import load_config
from src.v1_0.core.news import NewsEngine


@dataclass
class BacktestTrade:
    direction: str
    entry: float
    stop: float
    tp1: float
    open_time: pd.Timestamp
    close_time: Optional[pd.Timestamp] = None
    exit_price: Optional[float] = None
    outcome_r: Optional[float] = None


def run_backtest() -> None:
    cfg = load_config()
    feed = DataFeed(DataFeedConfig(path_pattern=cfg.data.path_pattern))
    sc = cfg.strategy
    
    # Initialize news engine if enabled
    news_engine = None
    if cfg.news.enabled:
        news_engine = NewsEngine(cfg.news)
    
    engine = StrategyEngine(
        config=StrategyConfig(
            risk_percent_default=sc.risk_percent_default,
            min_rr=sc.min_rr,
            atr_stop_multiplier=sc.atr_stop_multiplier,
        ),
        news_engine=news_engine,
    )

    instrument = "EURUSD"
    df_daily = feed.get_candles(instrument, "D")
    df_h4 = feed.get_candles(instrument, "H4")

    if df_daily.empty or df_h4.empty:
        print("No data loaded. Check CSV files in data/ directory.")
        return

    print(f"Backtest on {instrument}: {len(df_h4)} H4 bars, {len(df_daily)} Daily bars.")

    open_trades: List[BacktestTrade] = []
    closed_trades: List[BacktestTrade] = []
    total_signal_candidates = 0
    news_blocked_count = 0

    # We iterate over H4 bars starting after some warm-up period
    warmup = 50
    for i in range(warmup, len(df_h4)):
        current_time = df_h4.iloc[i]["timestamp"]
        # Subset H4 up to and including current bar
        h4_slice = df_h4.iloc[: i + 1]
        # Subset Daily up to current time
        daily_slice = df_daily[df_daily["timestamp"] <= current_time]
        if len(daily_slice) < 30:
            continue  # not enough daily history

        # 1) Update existing open trades
        bar = df_h4.iloc[i]
        high = bar["high"]
        low = bar["low"]
        close = bar["close"]

        still_open: List[BacktestTrade] = []
        for trade in open_trades:
            r_per_point = (trade.entry - trade.stop) if trade.direction == "long" else (trade.stop - trade.entry)
            r_per_point = abs(r_per_point)
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
            else:  # short
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
                closed_trades.append(trade)
            else:
                still_open.append(trade)

        open_trades = still_open

        # 2) Generate new signals from strategy using all data so far
        signals: List[Signal] = engine.generate_signals(instrument, daily_slice, h4_slice)
        total_signal_candidates += 1
        
        if not signals:
            # Signal was filtered out (potentially by news)
            news_blocked_count += 1
            continue

        sig = signals[-1]
        # Only one open trade at a time in this simple example
        if open_trades:
            continue

        # Open a new trade at the signal's entry price on the next bar
        trade = BacktestTrade(
            direction=sig.direction,
            entry=sig.entry,
            stop=sig.stop,
            tp1=sig.tp1,
            open_time=current_time,
        )
        open_trades.append(trade)

    # Close any remaining open trades at last close price
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
            closed_trades.append(trade)
        open_trades = []

    if not closed_trades:
        print("No trades closed in this backtest.")
        return

    # Summarise results
    outcomes = [t.outcome_r for t in closed_trades if t.outcome_r is not None]
    total_r = sum(outcomes)
    avg_r = total_r / len(outcomes)
    wins = [r for r in outcomes if r > 0]
    losses = [r for r in outcomes if r <= 0]

    print("")
    print(f"Total trades: {len(outcomes)}")
    print(f"Total R     : {total_r:.2f}")
    print(f"Average R   : {avg_r:.2f}")
    print(f"Wins        : {len(wins)}")
    print(f"Losses      : {len(losses)}")
    print(f"Signals blocked: {news_blocked_count} / {total_signal_candidates} candidates")

    if losses:
        avg_loss = sum(losses) / len(losses)
        print(f"Avg loss R  : {avg_loss:.2f}")
    if wins:
        avg_win = sum(wins) / len(wins)
        print(f"Avg win R   : {avg_win:.2f}")


load_dotenv()

if __name__ == "__main__":
    run_backtest()
