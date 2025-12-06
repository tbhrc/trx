"""FastAPI server for AI Trading Copilot v1.0.

This service exposes HTTP endpoints that allow clients to:

- Request the latest trading signal for a given instrument.
- View a simple HTML dashboard.
- Inspect the active configuration.
- Retrieve a simulated portfolio equity curve from the backtester.
"""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from ..core.data_feed import DataFeed, DataFeedConfig
from ..core.strategy import StrategyEngine, StrategyConfig
from ..core.config import load_config
from ..core.equity import compute_portfolio_equity_curve
from ..core.news import NewsEngine
from .schemas import SignalResponse


app = FastAPI(title="AI Trading Copilot v1.0")

# Load application config once on startup
APP_CONFIG = load_config()


def _build_data_feed() -> DataFeed:
    """Create a DataFeed instance, using config and env overrides.

    Environment variable:

        DATA_PATH_PATTERN: pattern like "data/{symbol}_{timeframe}.csv"

    If not set, the value from config.yaml is used.
    """
    pattern = os.getenv("DATA_PATH_PATTERN", APP_CONFIG.data.path_pattern)
    cfg = DataFeedConfig(path_pattern=pattern)
    return DataFeed(cfg)


def _build_strategy_engine() -> StrategyEngine:
    """Create StrategyEngine with parameters taken from YAML config."""
    sc = APP_CONFIG.strategy
    cfg = StrategyConfig(
        risk_percent_default=sc.risk_percent_default,
        min_rr=sc.min_rr,
        atr_stop_multiplier=sc.atr_stop_multiplier,
    )
    
    # Add news engine if enabled
    news_engine = None
    if APP_CONFIG.news.enabled:
        news_engine = NewsEngine(APP_CONFIG.news)
    
    return StrategyEngine(config=cfg, news_engine=news_engine)


# Global singletons for simplicity in v1.0
DATA_FEED = _build_data_feed()
STRATEGY_ENGINE = _build_strategy_engine()


@app.get("/signal/latest", response_model=Optional[SignalResponse])
def get_latest_signal(
    instrument: str = Query(..., description="Instrument symbol, e.g. EURUSD")
) -> Optional[SignalResponse]:
    """Return the most recent candidate signal for the given instrument.

    This endpoint:
    - Loads Daily and H4 data via DataFeed.
    - Runs StrategyEngine.generate_signals.
    - If signals exist, returns the last one as JSON.
    - If no signals exist, returns null (HTTP 200 with null body).
    """
    instrument = instrument.upper()

    try:
        df_daily = DATA_FEED.get_candles(instrument, "D")
        df_h4 = DATA_FEED.get_candles(instrument, "H4")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - generic safety net
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if df_daily.empty or df_h4.empty:
        return None

    signals = STRATEGY_ENGINE.generate_signals(instrument, df_daily, df_h4)
    if not signals:
        return None

    sig = signals[-1]
    return SignalResponse.from_domain(sig)


@app.get("/config")
def get_config() -> Dict[str, Any]:
    """Return the currently loaded YAML configuration as JSON."""
    return asdict(APP_CONFIG)


@app.get("/equity/portfolio")
def get_portfolio_equity_curve() -> List[Dict[str, Any]]:
    """Return a simulated portfolio equity curve based on backtest results.

    The curve is computed using the same config.yaml instruments and
    StrategyEngine parameters as the live pipeline.
    """
    try:
        points = compute_portfolio_equity_curve()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return points


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard() -> HTMLResponse:
    """Serve a minimal HTML dashboard that shows the latest signal per instrument."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[3]  # repo root
    html_path = root / "dashboard" / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=500, detail=f"Dashboard file not found: {html_path}")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"), status_code=200)
