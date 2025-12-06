# MT4 EA Integration Specification

## Objective

Allow MetaTrader 4 to:

1. Request the latest trading signal for a given instrument from the
   AI Trading Copilot FastAPI server.
2. Display the suggested entry, stop-loss and take-profit on the chart.
3. Allow the trader to accept the signal and place an order.
4. Report the order ticket back to the API.

## HTTP endpoint

- URL: `http://localhost:8000/signal/latest?instrument=SYMBOL`
- Method: GET
- Response: JSON, matching the `SignalResponse` schema:

```json
{
  "instrument": "EURUSD",
  "direction": "long",
  "entry": 1.10234,
  "stop": 1.09900,
  "tp1": 1.10834,
  "tp2": null,
  "risk_percent": 0.75,
  "trend_regime": "uptrend",
  "timestamp": "2025-11-25T08:00:00Z"
}
```

If there is no signal, the endpoint returns HTTP 200 with a null body.

## EA behaviour

1. Inputs:

   - `ApiUrl`        – base URL of the API, default `http://localhost:8000`.
   - `Instrument`    – symbol, default `EURUSD`.
   - `PollingPeriod` – seconds between API calls, default 60.

2. On each `OnTimer` event:

   - Build URL: `ApiUrl + "/signal/latest?instrument=" + Instrument`.
   - Perform HTTP GET using `WebRequest`.
   - If response is non-empty JSON:
     - Parse fields into internal variables.
     - Draw horizontal lines for entry, stop, TP1, TP2 (if present).
     - Update chart objects with trend regime and risk.

3. On user action (for example pressing a chart button or setting an input):

   - Calculate lot size from risk percent, account equity and SL distance.
   - Send `OrderSend` with correct direction (buy/sell).
   - If order succeeds, call a separate endpoint (to be defined later)
     to report ticket id and status.

## Notes

- MT4 requires that the API host be whitelisted in:
  - `Tools -> Options -> Expert Advisors -> Allow WebRequest for listed URL`
- The EA must handle network errors gracefully and avoid spamming requests.

## MT4 platform setup

### 1. Allow WebRequest to the API URL

1. In MetaTrader 4, go to: `Tools` → `Options` → `Expert Advisors`.
2. Tick `Allow WebRequest for listed URL`.
3. In the URL list, add: `http://localhost:8000`
4. Click `OK`.

Without this, `WebRequest` calls from the EA will fail.

### 2. Install the EA

1. Copy `AICopilotEA.mq4` into your MT4 `Experts` folder.
   - Typically: `MQL4/Experts/`
2. In MT4, open the `Navigator` panel.
3. Right-click `Expert Advisors` → `Refresh` or restart MT4.
4. You should see `AICopilotEA` in the list.

### 3. Attach EA to a chart

1. Open a chart for the symbol matching the `Instrument` input (for example `EURUSD`).
2. Drag `AICopilotEA` from `Navigator` onto the chart.
3. In the EA inputs:
   - Set `ApiUrl` if different from default (usually `http://localhost:8000`).
   - Set `Instrument` to match the chart symbol (e.g. `EURUSD`).
   - Adjust `PollingPeriod` (in seconds) if desired.
4. Ensure `AutoTrading` is enabled in MT4 if you later add order sending logic.

### 4. Confirm JSON is received

With the FastAPI server running, watch the MT4 `Experts` log:

- When a signal exists, you should see lines like:
  - `Received signal JSON: {"instrument": "EURUSD", ...}`

Once that works, the EA will also draw:

- Horizontal line for entry (blue).
- Horizontal line for stop (red).
- Horizontal line for TP1 (green).
- Optional TP2 line if present.
- A label in the top-left with direction, trend, and risk%.

This confirms full end-to-end connectivity between MT4 and the AI Trading Copilot.
