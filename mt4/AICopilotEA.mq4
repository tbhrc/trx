//+------------------------------------------------------------------+
//|                                               AICopilotEA.mq4    |
//|                    AI Trading Copilot – MT4 integration (v1.0)   |
//+------------------------------------------------------------------+
#property strict

//--- external inputs
extern string ApiUrl        = "http://localhost:8000";
extern string Instrument    = "EURUSD";
extern int    PollingPeriod = 60;   // seconds

datetime lastPollTime = 0;

//--- global variables for last signal
string  g_direction   = "";
double  g_entry       = 0.0;
double  g_stop        = 0.0;
double  g_tp1         = 0.0;
double  g_tp2         = 0.0;
double  g_riskPercent = 0.0;
string  g_trend       = "";

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int init()
  {
   EventSetTimer(PollingPeriod);
   ObjectsDeleteAll(0, "AIC_");
   return(0);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
int deinit()
  {
   EventKillTimer();
   ObjectsDeleteAll(0, "AIC_");
   return(0);
  }
//+------------------------------------------------------------------+
//| Timer event handler                                              |
//+------------------------------------------------------------------+
void OnTimer()
  {
   datetime nowTime = TimeCurrent();
   if(nowTime - lastPollTime < PollingPeriod) return;
   lastPollTime = nowTime;

   string url = ApiUrl + "/signal/latest?instrument=" + Instrument;
   char   post[], result[];
   string headers = "";
   int    timeout = 5000;

   int res = WebRequest("GET", url, headers, timeout, post, 0, result, 0);
   if(res == -1)
     {
      Print("WebRequest error: check URL permissions in MT4 options.");
      return;
     }

   string json = CharArrayToString(result, 0, -1);
   if(StringLen(json) == 0 || json == "null")
     {
      // no signal
      return;
     }

   // Parse JSON in a lightweight way assuming the schema from the API.
   if(!ParseSignalJson(json))
     {
      Print("Failed to parse signal JSON.");
      return;
     }

   DrawSignalLevels();
  }

//+------------------------------------------------------------------+
//| Parse JSON string into global variables                          |
//+------------------------------------------------------------------+
bool ParseSignalJson(string json)
  {
   // This is a very simple parser that searches for key tokens and
   // extracts numeric values using StringFind and StringSubstr.
   // For production, integrating a full JSON parser library is better.

   g_direction   = ExtractString(json, ""direction":"", """);
   g_trend       = ExtractString(json, ""trend_regime":"", """);
   g_entry       = ExtractDouble(json, ""entry":");
   g_stop        = ExtractDouble(json, ""stop":");
   g_tp1         = ExtractDouble(json, ""tp1":");
   g_tp2         = ExtractDouble(json, ""tp2":");
   g_riskPercent = ExtractDouble(json, ""risk_percent":");

   if(g_entry == 0.0 || g_stop == 0.0 || g_tp1 == 0.0)
      return(false);

   return(true);
  }

//+------------------------------------------------------------------+
//| Helper: extract string field                                     |
//+------------------------------------------------------------------+
string ExtractString(string json, string key, string terminator)
  {
   int start = StringFind(json, key);
   if(start < 0) return("");
   start += StringLen(key);
   int end = StringFind(json, terminator, start);
   if(end < 0) return("");
   return(StringSubstr(json, start, end - start));
  }

//+------------------------------------------------------------------+
//| Helper: extract double field                                     |
//+------------------------------------------------------------------+
double ExtractDouble(string json, string key)
  {
   int start = StringFind(json, key);
   if(start < 0) return(0.0);
   start += StringLen(key);
   int end = StringFind(json, ",", start);
   if(end < 0) end = StringFind(json, "}", start);
   if(end < 0) return(0.0);
   string sub = StringSubstr(json, start, end - start);
   sub = StringTrimLeft(StringTrimRight(sub));
   return(StrToDouble(sub));
  }

//+------------------------------------------------------------------+
//| Draw entry, stop and TP levels on chart                          |
//+------------------------------------------------------------------+
void DrawSignalLevels()
  {
   string prefix = "AIC_";
   // Remove previous objects
   ObjectsDeleteAll(0, prefix);

   if(g_entry == 0.0 || g_stop == 0.0 || g_tp1 == 0.0)
      return;

   datetime nowTime = Time[0];

   DrawHLine(prefix + "ENTRY", g_entry, clrDodgerBlue, STYLE_SOLID);
   DrawHLine(prefix + "STOP",  g_stop,  clrRed,       STYLE_DASHDOT);
   DrawHLine(prefix + "TP1",   g_tp1,   clrLimeGreen, STYLE_DASH);

   if(g_tp2 != 0.0)
      DrawHLine(prefix + "TP2", g_tp2, clrLimeGreen, STYLE_DOT);

   string label = prefix + "INFO";
   if(ObjectFind(label) < 0)
     {
      ObjectCreate(label, OBJ_LABEL, 0, 0, 0);
      ObjectSet(label, OBJPROP_CORNER, 0);
      ObjectSet(label, OBJPROP_XDISTANCE, 10);
      ObjectSet(label, OBJPROP_YDISTANCE, 15);
     }
   string text = "Direction: " + g_direction +
                 "  Trend: " + g_trend +
                 "  Risk%: " + DoubleToStr(g_riskPercent, 2);
   ObjectSetText(label, text, 10, "Arial", clrWhite);
  }

//+------------------------------------------------------------------+
//| Helper: draw horizontal line                                     |
//+------------------------------------------------------------------+
void DrawHLine(string name, double price, color clr, int style)
  {
   if(ObjectFind(name) < 0)
     {
      ObjectCreate(name, OBJ_HLINE, 0, Time[0], price);
     }
   ObjectSet(name, OBJPROP_PRICE1, price);
   ObjectSet(name, OBJPROP_COLOR, clr);
   ObjectSet(name, OBJPROP_STYLE, style);
   ObjectSet(name, OBJPROP_WIDTH, 1);
  }
//+------------------------------------------------------------------+
