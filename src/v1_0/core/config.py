"""Configuration loader for AI Trading Copilot v1.0.

This module centralises loading of YAML configuration and environment
variables so other modules can depend on a simple, typed interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import os
import yaml


CONFIG_PATH = os.getenv("AIC_CONFIG_PATH", "config/config.yaml")


@dataclass
class DataConfig:
    path_pattern: str


@dataclass
class StrategyConfigValues:
    risk_percent_default: float
    min_rr: float
    atr_stop_multiplier: float


@dataclass
class AppConfig:
    instruments: List[str]
    data: DataConfig
    strategy: StrategyConfigValues


def load_config(path: str | None = None) -> AppConfig:
    """Load configuration from YAML file.

    Environment variable AIC_CONFIG_PATH can override the default path.
    """
    cfg_path = Path(path or CONFIG_PATH)
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")

    with cfg_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    instruments = [s.upper() for s in (raw.get("instruments") or [])]

    data_cfg = raw.get("data") or {}
    strategy_cfg = raw.get("strategy") or {}

    data = DataConfig(
        path_pattern=data_cfg.get("path_pattern", "data/{symbol}_{timeframe}.csv"),
    )

    strategy = StrategyConfigValues(
        risk_percent_default=float(strategy_cfg.get("risk_percent_default", 0.75)),
        min_rr=float(strategy_cfg.get("min_rr", 2.0)),
        atr_stop_multiplier=float(strategy_cfg.get("atr_stop_multiplier", 1.25)),
    )

    return AppConfig(
        instruments=instruments,
        data=data,
        strategy=strategy,
    )
