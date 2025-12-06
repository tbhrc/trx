# Production Data Sources Guide - AI Trading Copilot v1.2.2

## Overview

This document provides comprehensive research and recommendations for replacing sample CSV data with real-time production data sources for the News & Economic Calendar Filter feature.

---

## Economic Calendar Data Sources

### 1. ForexFactory ⭐ Recommended for Free

**Type**: Web scraping (no official API)  
**Cost**: Free  
**Reliability**: High (popular community source)

**Pros**:
- Completely free
- Comprehensive economic calendar
- High/medium/low impact indicators
- Historical event data available
- Wide coverage of global markets

**Cons**:
- No official API (requires scraping)
- Terms of Service may restrict automated access
- HTML structure changes can break scrapers
- No rate limiting guarantees

**Implementation**:
- Use `BeautifulSoup` or `requests-html` for scraping
- Target URL: `https://www.forexfactory.com/calendar.php`
- Parse event table: date, time, currency, impact,event name
- Update CSV daily or weekly

**Sample Code**:
```python
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_forexfactory():
    url = "https://www.forexfactory.com/calendar.php"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    events = []
    # Parse calendar table
    # ... implementation details
    
    df = pd.DataFrame(events)
    df.to_csv("data/economic_calendar.csv", index=False)
```

---

### 2. Investing.com

**Type**: Web scraping + Paid API  
**Cost**: Free (scraping) | Paid API ($X/month - contact for pricing)  
**Reliability**: Very High

**Free Option (Scraping)**:
**Pros**:
- Comprehensive calendar
- Multiple asset classes
- Historical data

**Cons**:
- Aggressive anti-bot measures
- Frequent site updates
- Legal gray area

**Paid API**:
**Pros**:
- Official support
- JSON/REST API
- Rate limits guaranteed
- Legal and reliable

**Cons**:
- Pricing not publicly listed (enterprise tier)
- Requires business license

**Recommendation**: Use scraping for testing, migrate to API for production if budget allows.

---

### 3. Trading Economics 💰 Premium Option

**Type**: Official REST API  
**Cost**: Starting at $199/month (Basic Plan)  
**Reliability**: Excellent (institutional grade)

**Plans**:
- **Basic** ($199/mo): 100K API calls/month
- **Professional** ($599/mo): 500K calls/month
- **Enterprise** (Custom pricing): Unlimited

**Pros**:
- Official API with SLA guarantees
- Extremely comprehensive (196 countries, 300K+ indicators)
- Historical data dating back decades
- Real-time updates
- Event impact ratings
- Forecast vs actual data
- JSON/CSV/XML formats

**Cons**:
- Expensive for individual traders
- Overkill for small projects

**API Example**:
```python
import requests

API_KEY = "your_key_here"
url = f"https://api.tradingeconomics.com/calendar?c={API_KEY}"

response = requests.get(url)
events = response.json()

# Convert to CSV format
df = pd.DataFrame(events)
df[['Date', 'Country', 'Category', 'Actual', 'Forecast']].to_csv('calendar.csv')
```

**Best For**: Professional/institutional use, funded projects

---

## News Headline Data Sources

###1. NewsAPI ⭐ Recommended for Prototyping

**Type**: Official REST API  
**Cost**: Free (Developer) | $449/month (Business)

**Free Tier**:
- 100 requests/day
- Up to 100 articles per request
- 1-month historical data
- Delayed by 24 hours

**Business Tier** ($449/mo):
- Unlimited requests
- Real-time articles
- Full historical archive
- Advanced search

**Pros**:
- Easy to use REST API
- Good coverage of financial news
- Keyword search + filters
- Source filtering (Bloomberg, Reuters, etc.)

**Cons**:
- Free tier is heavily limited
- 24-hour delay on free tier
- Business plan expensive

**API Example**:
```python
import requests

API_KEY = "your_newsapi_key"
url = "https://newsapi.org/v2/everything"

params = {
    "q": "EUR USD forex",
    "language": "en",
    "sortBy": "publishedAt",
    "apiKey": API_KEY
}

response = requests.get(url, params=params)
articles = response.json()['articles']

headlines = []
for article in articles:
    headlines.append({
        'timestamp': article['publishedAt'],
        'instrument': 'EURUSD',  # Map from keywords
        'headline': article['title']
    })

pd.DataFrame(headlines).to_csv('news_headlines.csv', index=False)
```

**Best For**: Development/testing, low-frequency updates

---

### 2. Alpha Vantage

**Type**: Official REST API  
**Cost**: Free (Premium: $49.99/month)

**Free Tier**:
- 25 requests/day (News Sentiment endpoint)
- 500 requests/day (standard endpoints)
- No cost, API key required

**Premium** ($49.99/mo):
- 75 requests/minute
- Real-time data
- Extended coverage

**Pros**:
- Very generous free tier
- Financial market focus
- Sentiment scores included
- Easy integration

**Cons**:
- Rate limits on free tier
- Limited news sources
- Not as comprehensive as NewsAPI

**API Example**:
```python
import requests

API_KEY = "your_alphavantage_key"
url = "https://www.alphavantage.co/query"

params = {
    "function": "NEWS_SENTIMENT",
    "tickers": "FOREX:EUR",
    "apikey": API_KEY
}

response = requests.get(url, params=params)
news = response.json()['feed']

# Extract headlines
headlines = []
for item in news:
    headlines.append({
        'timestamp': item['time_published'],
        'instrument': 'EURUSD',
        'headline': item['title']
    })
```

**Best For**: Free tier is excellent for individual use

---

### 3. Finnhub

**Type**: Official REST API  
**Cost**: Free | Pro ($59/mo) | Enterprise (custom)

**Free Tier**:
- 60 API calls/minute
- Company news endpoint
- Market news endpoint
- Real-time

**Pro Tier** ($59/mo):
- 300 calls/minute
- Premium data sources
- Historical news

**Pros**:
- Excellent free tier
- Real-time news
- Financial market focus
- WebSocket support

**Cons**:
- Limited to financial news
- Free tier has source restrictions

**API Example**:
```python
import requests

API_KEY = "your_finnhub_key"
url = "https://finnhub.io/api/v1/news"

params = {
    "category": "forex",
    "token": API_KEY
}

response = requests.get(url, params=params)
news = response.json()

headlines = []
for article in news:
    headlines.append({
        'timestamp': article['datetime'],
        'instrument': 'EURUSD',  # Parse from summary
        'headline': article['headline']
    })
```

**Best For**: Real-time financial news with generous free tier

---

## Recommendations by Use Case

### Hobbyist / Individual Trader (Free)
**Economic Calendar**: ForexFactory (scraping)  
**News Headlines**: Alpha Vantage or Finnhub (free tier)  
**Total Cost**: $0/month

### Small Team / Startup (Budget <$100/mo)
**Economic Calendar**: ForexFactory (scraping)  
**News Headlines**: Alpha Vantage Premium ($49.99/mo)  
**Total Cost**: ~$50/month

### Professional / Fund ed Project ($200-500/mo)
**Economic Calendar**: Trading Economics Basic ($199/mo)  
**News Headlines**: NewsAPI Business ($449/mo) OR Finnhub Pro ($59/mo)  
**Total Cost**: $258 - $648/month

### Enterprise / Institutional
**Economic Calendar**: Trading Economics Professional ($599/mo)  
**News Headlines**: NewsAPI Business ($449/mo) + custom feeds  
**Total Cost**: $1000+/month

---

## Implementation Strategy

### Phase 1: MVP (Free Tier)
1. Use ForexFactory scraping for economic calendar
2. Use Alpha Vantage or Finnhub free tier for headlines
3. Update data once daily (off-peak hours)
4. Store in existing CSV format
5. **Estimated effort**: 2-3 days development

### Phase 2: Production (Paid APIs)
1. Migrate to Trading Economics for calendar
2. Upgrade to Alpha Vantage Premium or NewsAPI Business
3. Implement real-time or hourly updates
4. Add error handling and fallbacks
5. **Estimated effort**: 1 week development + testing

### Phase 3: Enterprise (Full-Scale)
1. Multiple data source redundancy
2. WebSocket connections for real-time
3. Data validation and cross-checking
4. Historical data archiving
5. **Estimated effort**: 2-3 weeks development

---

## Legal & Compliance Notes

⚠️ **Important Considerations**:

1. **Web Scraping**: Check Terms of Service before scraping any site
   - ForexFactory ToS may prohibit automated access
   - Use respectful rate limiting (1 request per 5-10 seconds)
   - Add User-Agent header identifying your project

2. **API Usage**: Read API documentation carefully
   - Respect rate limits to avoid IP bans
   - Store API keys securely (use environment variables)
   - Never commit API keys to version control

3. **Data Licensing**: Some data sources have restrictions on:
   - Redistribution
   - Commercial use
   - Storage duration

4. **Attribution**: Some free services require attribution

---

## Next Steps

### Immediate Actions:
1. Sign up for free API keys:
   - NewsAPI: https://newsapi.org/register
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key
  - Finnhub: https://finnhub.io/register

2. Test API calls manually (curl or Postman)

3. Review current CSV format compatibility

### Development Tasks:
1. Create `scripts/fetch_calendar.py`
2. Create `scripts/fetch_headlines.py`
3. Add error handling and      logging
4. Schedule automated updates (cron/Task Scheduler)
5. Update documentation

---

## Conclusion

**Recommended Starting Point**:
- **Economic Calendar**: ForexFactory (scraping) - free, reliable
- **News Headlines**: Alpha Vantage (free tier) - 25 calls/day is sufficient for daily updates

**Upgrade Path When Ready**:
- Trading Economics ($199/mo) for institutional-grade calendar
- Alpha Vantage Premium ($49.99/mo) for increased headline volume

This provides a solid free foundation with a clear upgrade path as the project grows.
