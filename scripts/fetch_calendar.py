"""
ForexFactory Economic Calendar Scraper

This script scrapes economic calendar events from ForexFactory and saves them to CSV format.
Designed to run as a scheduled task (daily or weekly).

Author: AI Trading Copilot Team
Version: 1.0
Date: 2025-12-06
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import sys

# Configuration
OUTPUT_FILE = "data/economic_calendar.csv"
FOREXFACTORY_URL = "https://www.forexfactory.com/calendar.php"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REQUEST_DELAY = 2  # seconds between requests (be respectful)
HIGH_IMPACT_ONLY = True  # Set to False to include all impacts


def fetch_calendar_page(url: str, date_offset: int = 0) -> str:
    """
    Fetch calendar page HTML from ForexFactory.
    
    Args:
        url: Base URL
        date_offset: Number of days from today (0 = today, 1 = tomorrow, etc.)
    
    Returns:
        HTML content as string
    """
    headers = {"User-Agent": USER_AGENT}
    
    # Add date parameter if offset
    if date_offset > 0:
        target_date = datetime.now() + timedelta(days=date_offset)
        params = {"day": target_date.strftime("%b%d.%Y").lower()}
        response = requests.get(url, headers=headers, params=params, timeout=10)
    else:
        response = requests.get(url, headers=headers, timeout=10)
    
    response.raise_for_status()
    return response.text


def parse_calendar_html(html: str) -> list:
    """
    Parse ForexFactory calendar HTML and extract events.
    
    Args:
        html: HTML content
    
    Returns:
        List of event dictionaries
    """
    soup = BeautifulSoup(html, 'html.parser')
    events = []
    
    # Find calendar table
    calendar_table = soup.find('table', class_='calendar__table')
    if not calendar_table:
        print("Warning: Could not find calendar table in HTML")
        return events
    
    current_date = None
    
    # Iterate through rows
    for row in calendar_table.find_all('tr', class_='calendar__row'):
        # Check for date row
        date_cell = row.find('td', class_='calendar__cell calendar__date')
        if date_cell and date_cell.text.strip():
            current_date = date_cell.text.strip()
        
        # Extract event data
        time_cell = row.find('td', class_='calendar__time')
        currency_cell = row.find('td', class_='calendar__currency')
        impact_cell = row.find('td', class_='calendar__impact')
        event_cell = row.find('td', class_='calendar__event')
        
        if not all([time_cell, currency_cell, event_cell]):
            continue
        
        # Get impact level
        impact_span = impact_cell.find('span') if impact_cell else None
        impact = 'low'
        if impact_span:
            if 'icon--ff-impact-red' in impact_span.get('class', []):
                impact = 'high'
            elif 'icon--ff-impact-ora' in impact_span.get('class', []):
                impact = 'medium'
        
        # Filter by impact if configured
        if HIGH_IMPACT_ONLY and impact != 'high':
            continue
        
        # Extract data
        event_time = time_cell.text.strip()
        currency = currency_cell.text.strip()
        event_name = event_cell.text.strip()
        
        # Skip if missing critical data
        if not event_time or event_time == 'All Day' or not current_date:
            continue
        
        # Construct timestamp (simplified - assumes current year)
        try:
            year = datetime.now().year
            datetime_str = f"{year} {current_date} {event_time}"
            timestamp = datetime.strptime(datetime_str, "%Y %a%b %d %I:%M%p")
        except ValueError:
            print(f"Warning: Could not parse timestamp for {current_date} {event_time}")
            continue
        
        events.append({
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'currency': currency,
            'impact': impact,
            'event_name': event_name
        })
    
    return events


def scrape_calendar(days_ahead: int = 7) -> pd.DataFrame:
    """
    Scrape calendar events for multiple days.
    
    Args:
        days_ahead: Number of days to scrape (including today)
    
    Returns:
        DataFrame with all events
    """
    all_events = []
    
    for day_offset in range(days_ahead):
        print(f"Fetching events for day +{day_offset}...")
        
        try:
            html = fetch_calendar_page(FOREXFACTORY_URL, day_offset)
            events = parse_calendar_html(html)
            all_events.extend(events)
            print(f"  Found {len(events)} events")
            
            # Respectful delay between requests
            if day_offset < days_ahead - 1:
                time.sleep(REQUEST_DELAY)
                
        except Exception as e:
            print(f"  Error fetching day +{day_offset}: {e}")
            continue
    
    if not all_events:
        print("Warning: No events found")
        return pd.DataFrame(columns=['timestamp', 'currency', 'impact', 'event_name'])
    
    df = pd.DataFrame(all_events)
    df = df.drop_duplicates(subset=['timestamp', 'currency', 'event_name'])
    df = df.sort_values('timestamp')
    
    return df


def save_to_csv(df: pd.DataFrame, output_path: str):
    """
    Save events DataFrame to CSV file.
    
    Args:
        df: Events DataFrame
        output_path: Output CSV file path
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\nSaved {len(df)} events to {output_path}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("ForexFactory Economic Calendar Scraper")
    print("=" * 60)
    print(f"High Impact Only: {HIGH_IMPACT_ONLY}")
    print(f"Output File: {OUTPUT_FILE}")
    print()
    
    try:
        # Scrape calendar
        df = scrape_calendar(days_ahead=7)
        
        # Save to file
        save_to_csv(df, OUTPUT_FILE)
        
        # Print summary
        print("\nSummary:")
        print(f"  Total Events: {len(df)}")
        if len(df) > 0:
            print(f"  Date Range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            print(f"  Currencies: {', '.join(df['currency'].unique())}")
        
        print("\n✅ Success!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
