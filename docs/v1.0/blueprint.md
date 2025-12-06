# AI Trading Copilot – Blueprint Document "FROZEN"
Version: 1.0  
Date: 06 December 2025 (GST)

## 1. Objective and high-level concept

You are not building an automatic profit machine. You are building a trading copilot that:

1. Watches a small set of instruments in real time.  
2. Combines technical trend and structure with volatility filters.  
3. Adds a news and macro awareness layer.  
4. Outputs clear trade plans:
   - Direction (long or short)
   - Entry zone
   - Stop-loss
   - Take-profit
   - Position size as a percent of equity

Initially, the system acts as a signal and risk assistant. Only after robust testing on demo and paper trading would you consider semi- or fully automated execution.

## 2. Asset universe and timeframes

### 2.1 Instruments

v1 focuses on a small, liquid universe:

- EURUSD  
- GBPUSD  
- XAUUSD (gold vs USD)  
- NAS100 or US500 (one index CFD to start)  
- BTCUSD or BTCUSDT (via CFD or exchange feed)

### 2.2 Timeframes

- Higher timeframe trend filter: Daily  
- Primary signal timeframe: H4  
- Optional refinement timeframe: H1 (disabled by default)

The system prefers swing-style trading rather than scalping low timeframes.

## 3. Strategy logic

### 3.1 Trend regime

On the Daily chart, compute:

- 200 EMA  
- 50 EMA  

Define regimes:

- Uptrend:
  - Close > 200 EMA  
  - 50 EMA > 200 EMA  
  - 50 EMA slope over last 5 bars > 0  

- Downtrend:
  - Close < 200 EMA  
  - 50 EMA < 200 EMA  
  - 50 EMA slope over last 5 bars < 0  

- Sideways:
  - Price within ±1 Daily ATR(14) of 200 EMA, or  
  - Absolute slope of 50 EMA below a small threshold

Trading rules:

- Only long in uptrend  
- Only short in downtrend  
- No trading in sideways regime for v1

### 3.2 Pullback pattern on H4

For each instrument on H4:

1. Identify swing highs and lows:
   - Swing high: high greater than highs of at least two bars on each side.  
   - Swing low: low lower than lows of at least two bars on each side.

2. Compute:
   - 20 EMA, 50 EMA, ATR14, RSI14.

3. Long setup in uptrend:

   - Price previously created a swing high consistent with the trend.  
   - Price pulls back into zone between 20 EMA and 50 EMA.  
   - RSI14 dips below 55 but stays above 35.  
   - ATR14 above a minimum volatility threshold (for example 30th percentile of last 100 bars).  
   - A bullish reversal candle forms in or near the EMA zone:
     - Bullish engulfing, or  
     - Pin bar with lower wick at least 2 times the body, or  
     - Rejection bar closing above 50 percent of its range.

4. Short setup in downtrend mirrors the above in the opposite direction.

If any required condition is not satisfied, no signal is generated.

### 3.3 Entry, stop and targets

- Entry:
  - Default entry at or near the close of the reversal candle.  
  - Optionally define an entry zone around 20 EMA for limit entries.

- Stop-loss:
  - For long: below recent swing low minus k × ATR14 (k default 1.25).  
  - For short: above recent swing high plus k × ATR14.

- Take-profit:
  - TP1 at 2R (twice distance from entry to stop).  
  - TP2 at 3R if higher timeframe structure allows; otherwise only TP1.

No trailing stop in v1.

## 4. Risk and money management

### 4.1 Per-trade risk

- Risk per trade between 0.5 percent and 1.0 percent of account equity.  
- Default risk 0.75 percent.  
- Position size:
  - PositionSize = (Equity × RiskPercent) ÷ (monetary value of distance between entry and stop).

### 4.2 Portfolio level safeguards

- Maximum open risk across all trades: 3 percent of equity.  
- Maximum daily realised loss: 2 percent of equity. When reached, no new trades until next trading day.  
- Correlated exposure rules:
  - Limit combined risk on highly correlated FX pairs in same direction.  
  - Gold and indices treated separately but still within total risk cap.  
  - BTC considered independent, but also contributes to caps.

## 5. News and macro filter

### 5.1 Economic calendar

Integrate a calendar feed providing:

- Event time  
- Currency or region  
- Impact level (low, medium, high)  
- Event name  

Rules:

- Block new entries 45 minutes before high impact events affecting the instrument.  
- Block new entries until 30 minutes after such events.  
- Optionally, relax rules for lower impact events.

### 5.2 News sentiment

Use NLP to analyse headlines and short news texts:

- Classify as positive, negative or neutral for each relevant currency or asset.  
- Maintain a rolling sentiment score between −1 and +1 per instrument.  

Sentiment usage:

- If sentiment strongly opposes the trade direction (for example score < −0.5 for a long), reduce risk or skip trade.  
- If sentiment supports the trade, allow full risk.

## 6. ML signal quality scoring

### 6.1 Features

For every candidate trade, extract features such as:

- Trend regime (up, down, sideways)  
- Distance of price to 20, 50 and 200 EMA  
- EMA slopes  
- Pullback depth relative to prior swing move  
- RSI14 value and any divergence flags  
- ATR14 absolute and as percentile  
- Distance to local support/resistance and higher timeframe levels  
- Session label (Asia, London, New York)  
- Sentiment score and time to next high impact event  
- Recent performance metrics (last 20 trades, rolling drawdown state)

### 6.2 Model

- Preferred: gradient boosted tree model (for example XGBoost, LightGBM).  
- Output:
  - Probability that trade reaches at least +1R before −1R.  
  - Probability that trade reaches at least +2R before −1R.

### 6.3 Decision thresholds

- Accept trade if Probability(≥ +1R before −1R) ≥ 0.60.  
- Allow full risk if Probability(≥ +2R before −1R) ≥ 0.50.  
- Otherwise discard or reduce risk within permitted bounds.

## 7. Explanation and coaching layer

Use a language model as a commentary engine:

- Explain signal rationale in plain language.  
- Warn when risk limits or drawdown thresholds are close.  
- Generate daily and weekly summaries including:
  - Trades taken and their outcomes in R.  
  - Instruments behaving cleanly or erratically.  
  - Impact of news events on strategy performance.

This layer does not decide trades; it improves transparency and user understanding.

## 8. System architecture

### 8.1 Components

- Python core (strategy, risk, ML, news).  
- FastAPI service exposing:
  - Endpoints for fetching signals, trades and summaries.  
- SQLite database:
  - For signals, trades, performance statistics.  
- Optional web dashboard:
  - For visualising charts, positions, and logs.  
- MT4 or MT5 Expert Advisors:
  - For chart display and order execution.

### 8.2 Data flow

1. Price data feeds into the core engine.  
2. Engine computes indicators and checks for setups on bar close.  
3. ML scorer evaluates candidate trades.  
4. News and calendar filters apply.  
5. A signal object is created if all conditions are met.  
6. Signal is stored in the database and exposed through the API.  
7. EA polls the API, displays signal and, on user acceptance, places orders.  
8. EA reports executions back to the API for logging and analytics.

## 9. Backtesting and validation

### 9.1 Backtesting engine

Requirements:

- Simulate trades on historical OHLC data for all supported instruments.  
- Include realistic spread, commission and slippage estimates.  
- Support portfolio level risk limits and daily stops.  

Metrics:

- Net return in R and percent.  
- Maximum drawdown.  
- Win rate, average win and average loss in R.  
- Profit factor.  
- Longest losing streak.  
- Distribution of trade outcomes.

### 9.2 Validation approach

- Split historical data into:
  - Training period (for parameter selection and ML training).  
  - Validation period (for model and rule tuning).  
  - Out-of-sample test period (untouched until final evaluation).

- Use walk-forward analysis instead of a single static optimisation.

## 10. EA bridge design

### 10.1 Responsibilities

EA per instrument:

- Polls the API for the latest pending signal.  
- Draws entry, stop and targets on chart.  
- Shows risk and R:R details.  
- Provides user controls for acceptance or rejection.  
- Calculates lot size based on SL distance and risk percent.  
- Places orders and reports ticket details back to the API.

### 10.2 Communication protocol (example)

- `GET /signal/latest?instrument=EURUSD`  
- Response: JSON with signal fields (instrument, direction, entry, stop, TP1, TP2, risk, scores).  
- `POST /signal/{id}/status` with payload:
  - `status` ("accepted" or "rejected")  
  - `ticket` (if accepted)

## 11. Assumptions and constraints

- Assumption: data and economic calendar feeds will be available and reliable.  
- Assumption: the system runs on a local Windows machine.  
- Constraint: v1 will not attempt extremely low latency HFT; bar close logic is sufficient.  
- Constraint: auto execution is limited and always subject to hard risk caps.

## 12. Suggested next steps

1. Finalise the precise strategy rule sheet and lock parameters for v1.  
2. Scaffold the Python project with modules for core, API, ML, storage and UI.  
3. Implement and test the backtesting engine for a subset of instruments.  
4. Develop the MT4 or MT5 EA bridge in parallel for seamless integration.  
5. Run extended paper trading before considering live deployment.
