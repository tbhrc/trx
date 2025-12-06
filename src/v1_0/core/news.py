"""News and economic calendar filtering for AI Trading Copilot v1.2.3.

This module provides event-based trade blocking and sentiment analysis
to avoid trading during high-impact economic releases.

Version 1.2.3 optimizations:
- LRU caching for sentiment scores
- Vectorized keyword matching with numpy
- Instrument-indexed headlines for O(1) lookup
- Headline expiration (>7 days)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict
from functools import lru_cache
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import re


@dataclass
class NewsConfig:
    """Configuration for news filtering."""
    enabled: bool = True
    calendar_path: str = "data/economic_calendar.csv"
    headlines_path: str = "data/news_headlines.csv"
    block_before_minutes: int = 45
    block_after_minutes: int = 30
    high_impact_only: bool = True
    sentiment_threshold: float = -0.5
    headline_expiration_days: int = 7  # Phase 5: Configurable expiration


class NewsEngine:
    """Economic calendar and sentiment filters with performance optimizations."""
    
    def __init__(self, config: NewsConfig):
        """Initialize NewsEngine with configuration.
        
        Args:
            config: NewsConfig object with filter settings
        """
        self.config = config
        self.calendar: Optional[pd.DataFrame] = None
        self.headlines: Optional[pd.DataFrame] = None
        self.headlines_by_instrument: Dict[str, pd.DataFrame] = {}  # Phase 5: Indexed headlines
        
        # Currency to instrument mapping
        self.currency_map = {
            "USD": ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "NAS100"],
            "EUR": ["EURUSD"],
            "GBP": ["GBPUSD"],
            "XAU": ["XAUUSD"],
            "BTC": ["BTCUSD"],
            "NAS": ["NAS100"],
        }
        
        # Sentiment keywords (vectorized in Phase 5)
        self.positive_keywords = [
            "rally", "surge", "gains", "bullish", "optimistic", "growth",
            "strong", "rise", "upbeat", "positive", "boost"
        ]
        self.negative_keywords = [
            "fall", "decline", "drop", "bearish", "pessimistic", "weak",
            "downturn", "slump", "crash", "negative", "concern", "risk"
        ]
        
        # Phase 5: Pre-compile regex patterns for vectorization
        self._positive_pattern = re.compile('|'.join(self.positive_keywords), re.IGNORECASE)
        self._negative_pattern = re.compile('|'.join(self.negative_keywords), re.IGNORECASE)
        
        # Phase 5: Lazy loading - only load if enabled
        if self.config.enabled:
            self._load_data()
    
    def _load_data(self):
        """Load economic calendar and news headlines from CSV files with optimizations."""
        # Load calendar
        cal_path = Path(self.config.calendar_path)
        if cal_path.exists():
            self.calendar = pd.read_csv(cal_path, parse_dates=["timestamp"])
            if self.config.high_impact_only and "impact" in self.calendar.columns:
                self.calendar = self.calendar[
                    self.calendar["impact"].str.lower() == "high"
                ].copy()
        
        # Load headlines with Phase 5 optimizations
        headlines_path = Path(self.config.headlines_path)
        if headlines_path.exists():
            self.headlines = pd.read_csv(headlines_path, parse_dates=["timestamp"])
            
            # Phase 5: Filter out headlines older than configured days
            expiration_days = getattr(self.config, 'headline_expiration_days', 7)
            if expiration_days > 0:  # 0 = no expiration
                cutoff_date = datetime.now() - timedelta(days=expiration_days)
                self.headlines = self.headlines[
                    self.headlines["timestamp"] >= cutoff_date
                ].copy()
            
            # Phase 5: Pre-index headlines by instrument for O(1) lookup
            if not self.headlines.empty:
                for instrument in self.headlines["instrument"].unique():
                    self.headlines_by_instrument[instrument] = self.headlines[
                        self.headlines["instrument"] == instrument
                    ].copy()
    
    def clear_cache(self):
        """Clear the sentiment score cache. Useful after data refresh."""
        self._get_sentiment_score_cached.cache_clear()
    
    def is_blocked(self, instrument: str, timestamp: pd.Timestamp) -> bool:
        """Check if trading is blocked for instrument at given time.
        
        Args:
            instrument: Trading instrument (e.g., "EURUSD")
            timestamp: Time to check
            
        Returns:
            True if trading should be blocked, False otherwise
        """
        if not self.config.enabled or self.calendar is None or self.calendar.empty:
            return False
        
        # Get relevant currencies for this instrument
        relevant_currencies = []
        for currency, instruments in self.currency_map.items():
            if instrument in instruments:
                relevant_currencies.append(currency)
        
        if not relevant_currencies:
            return False
        
        # Check if any events fall within blocking window
        for _, event in self.calendar.iterrows():
            if event["currency"] not in relevant_currencies:
                continue
            
            event_time = event["timestamp"]
            before_window = pd.Timedelta(minutes=self.config.block_before_minutes)
            after_window = pd.Timedelta(minutes=self.config.block_after_minutes)
            
            if event_time - before_window <= timestamp <= event_time + after_window:
                return True
        
        return False
    
    def get_sentiment_score(self, instrument: str, timestamp: pd.Timestamp) -> float:
        """Get sentiment score with LRU caching (Phase 5).
        
        Delegates to cached implementation for performance.
        
        Args:
            instrument: Trading instrument
            timestamp: Time to check
            
        Returns:
            Sentiment score between -1.0 (bearish) and +1.0 (bullish)
        """
        # Round timestamp to nearest hour for cache key
        timestamp_hour = timestamp.floor('h')
        return self._get_sentiment_score_cached(instrument, timestamp_hour, timestamp)
    
    @lru_cache(maxsize=1000)
    def _get_sentiment_score_cached(self, instrument: str, timestamp_hour: pd.Timestamp, timestamp: pd.Timestamp) -> float:
        """Cached sentiment score calculation with vectorized keyword matching (Phase 5).
        
        Args:
            instrument: Trading instrument
            timestamp_hour: Timestamp rounded to hour (cache key)
            timestamp: Actual timestamp for lookback
            
        Returns:
            Sentiment score between -1.0 (bearish) and +1.0 (bullish)
        """
        if not self.config.enabled or not self.headlines_by_instrument:
            return 0.0
        
        # Phase 5: Use pre-indexed headlines for O(1) lookup
        if instrument not in self.headlines_by_instrument:
            return 0.0
        
        instrument_headlines = self.headlines_by_instrument[instrument]
        
        # Get headlines from last 24 hours
        lookback = pd.Timedelta(hours=24)
        recent = instrument_headlines[
            (instrument_headlines["timestamp"] <= timestamp) &
            (instrument_headlines["timestamp"] >= timestamp - lookback)
        ]
        
        if recent.empty:
            return 0.0
        
        # Phase 5: Vectorized keyword matching with regex
        headlines_text = recent["headline"].str.lower().fillna('')
        
        # Count keyword occurrences using vectorized operations
        pos_counts = headlines_text.str.count(self._positive_pattern).values
        neg_counts = headlines_text.str.count(self._negative_pattern).values
        
        # Calculate scores
        total_keywords = pos_counts + neg_counts
        
        # Avoid division by zero
        scores = np.where(
            total_keywords > 0,
            (pos_counts - neg_counts) / total_keywords,
            0.0
        )
        
        # Average and normalize
        if len(scores) > 0:
            avg_score = np.mean(scores)
            return float(np.clip(avg_score, -1.0, 1.0))
        
        return 0.0
    
    def get_sentiment_trend(self, instrument: str, timestamp: pd.Timestamp, hours_back: int = 24) -> pd.Series:
        """Get sentiment score time series for trend analysis (Phase 6).
        
        Args:
            instrument: Trading instrument
            timestamp: Current timestamp
            hours_back: Number of hours to look back
            
        Returns:
            pandas Series with hourly sentiment scores indexed by timestamp
        """
        if not self.config.enabled or instrument not in self.headlines_by_instrument:
            return pd.Series(dtype=float)
        
        # Get hourly timestamps
        timestamps = pd.date_range(
            end=timestamp,
            periods=hours_back,
            freq='H'
        )
        
        # Calculate sentiment for each hour
        scores = {}
        for ts in timestamps:
            scores[ts] = self.get_sentiment_score(instrument, ts)
        
        return pd.Series(scores)
    
    def should_reduce_risk(
        self,
        instrument: str,
        direction: str,
        timestamp: pd.Timestamp
    ) -> bool:
        """Check if sentiment opposes the trade direction.
        
        Args:
            instrument: Trading instrument
            direction: "long" or "short"
            timestamp: Time to check
            
        Returns:
            True if sentiment significantly opposes direction
        """
        if not self.config.enabled:
            return False
        
        sentiment = self.get_sentiment_score(instrument, timestamp)
        
        # If sentiment opposes direction and exceeds threshold, reduce risk
        if direction.lower() == "long" and sentiment < self.config.sentiment_threshold:
            return True
        if direction.lower() == "short" and sentiment > -self.config.sentiment_threshold:
            return True
        
        return False
