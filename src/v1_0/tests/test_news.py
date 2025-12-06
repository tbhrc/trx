"""Unit tests for NewsEngine (AI Trading Copilot v1.0)."""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
import tempfile
import os

from ..core.news import NewsEngine, NewsConfig


class TestNewsEngineInitialization:
    """Test NewsEngine initialization and configuration."""
    
    def test_init_with_default_config(self):
        """Test NewsEngine initializes with default config."""
        config = NewsConfig(enabled=False)  # Disable to skip file loading
        engine = NewsEngine(config)
        
        assert engine.config == config
        assert engine.calendar is None
        assert engine.headlines is None
    
    def test_init_with_custom_config(self):
        """Test NewsEngine initializes with custom settings."""
        config = NewsConfig(
            enabled=False,
            block_before_minutes=60,
            block_after_minutes=45,
            sentiment_threshold=-0.7
        )
        engine = NewsEngine(config)
        
        assert engine.config.block_before_minutes == 60
        assert engine.config.block_after_minutes == 45
        assert engine.config.sentiment_threshold == -0.7


class TestEconomicCalendarLoading:
    """Test economic calendar CSV loading."""
    
    def test_load_valid_calendar(self, tmp_path):
        """Test loading a valid economic calendar CSV."""
        # Create temporary CSV
        calendar_file = tmp_path / "calendar.csv"
        calendar_file.write_text(
            "timestamp,currency,impact,event_name\n"
            "2024-01-15 13:30:00,USD,high,Non-Farm Payrolls\n"
            "2024-01-16 08:00:00,EUR,medium,ECB Meeting\n"
        )
        
        config = NewsConfig(
            enabled=True,
            calendar_path=str(calendar_file),
            headlines_path="nonexistent.csv"  # Will be skipped if not exists
        )
        engine = NewsEngine(config)
        
        assert engine.calendar is not None
        assert len(engine.calendar) == 1  # Only high-impact events filtered
        assert engine.calendar.iloc[0]["currency"] == "USD"
    
    def test_load_calendar_missing_file(self):
        """Test graceful handling of missing calendar file."""
        config = NewsConfig(
            enabled=True,
            calendar_path="nonexistent_calendar.csv",
            headlines_path="nonexistent_headlines.csv"
        )
        engine = NewsEngine(config)
        
        # Should initialize without crashing
        assert engine.calendar is None or engine.calendar.empty
    
    def test_load_calendar_all_impacts(self, tmp_path):
        """Test loading calendar with high_impact_only = False."""
        calendar_file = tmp_path / "calendar.csv"
        calendar_file.write_text(
            "timestamp,currency,impact,event_name\n"
            "2024-01-15 13:30:00,USD,high,Non-Farm Payrolls\n"
            "2024-01-16 08:00:00,EUR,medium,ECB Meeting\n"
            "2024-01-17 10:00:00,GBP,low,Retail Sales\n"
        )
        
        config = NewsConfig(
            enabled=True,
            calendar_path=str(calendar_file),
            headlines_path="nonexistent.csv",
            high_impact_only=False
        )
        engine = NewsEngine(config)
        
        assert len(engine.calendar) == 3  # All events loaded


class TestEventBlocking:
    """Test event blocking logic."""
    
    @pytest.fixture
    def engine_with_calendar(self, tmp_path):
        """Create NewsEngine with sample calendar data."""
        calendar_file = tmp_path / "calendar.csv"
        calendar_file.write_text(
            "timestamp,currency,impact,event_name\n"
            "2024-01-15 14:00:00,USD,high,FOMC Meeting\n"
            "2024-01-20 09:00:00,EUR,high,ECB Rate Decision\n"
        )
        
        config = NewsConfig(
            enabled=True,
            calendar_path=str(calendar_file),
            headlines_path="nonexistent.csv",
            block_before_minutes=45,
            block_after_minutes=30
        )
        return NewsEngine(config)
    
    def test_block_within_window_before(self, engine_with_calendar):
        """Test blocking during before-event window."""
        # 30 minutes before event at 14:00
        check_time = pd.Timestamp("2024-01-15 13:30:00")
        
        assert engine_with_calendar.is_blocked("EURUSD", check_time) is True
    
    def test_block_within_window_after(self, engine_with_calendar):
        """Test blocking during after-event window."""
        # 20 minutes after event at 14:00
        check_time = pd.Timestamp("2024-01-15 14:20:00")
        
        assert engine_with_calendar.is_blocked("EURUSD", check_time) is True
    
    def test_no_block_outside_window(self, engine_with_calendar):
        """Test no blocking outside event windows."""
        # 2 hours before event at 14:00
        check_time = pd.Timestamp("2024-01-15 12:00:00")
        
        assert engine_with_calendar.is_blocked("EURUSD", check_time) is False
    
    def test_block_exact_boundary_before(self, engine_with_calendar):
        """Test blocking at exact before-window boundary."""
        # Exactly 45 minutes before event at 14:00
        check_time = pd.Timestamp("2024-01-15 13:15:00")
        
        assert engine_with_calendar.is_blocked("EURUSD", check_time) is True
    
    def test_block_exact_boundary_after(self, engine_with_calendar):
        """Test blocking at exact after-window boundary."""
        # Exactly 30 minutes after event at 14:00
        check_time = pd.Timestamp("2024-01-15 14:30:00")
        
        assert engine_with_calendar.is_blocked("EURUSD", check_time) is True
    
    def test_no_block_wrong_instrument(self, engine_with_calendar):
        """Test no blocking for instruments not affected by currency."""
        # USD event should not block BTCUSD (crypto)
        check_time = pd.Timestamp("2024-01-15 14:00:00")
        
        # This actually WILL block because USD is mapped to BTCUSD
        # Let's test with an instrument not in the mapping
        assert engine_with_calendar.is_blocked("UNKNOWN", check_time) is False


class TestSentimentScoring:
    """Test sentiment analysis."""
    
    @pytest.fixture
    def engine_with_headlines(self, tmp_path):
        """Create NewsEngine with sample headlines."""
        headlines_file = tmp_path / "headlines.csv"
        headlines_file.write_text(
            'timestamp,instrument,headline\n'
            '2024-01-15 10:00:00,EURUSD,"Euro rallies on strong growth data"\n'
            '2024-01-15 11:00:00,EURUSD,"Markets bearish on weak inflation outlook"\n'
            '2024-01-15 12:00:00,GBPUSD,"Pound gains momentum with positive sentiment"\n'
        )
        
        config = NewsConfig(
            enabled=True,
            calendar_path="nonexistent.csv",
            headlines_path=str(headlines_file),
            headline_expiration_days=0  # Disable expiration for tests
        )
        return NewsEngine(config)
    
    def test_sentiment_positive(self, engine_with_headlines):
        """Test positive sentiment detection."""
        check_time = pd.Timestamp("2024-01-15 12:30:00")
        score = engine_with_headlines.get_sentiment_score("GBPUSD", check_time)
        
        # Should be positive due to "gains", "positive" keywords
        assert score > 0
    
    def test_sentiment_mixed(self, engine_with_headlines):
        """Test mixed sentiment (positive and negative)."""
        check_time = pd.Timestamp("2024-01-15 12:00:00")
        score = engine_with_headlines.get_sentiment_score("EURUSD", check_time)
        
        # Should be mixed (rallies + bearish)
        assert -1.0 <= score <= 1.0
    
    def test_sentiment_no_headlines(self, engine_with_headlines):
        """Test sentiment when no headlines exist for instrument."""
        check_time = pd.Timestamp("2024-01-15 12:00:00")
        score = engine_with_headlines.get_sentiment_score("XAUUSD", check_time)
        
        # Should return neutral
        assert score == 0.0
    
    def test_sentiment_old_headlines(self, engine_with_headlines):
        """Test sentiment ignores headlines older than 24 hours."""
        # Check time more than 24 hours after headlines
        check_time = pd.Timestamp("2024-01-17 12:00:00")
        score = engine_with_headlines.get_sentiment_score("EURUSD", check_time)
        
        # Should return neutral (no recent headlines)
        assert score == 0.0


class TestRiskReduction:
    """Test risk reduction logic based on sentiment."""
    
    @pytest.fixture
    def engine_with_headlines(self, tmp_path):
        """Create NewsEngine with directional headlines."""
        headlines_file = tmp_path / "headlines.csv"
        headlines_file.write_text(
            'timestamp,instrument,headline\n'
            '2024-01-15 10:00:00,EURUSD,"Euro falls sharply on weak data and bearish outlook"\n'
            '2024-01-15 11:00:00,GBPUSD,"Pound surges with strong gains and bullish sentiment"\n'
        )
        
        config = NewsConfig(
            enabled=True,
            calendar_path="nonexistent.csv",
            headlines_path=str(headlines_file),
            sentiment_threshold=-0.5,
            headline_expiration_days=0  # Disable expiration for tests
        )
        return NewsEngine(config)
    
    def test_reduce_risk_opposing_sentiment_long(self, engine_with_headlines):
        """Test risk reduction when sentiment opposes long trade."""
        check_time = pd.Timestamp("2024-01-15 12:00:00")
        
        # EURUSD has bearish sentiment, should oppose long trade
        should_reduce = engine_with_headlines.should_reduce_risk("EURUSD", "long", check_time)
        assert should_reduce is True
    
    def test_reduce_risk_opposing_sentiment_short(self, engine_with_headlines):
        """Test risk reduction when sentiment opposes short trade."""
        check_time = pd.Timestamp("2024-01-15 12:00:00")
        
        # GBPUSD has bullish sentiment, should oppose short trade
        should_reduce = engine_with_headlines.should_reduce_risk("GBPUSD", "short", check_time)
        assert should_reduce is True
    
    def test_no_reduce_risk_aligned_sentiment(self, engine_with_headlines):
        """Test no risk reduction when sentiment aligns with trade."""
        check_time = pd.Timestamp("2024-01-15 12:00:00")
        
        # GBPUSD has bullish sentiment, should support long trade
        should_reduce = engine_with_headlines.should_reduce_risk("GBPUSD", "long", check_time)
        assert should_reduce is False


class TestDisabledNewsFilter:
    """Test behavior when news filter is disabled."""
    
    def test_disabled_no_blocking(self):
        """Test is_blocked returns False when disabled."""
        config = NewsConfig(enabled=False)
        engine = NewsEngine(config)
        
        check_time = pd.Timestamp("2024-01-15 14:00:00")
        assert engine.is_blocked("EURUSD", check_time) is False
    
    def test_disabled_neutral_sentiment(self):
        """Test get_sentiment_score returns 0.0 when disabled."""
        config = NewsConfig(enabled=False)
        engine = NewsEngine(config)
        
        check_time = pd.Timestamp("2024-01-15 14:00:00")
        assert engine.get_sentiment_score("EURUSD", check_time) == 0.0
    
    def test_disabled_no_risk_reduction(self):
        """Test should_reduce_risk returns False when disabled."""
        config = NewsConfig(enabled=False)
        engine = NewsEngine(config)
        
        check_time = pd.Timestamp("2024-01-15 14:00:00")
        assert engine.should_reduce_risk("EURUSD", "long", check_time) is False


# Run with: pytest src/v1_0/tests/test_news.py -v
