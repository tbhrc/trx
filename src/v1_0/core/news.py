"""News and economic calendar filtering for AI Trading Copilot v1.0.

This module provides event-based trade blocking and sentiment analysis
to avoid trading during high-impact economic releases.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import pandas as pd


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


class NewsEngine:
    """Economic calendar and sentiment filters."""
    
    def __init__(self, config: NewsConfig):
        """Initialize NewsEngine with configuration.
        
        Args:
            config: NewsConfig object with filter settings
        """
        self.config = config
        self.calendar: Optional[pd.DataFrame] = None
        self.headlines: Optional[pd.DataFrame] = None
        
        # Currency to instrument mapping
        self.currency_map = {
            "USD": ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "NAS100"],
            "EUR": ["EURUSD"],
            "GBP": ["GBPUSD"],
            "XAU": ["XAUUSD"],
            "BTC": ["BTCUSD"],
            "NAS": ["NAS100"],
        }
        
        # Sentiment keywords (simplified keyword-based scoring)
        self.positive_keywords = [
            "rally", "surge", "gains", "bullish", "optimistic", "growth",
            "strong", "rise", "upbeat", "positive", "boost"
        ]
        self.negative_keywords = [
            "fall", "decline", "drop", "bearish", "pessimistic", "weak",
            "downturn", "slump", "crash", "negative", "concern", "risk"
        ]
        
        if self.config.enabled:
            self._load_data()
    
    def _load_data(self):
        """Load economic calendar and news headlines from CSV files."""
        cal_path = Path(self.config.calendar_path)
        if cal_path.exists():
            self.calendar = pd.read_csv(cal_path, parse_dates=["timestamp"])
            if self.config.high_impact_only and "impact" in self.calendar.columns:
                self.calendar = self.calendar[
                    self.calendar["impact"].str.lower() == "high"
                ].copy()
        
        headlines_path = Path(self.config.headlines_path)
        if headlines_path.exists():
            self.headlines = pd.read_csv(headlines_path, parse_dates=["timestamp"])
    
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
        """Get sentiment score for instrument at given time.
        
        Uses simple keyword matching on headlines within the last 24 hours.
        
        Args:
            instrument: Trading instrument
            timestamp: Time to check
            
        Returns:
            Sentiment score between -1.0 (bearish) and +1.0 (bullish)
        """
        if not self.config.enabled or self.headlines is None or self.headlines.empty:
            return 0.0
        
        # Get headlines for this instrument from last 24 hours
        lookback = pd.Timedelta(hours=24)
        recent = self.headlines[
            (self.headlines["instrument"] == instrument) &
            (self.headlines["timestamp"] <= timestamp) &
            (self.headlines["timestamp"] >= timestamp - lookback)
        ]
        
        if recent.empty:
            return 0.0
        
        # Score based on keyword counts
        total_score = 0.0
        for _, row in recent.iterrows():
            headline = str(row.get("headline", "")).lower()
            
            pos_count = sum(1 for kw in self.positive_keywords if kw in headline)
            neg_count = sum(1 for kw in self.negative_keywords if kw in headline)
            
            if pos_count + neg_count > 0:
                total_score += (pos_count - neg_count) / (pos_count + neg_count)
        
        # Average and normalize
        if len(recent) > 0:
            return max(-1.0, min(1.0, total_score / len(recent)))
        
        return 0.0
    
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
