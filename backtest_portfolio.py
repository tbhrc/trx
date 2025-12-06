"""Portfolio backtest example for AI Trading Copilot v1.0.

This script:

- Loads instruments list and parameters from config/config.yaml.
- Uses the same DataFeed and StrategyEngine as live trading.
- For each instrument:
  - Runs a simple one-trade-at-a-time backtest on H4.
- Aggregates results across all instruments and prints portfolio metrics.
"""

from __future__ import annotations

from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List, Optional, Dict

import pandas as pd

from src.v1_0.core.data_feed import DataFeed, DataFeedConfig
from src.v1_0.core.strategy import StrategyEngine, StrategyConfig, Signal
from src.v1_0.core.config import load_config


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


def backtest_instrument(
    instrument: str,
    feed: DataFeed,
    engine: StrategyEngine,
) -> List[BacktestTrade]:
    df_daily = feed.get_candles(instrument, "D")
    df_h4 = feed.get_candles(instrument, "H4")

    if df_daily.empty or df_h4.empty:
        print(f"[{instrument}] No data loaded. Skipping.")
        return []

    print(f"[{instrument}] {len(df_h4)} H4 bars, {len(df_daily)} Daily bars.")

    open_trades: List[BacktestTrade] = []
    closed_trades: List[BacktestTrade] = []

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
        close = bar["close"]

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
                closed_trades.append(trade)
            else:
                still_open.append(trade)

        open_trades = still_open

        # Generate new signals (one-at-a-time model)
        signals: List[Signal] = engine.generate_signals(instrument, daily_slice, h4_slice)
        if not signals:
            continue
        if open_trades:
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
            closed_trades.append(trade)

    return closed_trades


def summarise_portfolio(trades: List[BacktestTrade]) -> None:
    if not trades:
        print("No trades in portfolio backtest.")
        return

    by_instrument: Dict[str, List[float]] = {}
    all_outcomes: List[float] = []

    for t in trades:
        if t.outcome_r is None:
            continue
        all_outcomes.append(t.outcome_r)
        by_instrument.setdefault(t.instrument, []).append(t.outcome_r)

    total_r = sum(all_outcomes)
    avg_r = total_r / len(all_outcomes)

    wins = [r for r in all_outcomes if r > 0]
    losses = [r for r in all_outcomes if r <= 0]

    print("\n=== Portfolio summary ===")
    print(f"Total trades: {len(all_outcomes)}")
    print(f"Total R     : {total_r:.2f}")
    print(f"Average R   : {avg_r:.2f}")
    print(f"Wins        : {len(wins)}")
    print(f"Losses      : {len(losses)}")

    if losses:
        avg_loss = sum(losses) / len(losses)
        print(f"Avg loss R  : {avg_loss:.2f}")
    if wins:
        avg_win = sum(wins) / len(wins)
        print(f"Avg win R   : {avg_win:.2f}")

    print("\nPer instrument:")
    for inst, vals in by_instrument.items():
        inst_total = sum(vals)
        inst_avg = inst_total / len(vals)
        print(f"  {inst}: trades={len(vals)}, totalR={inst_total:.2f}, avgR={inst_avg:.2f}")


def main() -> None:
    load_dotenv()
    cfg = load_config()
    feed = DataFeed(DataFeedConfig(path_pattern=cfg.data.path_pattern))
    sc = cfg.strategy
    engine = StrategyEngine(
        config=StrategyConfig(
            risk_percent_default=sc.risk_percent_default,
            min_rr=sc.min_rr,
            atr_stop_multiplier=sc.atr_stop_multiplier,
        )
    )

    all_trades: List[BacktestTrade] = []

    for inst in cfg.instruments:
        try:
            trades = backtest_instrument(inst, feed, engine)
            all_trades.extend(trades)
        except FileNotFoundError:
            print(f"[{inst}] Missing data files; skipping.")

    summarise_portfolio(all_trades)


if __name__ == "__main__":
    main()
