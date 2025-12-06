# Data Ingestion Scripts

This folder contains scripts for fetching production data from external sources.

## Scripts

### 1. `fetch_calendar.py` - Economic Calendar Scraper

Scrapes economic calendar events from ForexFactory.

**Features**:
- Fetches high-impact events for next 7 days
- Filters by impact level (configurable)
- Saves to `data/economic_calendar.csv`
- Respectful rate limiting (2-second delay between requests)

**Requirements**:
```bash
pip install requests beautifulsoup4 pandas
```

**Usage**:
```bash
python scripts/fetch_calendar.py
```

**Configuration** (edit script):
- `HIGH_IMPACT_ONLY = True/False` - Filter high-impact events only
- `OUTPUT_FILE` - Output CSV path
- `REQUEST_DELAY` - Seconds between requests

**Output Format**:
```csv
timestamp,currency,impact,event_name
2024-01-15 13:30:00,USD,high,Non-Farm Payrolls
```

---

### 2. `fetch_headlines.py` - News Headlines Fetcher

Fetches financial news headlines from Alpha Vantage or Finnhub APIs.

**Features**:
- Supports Alpha Vantage and Finnhub
- Maps headlines to instruments automatically
- Saves to `data/news_headlines.csv`
- Filters duplicates

**Requirements**:
```bash
pip install requests pandas
```

**API Keys** (set environment variables):
```bash
# Alpha Vantage (free: 25 news requests/day)
export ALPHAVANTAGE_API_KEY="your_key_here"

# Or Finnhub (free: 60 calls/minute)
export FINNHUB_API_KEY="your_key_here"
```

**Sign up for free keys**:
- Alpha Vantage: https://www.alphavantage.co/support/#api-key
- Finnhub: https://finnhub.io/register

**Usage**:
```bash
python scripts/fetch_headlines.py
```

**Configuration** (edit script):
- `API_SOURCE = "alphavantage"` or `"finnhub"` - Choose API
- `OUTPUT_FILE` - Output CSV path
- `INSTRUMENTS` - List of instruments to track

**Output Format**:
```csv
timestamp,instrument,headline
2024-01-15 10:00:00,EURUSD,"ECB signals dovish stance..."
```

---

## Scheduling

### Windows (Task Scheduler)

**Method 1: Using Task Scheduler GUI**

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task → Name it "Fetch Calendar"
3. Trigger: Daily at 6:00 AM
4. Action: Start a Program
   - Program: `python`
   - Arguments: `c:\path\to\trx\scripts\fetch_calendar.py`
   - Start in: `c:\path\to\trx`
5. Finish and repeat for `fetch_headlines.py`

**Method 2: Using PowerShell**

```powershell
# Fetch Calendar (daily at 6 AM)
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts\fetch_calendar.py" -WorkingDirectory "c:\Users\TalentBridgeDubai\Documents\app-web-dev\trx"
$trigger = New-ScheduledTaskTrigger -Daily -At 6am
Register-ScheduledTask -TaskName "TRX-FetchCalendar" -Action $action -Trigger $trigger -Description "Fetch economic calendar data"

# Fetch Headlines (every 6 hours)
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts\fetch_headlines.py" -WorkingDirectory "c:\Users\TalentBridgeDubai\Documents\app-web-dev\trx"
$trigger = New-ScheduledTaskTrigger -Once -At 12am -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration (New-TimeSpan -Days 9999)
Register-ScheduledTask -TaskName "TRX-FetchHeadlines" -Action $action -Trigger $trigger -Description "Fetch news headlines"
```

---

### Linux/Mac (Cron)

Edit crontab: `crontab -e`

```bash
# Fetch calendar daily at 6 AM
0 6 * * * cd /path/to/trx && python scripts/fetch_calendar.py >> logs/fetch_calendar.log 2>&1

# Fetch headlines every 6 hours
0 */6 * * * cd /path/to/trx && python scripts/fetch_headlines.py >> logs/fetch_headlines.log 2>&1
```

**Cron schedule format**:
```
* * * * * command
│ │ │ │ │
│ │ │ │ └─ Day of week (0-7, Sun=0 or 7)
│ │ │ └─── Month (1-12)
│ │ └───── Day of month (1-31)
│ └─────── Hour (0-23)
└───────── Minute (0-59)
```

---

## Recommended Schedule

**Development/Testing**:
- Calendar: Daily at 6 AM
- Headlines: Every 6 hours

**Production**:
- Calendar: Daily at 5 AM (before market open)
- Headlines: Every 4 hours during market hours
- Weekend: Reduce to once daily

---

## Monitoring & Logs

**Create logs folder**:
```bash
mkdir logs
```

**Run with logging**:
```bash
python scripts/fetch_calendar.py >> logs/fetch_calendar.log 2>&1
python scripts/fetch_headlines.py >> logs/fetch_headlines.log 2>&1
```

**Check logs**:
```bash
# Windows
type logs\fetch_calendar.log

# Linux/Mac
cat logs/fetch_calendar.log
```

---

## Troubleshooting

### ForexFactory Scraper Issues

**Problem**: "Could not find calendar table"
- **Solution**: ForexFactory may have changed HTML structure. Inspect page and update CSS selectors.

**Problem**: Rate limiting / IP blocked
- **Solution**: Increase `REQUEST_DELAY`, use VPN, or scrape less frequently.

**Problem**: Invalid timestamps
- **Solution**: Check date parsing logic - ForexFactory format may vary by region.

### API Issues

**Problem**: "API key invalid"
- **Solution**: Verify environment variables are set correctly.

**Problem**: "Rate limit exceeded"
- **Solution**: 
  - Alpha Vantage: Reduce frequency, upgrade to Premium ($49.99/mo)
  - Finnhub: Check free tier limits (60 calls/min)

**Problem**: Empty results
- **Solution**: Check API status, verify topics/categories, check date filters.

---

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Store keys in** `.env` file (add to `.gitignore`)
4. **Rotate keys** periodically
5. **Monitor API usage** to detect unauthorized access

**Example `.env` file**:
```
ALPHAVANTAGE_API_KEY=your_actual_key_here
FINNHUB_API_KEY=your_actual_key_here
```

**Load with python-dotenv**:
```python
from dotenv import load_dotenv
load_dotenv()  # Loads .env file
```

---

## Next Steps

1. **Test scripts manually** to verify they work
2. **Set up scheduling** based on your OS
3. **Monitor first few runs** to catch issues
4. **Adjust frequency** based on API limits and data freshness needs
5. **Consider upgrading** to paid APIs for production use

For more information, see [docs/v1.2.2/data_sources_guide.md](file:///c:/Users/TalentBridgeDubai/Documents/app-web-dev/trx/docs/v1.2.2/data_sources_guide.md)
