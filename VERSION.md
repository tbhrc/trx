v1.2.3
Date: 2025-12-06 14:32 (UAE)

## Features Planned

This version will include:
- Phase 5: Performance Optimization (sentiment analysis caching, vectorization)
- Phase 6: Advanced Sentiment Features (NLP-based analysis)
- Additional enhancements TBD

## Previous Versions

### v1.2.2 (2025-12-06) - Dashboard Integration & Data Sources Research
- **Dashboard Integration**:
  - Updated dashboard to display `news_blocked` and `sentiment_score` fields
  - Added visual indicators (🟢/🔴 for news status, 📈/📉 for sentiment)
  - Footer updated to v1.2.1
  
- **Production Data Sources Research**:
  - Created comprehensive data sources guide (`docs/v1.2.2/data_sources_guide.md`)
  - Researched 6 production data sources (3 calendar, 3 headlines)
  - Documented pricing tiers: $0 (free), $50-100, $200-500, $1000+
  - Recommendations: ForexFactory + Alpha Vantage for free tier
  - Full implementation roadmap (MVP → Production → Enterprise)

**Files Modified**:
- `dashboard/index.html` - Added news filter field display

**Files Created**:
- `docs/v1.2.2/` - v1.2.2 documentation folder
- `docs/v1.2.2/data_sources_guide.md` - Comprehensive data sources research

---

### v1.2.1 (2025-12-06) - News & Economic Calendar Filter (Core Implementation)
- **NewsEngine**: Complete implementation with CSV-based calendar and headline loading
  - Event blocking logic (45 min before, 30 min after high-impact events)
  - Keyword-based sentiment analysis (-1.0 to +1.0 scoring)
  - Currency-to-instrument mapping (USD, EUR, GBP, XAU, BTC, NAS)
  - Risk reduction based on opposing sentiment

- **Configuration Support**:
  - Added `news` section to `config.yaml` with 7 configurable parameters
  - `NewsConfig` dataclass in `config.py`
  - Enable/disable toggle via `news.enabled` setting

- **Strategy Integration**:
  - Optional `NewsEngine` parameter in `StrategyEngine`
  - Signal filtering: blocks trades during high-impact events
  - Signal filtering: reduces risk when sentiment opposes direction
  - Added `news_blocked` and `sentiment_score` fields to `Signal` dataclass

- **API Integration**:
  - News filter exposed via `/config` endpoint
  - Signal responses include `news_blocked` and `sentiment_score` fields
  - Fully backward compatible (optional integration)

- **Sample Data**:
  - `data/economic_calendar.csv` with 21 high-impact events
  - `data/news_headlines.csv` with 28 sample headlines

- **Testing & Verification**:
  - 21 comprehensive unit tests (100% pass rate)
  - Test coverage: initialization, calendar loading, event blocking, sentiment analysis, risk reduction
  - Smoke test and backtest verified with news filter enabled
  - API endpoints tested and functional

**Files Modified/Created** (Core Implementation):
- `src/v1_0/core/news.py` (new, 184 lines)
- `src/v1_0/core/config.py` (+20 lines)
- `src/v1_0/core/strategy.py` (+27 lines)
- `config/config.yaml` (+9 lines)
- `src/v1_0/api/server.py` (+7 lines)
- `src/v1_0/api/schemas.py` (+4 lines)
- `smoke_test.py` (+12 lines)
- `backtest_example.py` (+14 lines)
- `src/__init__.py` (new)
- `src/v1_0/__init__.py` (new)

**Data Files**:
- `data/economic_calendar.csv` (new)
- `data/news_headlines.csv` (new)

**Testing**:
- `src/v1_0/tests/test_news.py` (new, 21 test cases, 320 lines)

---

### v1.2.0 (2025-12-06) - Developer Framework Documentation
- Added developer framework docs (`MASTER_PROMPT_AI_DEV`, `DEVELOPER_CONTRACT`, `dev_contract`)
- Added `docs/rfcs/` folder for future design notes

---

### v1.0.0 - Initial Release
- Core strategy engine with rule-based trading logic
- Risk management and money management
- FastAPI server with signal endpoints
- MT4/MT5 integration architecture
