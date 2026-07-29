# NSE Participant OI Market Prediction System

## Overview

An intelligent market analysis system that predicts next-day NIFTY movements by analyzing NSE Participant-wise Open Interest data. Uses contrarian logic (retail traders) combined with smart money (FII/Pro) positioning to generate high-confidence trading signals.

## Features

### ✅ Core Prediction Engine (`predict_market_view.py`)
- **Participant Classification**: Analyzes Client, DII, FII, and Pro stances
- **Advanced Signals**: Includes both Index and Stock Futures/Options
- **Contrarian Logic**: Inverts Client (retail) positioning as contrarian indicator
- **Smart Money Tracking**: Follows FII and Pro (institutional) direction
- **Confidence Scoring**: HIGH/MEDIUM/LOW based on magnitude and confirmation
- **Multi-factor Analysis**: Considers futures, options, magnitude, and trends

### ✅ Historical Tracking (`prediction_tracker.py`)
- **Automatic Logging**: Every prediction stored with timestamp
- **Accuracy Measurement**: Track correct vs wrong predictions
- **Confidence Breakdown**: Separate accuracy by HIGH/MEDIUM/LOW confidence
- **JSON Database**: Simple file-based storage (`prediction_history.json`)
- **Report Generation**: Human-readable accuracy reports

### ✅ High-Confidence Alerts (`high_confidence_alert.txt`)
- **Conditional Generation**: Only created for HIGH confidence setups
- **Eye-catching Format**: Telegram-optimized with emojis
- **Concise Summary**: Top 5 key factors, clear action recommendation
- **Priority Delivery**: Sent separately after regular prediction

### ✅ Backtesting Framework (`backtest_predictions.py`)
- **Historical Validation**: Compare predictions against actual NIFTY movements
- **Accuracy Metrics**: Overall and confidence-level breakdown
- **NIFTY Data Cache**: Store historical price data for validation
- **Performance Reports**: Detailed backtest analysis

### ✅ Automated Telegram Delivery (`send_telegram.py`)
- **Excel Report**: NSE Participant OI data spreadsheet
- **Market Prediction**: Full analysis with participant breakdown
- **High-Confidence Alert**: Separate urgent notification (if applicable)
- **Error Handling**: Graceful fallback if prediction fails

### ✅ GitHub Actions Integration (`.github/workflows/nse_oi_daily.yml`)
- **Daily Automation**: Runs at 9 PM IST (Mon-Fri)
- **Three-Step Process**:
  1. Generate Excel report from NSE data
  2. Generate market prediction (with error tolerance)
  3. Send both to Telegram
- **Manual Trigger**: `workflow_dispatch` for on-demand runs

## File Structure

```
27-July-2026/
├── predict_market_view.py          # Main prediction engine
├── prediction_tracker.py            # Historical tracking & accuracy
├── backtest_predictions.py          # Backtesting framework
├── send_telegram.py                 # Telegram delivery
├── nse_participant_oi_horizontal.py # Excel report generator
│
├── market_prediction.json           # Latest prediction (JSON)
├── market_prediction.txt            # Latest prediction (text)
├── high_confidence_alert.txt        # HIGH confidence alert (conditional)
├── prediction_history.json          # All predictions database
├── nifty_historical_cache.json      # NIFTY price data (for backtesting)
│
├── participant_oi_*.csv             # NSE raw data files
└── nse_participant_oi_*.xlsx        # Excel reports
```

## Usage

### 1. Generate Prediction

```bash
python predict_market_view.py
```

**Output:**
- `market_prediction.json` - Structured data
- `market_prediction.txt` - Telegram-ready message
- `high_confidence_alert.txt` - Only if confidence = HIGH
- Updates `prediction_history.json` automatically

### 2. View Prediction Accuracy

```bash
python prediction_tracker.py
```

**Output:**
```
═══════════════════════════════════════════════════════════
📊 PREDICTION ACCURACY REPORT
═══════════════════════════════════════════════════════════

📅 Period: Last 30 days
📈 Total Predictions: 15 (8 with outcomes)

🎯 Overall Accuracy: 75.0%
   ✓ Correct: 6 | ✗ Wrong: 2

📋 Breakdown by Confidence:
   🔥 HIGH: 85.7% (6/7)
   ⚡ MEDIUM: 50.0% (1/2)
   💭 LOW: N/A (0/0)

═══════════════════════════════════════════════════════════
```

### 3. Run Backtest (Requires NIFTY Data)

```bash
python backtest_predictions.py
```

**Note:** You need to populate `nifty_historical_cache.json` first:

```python
from backtest_predictions import NiftyDataFetcher

fetcher = NiftyDataFetcher()

# Add manual entries (date_str, open, close)
fetcher.add_manual_entry("24072026", 24500, 24650)  # +0.61%
fetcher.add_manual_entry("25072026", 24650, 24580)  # -0.28%
# ... add more dates
```

**Or integrate with Yahoo Finance:**
```python
import yfinance as yf

nifty = yf.Ticker("^NSEI")
hist = nifty.history(period="3mo")

for date, row in hist.iterrows():
    date_str = date.strftime("%d%m%Y")
    fetcher.add_manual_entry(date_str, row['Open'], row['Close'])
```

### 4. Send to Telegram

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

python send_telegram.py
```

**Sends (in order):**
1. Excel report (nse_participant_oi_*.xlsx)
2. Market prediction (market_prediction.txt)
3. High-confidence alert (if exists)

## Prediction Logic

### Signal Classification

**Primary Signal: Index Futures**
- Net Buy/Sell = (Long Change - Short Change)
- Thresholds:
  - NEUTRAL: |net| < 5,000 contracts
  - HIGH magnitude: > 30,000 contracts (weight = 1.0)
  - MEDIUM magnitude: 15,000-30,000 (weight = 0.5-1.0)
  - LOW magnitude: < 15,000 (weight < 0.5)

**Secondary Confirmation: Index Options**
- Call buying + Put selling = BULLISH
- Put buying + Call selling = BEARISH
- Confirms futures if both align

**Advanced Signals: Stock Futures/Options**
- Same logic as Index derivatives
- Additional context for sectoral positioning

### Decision Tree

```
1. Invert Client stance (contrarian indicator)
2. Compare with FII and Pro (smart money)

Results:
├─ Client(inverted) + FII + Pro all aligned → STRONG_BULLISH/BEARISH
├─ Client(inverted) + (FII or Pro) aligned → BULLISH/BEARISH
├─ FII + Pro aligned (no contrarian)       → MILDLY_BULLISH/BEARISH
└─ Mixed signals or all neutral            → NEUTRAL
```

### Confidence Scoring

**HIGH Confidence:**
- Average smart money magnitude > 25,000 contracts
- Options confirm futures direction (≥2 participants)
- Strong alignment (STRONG_BULLISH/BEARISH)

**MEDIUM Confidence:**
- Moderate magnitude (15,000-25,000)
- Partial confirmation or moderate alignment

**LOW Confidence:**
- Weak magnitude (< 15,000)
- Conflicting signals or neutral stances

## Telegram Message Format

### Regular Prediction
```
═══════════════════════════════════════════════════════════
📊 NIFTY MARKET VIEW PREDICTION - 24 JUL 2026
═══════════════════════════════════════════════════════════

🎯 MARKET VIEW: 🚀 STRONG BULLISH
📈 CONFIDENCE: 🔥 HIGH

📋 PARTICIPANT BREAKDOWN:

🔴 CLIENTS (Retail - Contrarian):
   • Index Futures: Sold Net 35,000 → BEARISH
   • Contrarian Signal: BULLISH ✓
   • Magnitude: Very Strong (35,000)
   • Options confirm futures direction ✓

🟢 FII: Bought Net 45,000 → BULLISH
   • Options confirm futures direction ✓
   • Magnitude: Very Strong (45,000)

🟢 PRO: Bought Net 28,000 → BULLISH
   • Options confirm futures direction ✓
   • Magnitude: Strong (28,000)

🔵 DII: Bought Net 12,000 → BULLISH
   • Magnitude: Moderate (12,000)

✅ KEY FACTORS:
1. Clients heavily bearish (35,000) → Strong contrarian bullish signal
2. FII strongly bullish (45,000) with options confirmation
3. Pro strongly bullish (28,000) with options confirmation
4. Combined smart money (FII+Pro): 73,000 contracts (very high)
5. All major participants aligned in same direction

💡 INTERPRETATION:
Strong Bullish view based on strong alignment between contrarian
Client positioning and smart money (FII+Pro). High conviction setup
with large positions and confirmation across multiple indicators.

⚠️ DISCLAIMER: Educational purposes only. Not investment advice.
═══════════════════════════════════════════════════════════
```

### High-Confidence Alert
```
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
🚨 HIGH CONFIDENCE SETUP DETECTED 🚨
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

📅 Date: 24 JUL 2026
🎯 Market View: 🚀 STRONG BULLISH
🔥 Confidence: HIGH

⚡ KEY REASONS:
1. Clients heavily bearish → Strong contrarian bullish signal
2. Both FII and Pro aggressively bullish with large positions
3. Combined smart money: 73,000 contracts (very high)
4. Options confirm futures direction
5. Sustained multi-day bullish trend

💼 ACTION RECOMMENDED:
Consider bullish strategies for next trading session

⚠️ Disclaimer: Educational only. Trade at your own risk.
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
```

## GitHub Actions Workflow

**Schedule:** Daily at 9 PM IST (15:30 UTC), Monday-Friday

**Steps:**
```yaml
1. Checkout repo
2. Setup Python 3.11
3. Install dependencies (requirements.txt)
4. Generate Excel report
5. Generate market prediction (continue-on-error: true)
6. Send both to Telegram
```

**Environment Variables Required:**
- `TELEGRAM_BOT_TOKEN` (GitHub Secret)
- `TELEGRAM_CHAT_ID` (GitHub Secret)

**Manual Trigger:**
- Go to GitHub Actions tab
- Select "NSE Participant OI Daily Report"
- Click "Run workflow"

## Error Handling

### Prediction Failure
If prediction generation fails:
- Creates fallback message: "Market prediction unavailable - please analyze data manually"
- Workflow continues (doesn't fail)
- Excel report still sent

### Missing CSV Files
If < 2 CSV files found:
- Error message: "Need at least 2 CSV files for comparison"
- Creates fallback message
- Exits with code 1

### Telegram Failure
- Excel send fails → Workflow exits (critical)
- Prediction send fails → Warning only (non-critical)
- Alert send fails → Warning only (non-critical)

## Future Enhancements

### Completed ✅
1. ✅ Historical tracking with accuracy measurement
2. ✅ Advanced signals (Stock Futures/Options)
3. ✅ High-confidence alert system
4. ✅ Backtesting framework

### Planned 📋
1. **Machine Learning Model**
   - Train on historical predictions + outcomes
   - Feature engineering: magnitude, alignment, trends
   - Model: Gradient Boosting or Random Forest
   - Target: Next-day NIFTY direction

2. **VIX Integration**
   - Fetch India VIX data
   - Adjust confidence based on volatility
   - High VIX = lower confidence multiplier

3. **FII Cash Flow Data**
   - Incorporate FII cash market data
   - Derivative + cash alignment = stronger signal
   - Divergence = warning flag

4. **Visualization Dashboard**
   - matplotlib/plotly charts
   - Position trends over time
   - Accuracy heatmap
   - Participant flow diagrams

5. **Real-time Monitoring**
   - Intraday position tracking
   - Position reversal alerts
   - Unusual activity detection

6. **Multi-timeframe Analysis**
   - 3-day, 5-day, 10-day trends
   - Trend consistency scoring
   - Trend reversal detection

## Dependencies

```
openpyxl
requests
```

**For backtesting (optional):**
```
yfinance  # Yahoo Finance API
```

## License

Educational purposes only. Not financial advice.

## Support

For issues or feature requests, contact via Telegram: `t.me/MarketAnalysisNiftyBankNifty`

---

**Version:** 2.0.0
**Last Updated:** 29 July 2026
**Author:** Market Analysis With Manish Kumar
