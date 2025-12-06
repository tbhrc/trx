v1.2.1
Date: 2025-12-06 14:10 (UAE)

## Features Added

### News & Economic Calendar Filter (Core Implementation)
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

### Documentation
- Added developer framework docs (`MASTER_PROMPT_AI_DEV`, `DEVELOPER_CONTRACT`, `dev_contract`)
- Added `docs/rfcs/` folder for future design notes
- Created `docs/v1.2.1/` with implementation plan and walkthrough

## Files Modified/Created

**Core Implementation** (8 files):
- `src/v1_0/core/news.py` (new, 184 lines)
- `src/v1_0/core/config.py` (+20 lines)
- `src/v1_0/core/strategy.py` (+27 lines)
- `config/config.yaml` (+9 lines)
- `src/v1_0/api/server.py` (+7 lines)
- `src/v1_0/api/schemas.py` (+4 lines)
- `smoke_test.py` (+12 lines)
- `backtest_example.py` (+14 lines)

**Data Files** (2 new):
- `data/economic_calendar.csv`
- `data/news_headlines.csv`

**Testing** (1 new):
- `src/v1_0/tests/test_news.py` (21 test cases, 320 lines)

**Package Structure** (2 new):
- `src/__init__.py`
- `src/v1_0/__init__.py`

## Roadmap - Future Enhancements (v1.2.2+)

### Phase 3: Dashboard Integration
- Verify news filter fields display in HTML dashboard
- Add visual indicators for news-blocked signals
- Browser console error validation

### Phase 4: Production Data Sources
- Integrate real-time economic calendar APIs (ForexFactory, Investing.com, Trading Economics)
- Connect to news headline APIs (NewsAPI, Alpha Vantage, Finnhub)
- Automated data ingestion scripts
- API rate limit management

### Phase 5: Performance Optimization
- Implement sentiment score caching for repeat queries
- Vectorize keyword matching using numpy for large datasets (1000+ headlines)
- Add headline expiration and automatic cleanup (remove >7 days old)
- Pre-index headlines by instrument for O(1) lookup

### Phase 6: Advanced Features
- NLP-based sentiment analysis (replace keyword matching)
- Multi-source sentiment aggregation
- Event impact prediction modeling
- Custom event definitions and blocking windows
- Real-time WebSocket updates for news events

## Version History
- v1.2.1 (2025-12-06): News & Economic Calendar Filter with comprehensive testing
- v1.2.0 (2025-12-06): Developer framework documentation
- v1.0.0: Initial release with core strategy engine
