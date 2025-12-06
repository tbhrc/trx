# AI Trading Copilot – Product Requirements Document (PRD)
Version: 1.0  
Date: 06 December 2025 (GST)

## 1. Overview

Build a local, offline capable AI Trading Copilot that:

- Generates high probability trade setups for a small universe of instruments.  
- Manages risk strictly through hard coded rules.  
- Uses news filtering and ML scoring to improve quality.  
- Integrates with MT4 or MT5 via a clean API and EA bridge.  
- Provides full transparency through logging and explanations.

## 2. Goals

2.1. Provide consistent, rule-based signals aligned with trend and structure.  
2.2. Reduce trader error by enforcing risk management and news filters.  
2.3. Use ML to filter and score setups, not to invent opaque strategies.  
2.4. Keep a human in the loop for final execution in v1.  
2.5. Create an extensible platform for future strategies and modules.

## 3. Non-Goals

3.1. High frequency trading or ultra-low latency execution.  
3.2. Scalping strategies below M15.  
3.3. Fully autonomous trading in v1.  
3.4. Cloud-hosted infrastructure; v1 is local by design.

## 4. Architecture

### 4.1 Components

- Core engine (Python):
  - Strategy, indicators, risk, news, ML, backtesting.  
- API layer (FastAPI):
  - Exposes signals, trades, and summaries to clients.  
- Database (SQLite):
  - Stores signals, trades, and metrics.  
- ML models:
  - Scoring models for trade quality.  
- EA bridge:
  - MT4/MT5 Expert Advisors that connect to the API.  
- Optional dashboard:
  - Web UI for monitoring and configuration.

### 4.2 Data flow

1. Market data ingested into core engine.  
2. Engine calculates indicators and checks for setups on bar close.  
3. News filter and ML model score any candidate trade.  
4. Valid signals are stored and exposed through API.  
5. EA polls API, displays signals, and upon user acceptance, places orders.  
6. EA sends trade results back to API for logging.  
7. Reporting layer aggregates and summarises performance.

## 5. Functional Requirements

5.1. Trend regime detection:

- Compute Daily 200 EMA and 50 EMA.  
- Classify each instrument as uptrend, downtrend, or sideways.  
- Restrict trade direction based on regime.

5.2. Setup detection on H4:

- Identify swing highs and lows.  
- Detect pullbacks into EMA zones.  
- Use RSI and ATR filters.  
- Detect reversal candles.

5.3. Signal generation:

- For each valid setup, generate a signal object with all required fields.  
- Enforce minimum R:R of at least 1:2.  
- Compute risk-aware position size parameters.

5.4. News filter:

- Integrate economic calendar.  
- Enforce pre- and post-event blackout windows.  
- Apply sentiment weighting to risk or signal acceptance.

5.5. ML scoring:

- Extract features per candidate trade.  
- Use a trained model to estimate probabilities of success.  
- Apply thresholds to accept or filter trades.

5.6. Risk control:

- Enforce per trade and portfolio risk limits.  
- Enforce daily loss limit.  
- Block signals that violate constraints.

5.7. EA and execution:

- Provide an API the EA can query.  
- Ensure EA can draw lines, show risk, and provide Accept or Reject controls.  
- Ensure EA validates broker constraints at execution time.

5.8. Logging and reporting:

- Log every signal and trade with all parameters.  
- Provide daily and weekly reports with key statistics.  

## 6. API Requirements

Minimum endpoints:

- `GET /signal/latest?instrument=SYMBOL`
  - Returns latest pending signal for the symbol.  

- `GET /signal/{id}`
  - Returns full details for a specific signal.  

- `POST /signal/{id}/status`
  - Body includes:
    - `status`: "accepted" or "rejected"  
    - `ticket`: broker order ticket id, if accepted  

- `POST /trade/log`
  - EA posts trade execution details and outcomes.  

- `GET /trade/history?instrument=&from=&to=`
  - Returns historical trade list and summary statistics.  

- `GET /system/summary`
  - Returns current equity, open risk, daily PnL and status flags.

## 7. Performance Requirements

7.1. Signal computation and ML scoring must complete within 1 second of bar close.  
7.2. API should support at least 10 requests per second from EA.  
7.3. Logging operations should not block signal generation.

## 8. Deployment Requirements

8.1. Must run on Windows 10 or later on consumer hardware.  
8.2. Must not require GPU acceleration.  
8.3. Must be able to run with limited internet access (local operation plus broker data).  
8.4. Installation should require only Python, dependencies, and configuration.

## 9. Testing and Validation

9.1. Unit tests for:

- Indicator calculations.  
- Setup detection.  
- Risk sizing.  
- News blocking logic.  
- Signal to EA JSON encoding and decoding.  

9.2. Integration tests for:

- End-to-end pipeline from OHLC data to signal.  
- EA polling and order placement on demo environment.  

9.3. Backtesting:

- Use at least 5 years of data per instrument.  
- Evaluate on multiple market regimes (trends, ranges, high and low volatility).  

9.4. ML validation:

- Train on a subset of history.  
- Validate on separate period.  
- Test on final out-of-sample data.

## 10. Acceptance Criteria

- All trend, setup, and risk rules are implemented exactly as per Strategy Rule Sheet.  
- No live or simulated trade violates risk or news blackout rules.  
- ML scoring demonstrably improves quality (e.g. higher average R or lower drawdown compared with raw strategy).  
- System is stable under continuous operation during market hours.  
- Logs are complete and sufficient for after-the-fact audit of every trade.
