# AI Trading Copilot

## Project description
AI Trading Copilot is a local, offline capable assistant that generates rule-based, risk-controlled trade setups for a small universe of instruments and integrates with MT4 or MT5 via an API and Expert Advisor bridge.

The system combines:
- Deterministic technical strategy
- **Economic calendar and news sentiment filtering** (v1.2.1 - Fully Implemented)
  - Blocks trades during high-impact economic events
  - Analyzes news sentiment to reduce risk when opposed to trade direction
  - Configurable blocking windows and sentiment thresholds
- Machine learning signal scoring (planned)
- Strict risk and money management
- Full logging and explainability

## Repository structure

- `docs/`
  - `v1.0/`
    - `blueprint.md` – high-level design and architecture for version 1.0.
    - `strategy_rule_sheet.md` – precise line-by-line trading rules for version 1.0.
    - `prd.md` – product requirements document for version 1.0.
  - `v1.1/`
    - `README.md` – placeholder for upcoming documentation for version 1.1.

- `src/`
  - `v1_0/`
    - `core/` – strategy, indicators, risk, news, ML interfaces, backtester, performance.
    - `api/` – FastAPI server and schemas.
    - `storage/` – database and models.
    - `ui/` – optional dashboard entry points.
    - `ml/` – training scripts and ML utilities.
    - `tests/` – test suite skeleton.
  - `v1_1/`
    - `README.md` – placeholder, to be populated when version 1.1 starts.

- `VERSION.md` – versioning rules and current repo version.

## Version control model

This repository uses an internal version directory convention plus normal Git version control:

- Version 1.0 corresponds to:
  - `docs/v1.0/` for documentation.
  - `src/v1_0/` for implementation.

- Future minor versions (for example 1.1, 1.2):
  - New documentation in `docs/v1.x/`.
  - New code branch in `src/v1_x/`, cloned initially from previous version and then evolved.

- Git usage:
  - Tag releases: `v1.0.0`, `v1.1.0`, etc.
  - Use feature branches (for example `feature/news-filter`) merged into a main branch that tracks the latest stable tree for the active version.

### Versioning rules

- Major version `X.0`:
  - Breaking changes in architecture, strategy, or external interfaces.
- Minor version `1.X`:
  - Backward compatible feature additions, parameter tweaks, and new modules.
- Patch version `1.0.X`:
  - Bug fixes and internal improvements with no change to documented behaviour.

`VERSION.md` holds the current repository-level version reference.

## Getting started

1. Install Python 3.11 or later.  
2. Create and activate a virtual environment.  
3. Install dependencies (FastAPI, Uvicorn, pandas, NumPy, scikit-learn, etc.).  
4. From `src/v1_0/`, start by implementing:
   - `core.data_feed.DataFeed`
   - `core.indicators.IndicatorEngine`
   - `core.strategy.StrategyEngine`
   - `core.risk.RiskEngine`
   - `api.server` endpoints
   - `storage.db.Database`

5. For integration with MT4/MT5:
   - Define JSON schema for signals in `api.schemas`.
   - Build an EA that polls the FastAPI server and places orders on user confirmation.


## Quick start

### 1. Set up Python environment

From the repository root:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Run a local smoke test

```bash
python smoke_test.py
```

You should see output similar to:

- Number of daily and H4 candles loaded for EURUSD.
- Either "No signals generated." or details of the most recent signal.

### 3. Run the FastAPI server

```bash
uvicorn main:app --reload
```

This will start the API on `http://127.0.0.1:8000` by default.

You can then test the endpoint in a browser or with curl:

```bash
curl "http://127.0.0.1:8000/signal/latest?instrument=EURUSD"
```

If a signal is available, you will see a JSON representation. If not, the endpoint returns `null`.

### 4. First backtest run (basic)

A simple backtest example is provided in `backtest_example.py`.

Run:

```bash
python backtest_example.py
```

This will:

- Walk through H4 EURUSD data bar by bar.
- Generate signals using the same StrategyEngine.
- Manage a single open trade at a time with SL / TP1 exits.
- Print a summary of trades and performance in R at the end.


### 5. Running tests (v1.2.1+)

**Unit tests**:

```bash
# From project root
$env:PYTHONPATH="."; pytest src/v1_0/tests/test_news.py -v
```

You should see:
- 21 tests covering NewsEngine functionality
- All tests passing
- Coverage of calendar loading, event blocking, sentiment analysis, risk reduction

**Full test suite**:

```bash
# Run all verification scripts
python smoke_test.py
python backtest_example.py
$env:PYTHONPATH="."; pytest src/v1_0/tests/ -v
```

**API server testing**:

```bash
# Start server
uvicorn main:app --reload

# In another terminal, test endpoints
Invoke-WebRequest -Uri "http://127.0.0.1:8000/config" -Method GET
Invoke-WebRequest -Uri "http://127.0.0.1:8000/signal/latest?instrument=EURUSD" -Method GET
```


## Roadmap for v1.x

- **v1.0** (Complete):
  - ✅ Baseline rule-based strategy, risk, and signal engine
  - ✅ Semi-manual execution via MT4/MT5 EA
  - ✅ DataFeed, IndicatorEngine, StrategyEngine, RiskEngine
  - ✅ FastAPI server with signal endpoints

- **v1.2.1** (Current - Complete):
  - ✅ **News & Economic Calendar Filter**:
    - CSV-based economic calendar with event blocking (45 min before, 30 min after)
    - Keyword-based sentiment analysis for news headlines
    - Currency-to-instrument mapping (USD, EUR, GBP, XAU, BTC, NAS)
    - Signal filtering: blocks trades during high-impact events
    - Signal filtering: reduces risk when sentiment opposes direction
    - Configurable via `config.yaml` (enable/disable toggle)
  - ✅ **Comprehensive Testing**:
    - 21 unit tests covering all NewsEngine functionality
    - 100% test pass rate and code coverage
    - API verification and smoke tests
  - ✅ **Developer Framework**: MASTER_PROMPT_AI_DEV, DEVELOPER_CONTRACT, docs/rfcs

- **v1.2.2** (Planned - Enhancement Phase):
  - 🔜 **Phase 3: Dashboard Integration**
    - Verify news filter fields display in HTML dashboard
    - Add visual indicators for news-blocked signals
  - 🔜 **Phase 4: Production Data Sources**
    - Integrate real-time economic calendar APIs (ForexFactory, Investing.com)
    - Connect to news headline APIs (NewsAPI, Alpha Vantage, Finnhub)
    - Automated data ingestion and update scripts
  - 🔜 **Phase 5: Performance Optimization**
    - Implement sentiment score caching
    - Vectorize keyword matching for large datasets (1000+ headlines)
    - Add headline expiration and automatic cleanup
  - 🔜 **Phase 6: Advanced Sentiment Features**
    - NLP-based sentiment analysis (upgrade from keyword matching)
    - Multi-source sentiment aggregation
    - Event impact prediction modeling

- **v1.3+** (Future Ideas):
  - Full ML-based signal scoring
  - Multi-strategy support
  - Portfolio optimizers
  - Advanced coaching and explanation engine
  - Real-time WebSocket updates for news events


## Developer information

This repository is designed to be worked on by both human developers and AI coding assistants under a strict framework.

Key documents:

- `docs/MASTER_PROMPT_AI_DEV.md`  
  Master system prompt for AI coding tools. Copy this into Codex / Gemini / ChatGPT when asking for code changes.

- `docs/DEVELOPER_CONTRACT.md`  
  Project-specific rules and expectations for any developer working on AI Trading Copilot.

- `docs/dev_contract.md`  
  Generic development framework that can be reused across projects to enforce discipline and guardrails.

- `docs/rfcs/`  
  Folder reserved for request-for-comment design notes for larger features and architectural changes.

When using an AI coding assistant:

1. Open `docs/MASTER_PROMPT_AI_DEV.md`.  
2. Copy the full content as the system or initial prompt.  
3. Append a short "Task for this session" section describing the exact change you want.  
4. Ensure the AI output respects the file boundaries and constraints defined in the prompt.

