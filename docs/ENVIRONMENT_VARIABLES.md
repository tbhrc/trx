# Environment Variables Configuration

## Overview

This project uses environment variables to securely manage API keys, credentials, and configuration settings.

## Files

- **`.env`** - Your actual credentials (DO NOT COMMIT)
- **`.env.example`** - Template with all available variables and documentation

## Quick Start

1. **Copy the example file**:
   ```bash
   cp .env.example .env
   ```

2. **Fill in your credentials** in `.env`

3. **Ensure `.env` is in `.gitignore`** (already configured)

## Required Credentials

### For Data Ingestion (v1.2.2)

#### Alpha Vantage API Key
- **Where**: [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
- **Plan**: Free (5 requests/min, 500/day)
- **Used by**: `scripts/fetch_headlines.py`
- **Variable**: `ALPHAVANTAGE_API_KEY`

#### Finnhub API Key  
- **Where**: [https://finnhub.io/register](https://finnhub.io/register)
- **Plan**: Free (60 requests/min)
- **Used by**: `scripts/fetch_headlines.py`
- **Variable**: `FINNHUB_API_KEY`

## Optional Credentials (Future Features)

### Email Alerts (v1.2.6)

**Gmail Example**:
1. Enable 2-factor authentication
2. Create app-specific password: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Set:
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   ```

### SMS Alerts (v1.2.6)

**Twilio**:
1. Sign up: [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Get credentials from console: [https://www.twilio.com/console](https://www.twilio.com/console)
3. Get a phone number
4. Set:
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxx
   TWILIO_AUTH_TOKEN=xxxxx
   TWILIO_PHONE_NUMBER=+1234567890
   ```

### Push Notifications (v1.2.6)

**Firebase**:
1. Create project: [https://console.firebase.google.com/](https://console.firebase.google.com/)
2. Enable Cloud Messaging
3. Download service account key (JSON)
4. Extract credentials to `.env`

### MT4/MT5 Integration (v1.2.7)

- No credentials needed if using ZMQ bridge
- MT4/MT5 login handled in Expert Advisor

## Loading Environment Variables

### Python (Recommended)

Install `python-dotenv`:
```bash
pip install python-dotenv
```

Load in your script:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file

api_key = os.getenv('ALPHAVANTAGE_API_KEY')
```

### Existing Scripts

The data ingestion scripts (`fetch_headlines.py`, `fetch_calendar.py`) already use `python-dotenv` and will automatically load `.env` if it exists.

## Security Best Practices

### DO ✅
- ✅ Keep `.env` in `.gitignore`
- ✅ Use app-specific passwords for email
- ✅ Rotate API keys periodically
- ✅ Use different keys for dev/staging/prod
- ✅ Set restrictive permissions: `chmod 600 .env` (Linux/Mac)

### DON'T ❌
- ❌ Commit `.env` to version control
- ❌ Share API keys in chat/email
- ❌ Use production keys in development
- ❌ Hardcode credentials in source code
- ❌ Upload `.env` to public repositories

## Troubleshooting

### Environment variables not loading

**Check**:
1. File is named exactly `.env` (with the dot)
2. File is in project root directory
3. `python-dotenv` is installed: `pip install python-dotenv`
4. Script calls `load_dotenv()` before accessing variables

### API key not working

**Check**:
1. No extra spaces before/after the key
2. Quotes not needed (unless key contains special chars)
3. Key is active (not revoked)
4. Rate limits not exceeded

## Environment Variables Reference

| Variable | Required | Used By | Default | Notes |
|----------|----------|---------|---------|-------|
| `ALPHAVANTAGE_API_KEY` | For headlines | fetch_headlines.py | - | Free tier: 5 req/min |
| `FINNHUB_API_KEY` | For headlines | fetch_headlines.py | - | Free tier: 60 req/min |
| `SMTP_*` | For email alerts | alert_manager.py | - | Gmail recommended |
| `TWILIO_*` | For SMS alerts | alert_manager.py | - | Optional |
| `FIREBASE_*` | For push alerts | alert_manager.py | - | Optional |
| `DATABASE_URL` | For history | signal_history.py | sqlite:///./data/signals.db | SQLite default |
| `LOG_LEVEL` | Optional | All | INFO | DEBUG, INFO, WARNING, ERROR |

## Example `.env` Files

### Minimal (Data ingestion only)
```env
ALPHAVANTAGE_API_KEY=YOUR_KEY_HERE
FINNHUB_API_KEY=YOUR_KEY_HERE
```

### Full (All features)
```env
# Data sources
ALPHAVANTAGE_API_KEY=YOUR_KEY_HERE
FINNHUB_API_KEY=YOUR_KEY_HERE

# Email alerts
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# SMS alerts
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+1234567890

# Application
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Additional Resources

- [12-Factor App: Config](https://12factor.net/config)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [Alpha Vantage Docs](https://www.alphavantage.co/documentation/)
- [Finnhub Docs](https://finnhub.io/docs/api)
