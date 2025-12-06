"""
News Headlines Fetcher (Alpha Vantage / Finnhub)

This script fetches financial news headlines from Alpha Vantage or Finnhub APIs
and saves them to CSV format. Designed to run as a scheduled task.

Author: AI Trading Copilot Team
Version: 1.0
Date: 2025-12-06
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from typing import List, Dict

# Configuration
OUTPUT_FILE = "data/news_headlines.csv"
API_SOURCE = "alphavantage"  # Options: "alphavantage" or "finnhub"

# API Keys (set via environment variables for security)
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "demo")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

# Instruments to track
INSTRUMENTS = ["EURUSD", "GBPUSD", "XAUUSD", "BTCUSD", "NAS100"]

# Currency keywords for mapping
CURRENCY_KEYWORDS = {
    "EURUSD": ["EUR", "euro", "eurozone", "ECB"],
    "GBPUSD": ["GBP", "pound", "sterling", "UK", "Britain"],
    "XAUUSD": ["gold", "XAU", "precious metals"],
    "BTCUSD": ["bitcoin", "BTC", "crypto", "cryptocurrency"],
    "NAS100": ["nasdaq", "tech stocks", "technology"]
}


def fetch_alphavantage_news(topics: List[str] = None, limit: int = 50) -> List[Dict]:
    """
    Fetch news from Alpha Vantage News Sentiment API.
    
    Args:
        topics: List of topics/tickers (e.g., ["FOREX:EUR", "CRYPTO:BTC"])
        limit: Maximum number of articles
    
    Returns:
        List of article dictionaries
    """
    if not ALPHAVANTAGE_API_KEY or ALPHAVANTAGE_API_KEY == "demo":
        print("Warning: Using demo API key. Set ALPHAVANTAGE_API_KEY environment variable.")
    
    url = "https://www.alphavantage.co/query"
    
    # Default topics if none provided
    if not topics:
        topics = ["FOREX:EUR", "FOREX:GBP", "CRYPTO:BTC"]
    
    all_articles = []
    
    for topic in topics:
        print(f"Fetching news for {topic}...")
        
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": topic,
            "limit": limit,
            "apikey": ALPHAVANTAGE_API_KEY
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "feed" in data:
                articles = data["feed"]
                print(f"  Found {len(articles)} articles")
                all_articles.extend(articles)
            else:
                print(f"  No articles found or API error: {data.get('Note', 'Unknown error')}")
                
        except Exception as e:
            print(f"  Error fetching {topic}: {e}")
            continue
    
    return all_articles


def fetch_finnhub_news(category: str = "forex", days_back: int = 7) -> List[Dict]:
    """
    Fetch news from Finnhub Market News API.
    
    Args:
        category: News category ("general", "forex", "crypto", "merger")
        days_back: Number of days to fetch
    
    Returns:
        List of article dictionaries
    """
    if not FINNHUB_API_KEY:
        print("Error: FINNHUB_API_KEY environment variable not set")
        return []
    
    url = "https://finnhub.io/api/v1/news"
    
    params = {
        "category": category,
        "token": FINNHUB_API_KEY
    }
    
    print(f"Fetching {category} news from Finnhub...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        articles = response.json()
        
        # Filter by date
        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_timestamp = cutoff_date.timestamp()
        
        filtered_articles = [
            a for a in articles 
            if a.get('datetime', 0) >= cutoff_timestamp
        ]
        
        print(f"  Found {len(filtered_articles)} recent articles")
        return filtered_articles
        
    except Exception as e:
        print(f"  Error: {e}")
        return []


def map_article_to_instrument(headline: str) -> str:
    """
    Map article headline to instrument based on keywords.
    
    Args:
        headline: Article headline text
    
    Returns:
        Instrument symbol or "UNKNOWN"
    """
    headline_lower = headline.lower()
    
    for instrument, keywords in CURRENCY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in headline_lower:
                return instrument
    
    return "UNKNOWN"


def parse_alphavantage_articles(articles: List[Dict]) -> pd.DataFrame:
    """
    Parse Alpha Vantage articles into DataFrame format.
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        DataFrame with parsed headlines
    """
    parsed = []
    
    for article in articles:
        timestamp = article.get('time_published', '')
        headline = article.get('title', '')
        
        if not timestamp or not headline:
            continue
        
        # Parse timestamp (format: YYYYMMDDTHHMISS)
        try:
            dt = datetime.strptime(timestamp, '%Y%m%dT%H%M%S')
            timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue
        
        # Map to instrument
        instrument = map_article_to_instrument(headline)
        
        if instrument != "UNKNOWN":
            parsed.append({
                'timestamp': timestamp_str,
                'instrument': instrument,
                'headline': headline
            })
    
    return pd.DataFrame(parsed)


def parse_finnhub_articles(articles: List[Dict]) -> pd.DataFrame:
    """
    Parse Finnhub articles into DataFrame format.
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        DataFrame with parsed headlines
    """
    parsed = []
    
    for article in articles:
        timestamp = article.get('datetime', 0)
        headline = article.get('headline', '')
        
        if not timestamp or not headline:
            continue
        
        # Convert Unix timestamp to datetime
        dt = datetime.fromtimestamp(timestamp)
        timestamp_str = dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # Map to instrument
        instrument = map_article_to_instrument(headline)
        
        if instrument != "UNKNOWN":
            parsed.append({
                'timestamp': timestamp_str,
                'instrument': instrument,
                'headline': headline
            })
    
    return pd.DataFrame(parsed)


def save_to_csv(df: pd.DataFrame, output_path: str):
    """
    Save headlines DataFrame to CSV file.
    
    Args:
        df: Headlines DataFrame
        output_path: Output CSV file path
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df)} headlines to {output_path}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("News Headlines Fetcher")
    print("=" * 60)
    print(f"API Source: {API_SOURCE}")
    print(f"Output File: {OUTPUT_FILE}")
    print()
    
    try:
        # Fetch news based on selected source
        if API_SOURCE == "alphavantage":
            topics = ["FOREX:EUR", "FOREX:GBP", "CRYPTO:BTC"]
            articles = fetch_alphavantage_news(topics, limit=50)
            df = parse_alphavantage_articles(articles)
            
        elif API_SOURCE == "finnhub":
            # Fetch multiple categories
            forex_news = fetch_finnhub_news("forex", days_back=7)
            crypto_news = fetch_finnhub_news("crypto", days_back=7)
            all_articles = forex_news + crypto_news
            df = parse_finnhub_articles(all_articles)
            
        else:
            print(f"Error: Unknown API source '{API_SOURCE}'")
            return 1
        
        if df.empty:
            print("Warning: No headlines found")
            return 1
        
        # Remove duplicates and sort
        df = df.drop_duplicates(subset=['timestamp', 'headline'])
        df = df.sort_values('timestamp', ascending=False)
        
        # Save to file
        save_to_csv(df, OUTPUT_FILE)
        
        # Print summary
        print("\nSummary:")
        print(f"  Total Headlines: {len(df)}")
        if len(df) > 0:
            print(f"  Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            print(f"  Instruments: {', '.join(df['instrument'].unique())}")
            print("\n  Count by Instrument:")
            for instrument, count in df['instrument'].value_counts().items():
                print(f"    {instrument}: {count}")
        
        print("\n✅ Success!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
