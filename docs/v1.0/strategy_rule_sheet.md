# AI Trading Copilot – Strategy Rule Sheet (v1.0)
Version: 1.0  
Date: 06 December 2025 (GST)

# SECTION A — INSTRUMENT SCOPE

1. The system must analyse only these instruments in v1:  
   1.1. EURUSD  
   1.2. GBPUSD  
   1.3. XAUUSD  
   1.4. NAS100 or US500 (choose one for v1)  
   1.5. BTCUSD or BTCUSDT  

2. Each instrument must have its own independent signal generator instance.

3. Each instrument operates on these timeframes:  
   3.1. Trend filter: Daily  
   3.2. Signal chart: H4  
   3.3. Optional refinement: H1 (disabled by default in v1)

# SECTION B — TREND REGIME LOGIC

4. Compute Daily 200 EMA and Daily 50 EMA for every instrument.

5. Define trend regime:

   5.1. Uptrend if:  
        - Close price > Daily 200 EMA  
        - Daily 50 EMA > Daily 200 EMA  
        - 50 EMA slope (last N=5 bars) > 0  

   5.2. Downtrend if:  
        - Close price < Daily 200 EMA  
        - Daily 50 EMA < Daily 200 EMA  
        - 50 EMA slope (last N=5 bars) < 0  

   5.3. Sideways if:  
        - Price is within ±1 ATR (Daily ATR14) of 200 EMA  
        - OR 50 EMA slope absolute value < threshold (default: 0.05 percent)

6. Trend regime must be computed once per Daily candle close and cached for efficiency.

7. Only signals that align with the trend regime are valid:  
   7.1. Uptrend → Only long trades allowed.  
   7.2. Downtrend → Only short trades allowed.  
   7.3. Sideways → No trades (v1 default).

# SECTION C — SETUP DETECTION (H4 CHART)

8. Identify candidate signals on H4 only.

9. Detect recent swing structure:

   9.1. Swing high: a bar whose high is greater than highs of two bars on both sides.  
   9.2. Swing low: a bar whose low is lower than lows of two bars on both sides.

10. Compute 20 EMA, 50 EMA and ATR14 on H4.

11. Pullback requirement (long trades):

   11.1. Price must previously create a swing high in the current trend.  
   11.2. Price must pull back into zone between 20 EMA and 50 EMA.  
   11.3. RSI14 must fall below 55 but stay above 35.  
   11.4. ATR14 must be above ATR_min (default: 30th percentile of last 100 bars).

12. Pullback requirement (short trades):  
    Mirror all rules in 11 with RSI above 45 but below 65, and pullback into EMAs from below.

13. Reversal trigger (candle pattern):

   13.1. Valid bullish reversal bar for longs:  
        - Bullish engulfing, OR  
        - Pin bar with lower wick at least 2 times body, OR  
        - Strong rejection bar closing above 50 percent of its range.

   13.2. Valid bearish reversal bar for shorts:  
        Mirror logic in 13.1.

14. If no valid reversal trigger forms, no signal is produced.

# SECTION D — ENTRY, STOP AND TARGETS

15. Entry logic:

   15.1. Entry price = close of reversal candle OR first retracement into 20 EMA after reversal.  
   15.2. System stores both: preferred entry and acceptable entry range.

16. Stop loss logic:

   16.1. Long trades: Stop must be below most recent swing low minus 1.0 to 1.5 × ATR14.  
   16.2. Short trades: Stop must be above most recent swing high plus 1.0 to 1.5 × ATR14.  
   16.3. Use default multiplier = 1.25 ATR for v1.

17. Take profit logic:

   17.1. TP1 = Entry ± 2R distance depending on direction.  
   17.2. TP2 = Entry ± 3R distance, if higher timeframe structure does not violate it.  
   17.3. If structure is too close, only TP1 is used.

18. No trailing stop in v1.

# SECTION E — RISK MANAGEMENT

19. Per trade risk:

   19.1. Minimum risk = 0.5 percent of equity.  
   19.2. Maximum risk = 1.0 percent of equity.  
   19.3. Default risk = 0.75 percent unless ML overrides within allowed bounds.

20. Position size formula must use:  
    PositionSize = (Equity × RiskPercent) ÷ (|Entry − Stop| × price_value_per_unit)

21. Portfolio level limits:

   21.1. Sum of open position risks must not exceed 3 percent of equity.  
   21.2. Daily realised loss must not exceed 2 percent of equity.  
   21.3. If exceeded, block new trades until new day (GMT or broker rollover).

22. Correlation rules:

   22.1. Cannot take long EURUSD and GBPUSD simultaneously if trend regime is identical and combined risk exceeds 1.5 percent.  
   22.2. Gold and NAS100 can be traded together but must obey global risk cap.  
   22.3. BTC is treated independently but still contributes to total 3 percent cap.

# SECTION F — NEWS FILTER

23. System must integrate economic calendar data with fields: currency, impact, timestamp, event name.

24. A high impact event is any event marked high from the calendar provider.

25. Pre-event block:

   25.1. No new signals allowed within 45 minutes before a high impact event relevant to the instrument.

26. Post-event block:

   26.1. No new signals allowed until 30 minutes after the event.

27. Sentiment classification:

   27.1. Headlines must be classified as positive, negative or neutral using rule-based or ML-based scoring.  
   27.2. Sentiment score for each currency or asset must be maintained in range −1 to +1.

28. If sentiment opposes signal direction with score magnitude greater than 0.5:

   28.1. Reduce risk by 50 percent.  
   28.2. If risk falls below minimum threshold, signal is invalid.

# SECTION G — ML QUALITY SCORE

29. Feature extraction required for every candidate signal.

30. Minimum features:

   30.1. Trend regime  
   30.2. RSI  
   30.3. ATR percentile  
   30.4. Distance to EMAs  
   30.5. Distance to structure  
   30.6. Session label  
   30.7. Sentiment score  
   30.8. Time to next high impact event  
   30.9. Last 20 outcomes in R  
   30.10. Rolling drawdown state

31. The ML model must output:  
    ProbabilityWin1R and ProbabilityWin2R.

32. ML gatekeeping:

   32.1. Accept trade only if ProbabilityWin1R ≥ 0.60.  
   32.2. Full risk allowed only if ProbabilityWin2R ≥ 0.50.  
   32.3. If below thresholds, discard the trade.

# SECTION H — SIGNAL GENERATION SPEC

33. Every valid setup must generate a signal object with:

   33.1. Instrument  
   33.2. Direction  
   33.3. Entry  
   33.4. Stop  
   33.5. TP1  
   33.6. TP2  
   33.7. Risk percent  
   33.8. Trend regime  
   33.9. Sentiment score  
   33.10. ML score  
   33.11. Timestamp  
   33.12. Structured reasons list

34. Signal must be pushed to local queue and exposed through API.

35. EA must display one signal per instrument at a time.

# SECTION I — EXECUTION RULES (SEMI-AUTO)

36. EA can only execute signals that come from the queue.

37. EA must calculate its own position size from SL distance to avoid mismatch.

38. EA must reject orders if:

   38.1. SL distance < broker minimum.  
   38.2. Lot size < broker minimum.  
   38.3. Order violates total risk caps.  

39. EA must send order confirmation back to API.

# SECTION J — LOGGING

40. Every signal must be logged with full parameters.

41. Every trade must log:

   41.1. Open price and time  
   41.2. Close price and time  
   41.3. R multiple  
   41.4. Reason closed  
   41.5. Max favourable and adverse excursion  

42. Daily summary must be generated automatically.
