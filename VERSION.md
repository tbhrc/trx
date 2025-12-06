v1.2.4
Date: 2025-12-06 15:06 (UAE)

## Features Planned

This version will include:
- Phase 1: Enhanced Signal Dashboard with modern UI
- Real-time auto-refresh (10s interval)
- Sentiment visualizations and gauges
- Signal strength indicators
- Responsive grid layout
- Professional trading interface

## Previous Versions

### v1.2.3 (2025-12-06) - Performance Optimization & Advanced Sentiment

**Phase 5: Performance Optimization** ✅
- **LRU Caching**: Added `@lru_cache(maxsize=1000)` for sentiment scores
  - Hourly granularity cache keys
  - 85x speedup vs v1.2.1 (50ms → 0.59ms)
  - Clear cache method added
  
- **Vectorized Keyword Matching**: Numpy + regex implementation
  - Pre-compiled regex patterns
  - Batch processing with pandas `.str` methods
  - 5-10x speedup on large datasets
  
- **Instrument Indexing**: Pre-index headlines by instrument
  - O(1) lookup via `Dict[str, DataFrame]`
  - 25,000x speedup (10ms → 0.39μs)
  - Minimal memory overhead (+10%)
  
- **Headline Expiration**: Configurable data cleanup
  - New config parameter: `headline_expiration_days` (default: 7)
  - Automatic filtering during load
  - Reduced memory footprint
  
- **Lazy Loading**: Load data only when `enabled=True`
  - Faster initialization when disabled
  - No file I/O overhead

**Phase 6: Advanced Sentiment Features** ✅ (Partial)
- **Sentiment Trend Analysis**: New `get_sentiment_trend()` method
  - Returns hourly sentiment time-series
  - Leverages caching for performance
  - Use case: Detect sentiment shifts over 24 hours
  
- **Deferred Features**:
  - NLP sentiment (FinBERT) - heavy dependencies
  - Source weighting - needs CSV schema update

**Performance Benchmarking** ✅
- Created `scripts/benchmark_news.py` - Comprehensive benchmark suite
- Tested with up to 2000 headlines
- Results documented in `docs/v1.2.3/benchmark_results.md`
- Key findings:
  - <1ms per query with 1000+ headlines
  - Linear scaling confirmed
  - Cache overhead > benefit for small datasets (keep for future NLP)

**Testing** ✅
- All 21 unit tests passing
- Fixed `headline_expiration_days=0` in tests for old data compatibility
- Test runtime: 1.50s (down from 2.01s)
- Deprecated warnings fixed (`'H'` → `'h'`)

**Files Modified**:
- `src/v1_0/core/news.py` (+80 lines, optimizations)
- `src/v1_0/core/config.py` - Updated NewsConfig
- `src/v1_0/tests/test_news.py` - Fixed fixtures

**Files Created**:
- `scripts/benchmark_news.py` (430 lines) - Performance benchmark suite
- `docs/v1.2.3/benchmark_results.md` - Benchmark analysis and recommendations
- `docs/v1.2.3/README.md` - Version overview

---

### v1.2.2 (2025-12-06) - Dashboard Integration & Data Sources Research

**Dashboard Integration** ✅
- Updated `dashboard/index.html` to display news filter fields
- Added visual indicators:
  - 🟢/🔴 for news status (Clear/Blocked)
  - 📈/📉 for sentiment direction
- Updated footer to v1.2.1
- Browser verification successful

**Production Data Sources Research** ✅
- Created `docs/v1.2.2/data_sources_guide.md` (comprehensive guide)
- Researched 6 data sources:
  - **Economic Calendars**: ForexFactory, Investing.com, Trading Economics
  - **News Headlines**: NewsAPI, Alpha Vantage, Finnhub
- Documented pricing tiers: $0, $50-100, $200-500, $1000+
- Budget-tiered recommendations
- Implementation roadmap (MVP → Production → Enterprise)

**Data Ingestion Scripts** ✅
- Created `scripts/fetch_calendar.py` (280 lines) - ForexFactory scraper
- Created `scripts/fetch_headlines.py` (330 lines) - Alpha Vantage/Finnhub fetcher
- Created `scripts/README.md` (400+ lines) - Comprehensive documentation
- Features:
  - Respectful rate limiting
  - Environment variable API key management
  - Automatic instrument mapping
  - CSV output compatible with existing format
  - Duplicate filtering
- Scheduling guides for Windows (Task Scheduler) and Linux (cron)
- Security best practices documented

**Files Modified**:
- `dashboard/index.html` - News filter display

**Files Created**:
- `docs/v1.2.2/data_sources_guide.md`
- `scripts/fetch_calendar.py`
- `scripts/fetch_headlines.py`
- `scripts/README.md`

---

### v1.2.1 (2025-12-06) - News & Economic Calendar Filter (Core Implementation)

[Content remains the same as before...]

---

### v1.2.0 (2025-12-06) - Developer Framework Documentation

[Content remains the same as before...]

---

### v1.0.0 - Initial Release
- Core strategy engine with rule-based trading logic
- Risk management and money management
- FastAPI server with signal endpoints
- MT4/MT5 integration architecture
