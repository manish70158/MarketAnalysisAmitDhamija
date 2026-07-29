# Quick Start: Market Prediction Enhancements

## What's New? 🚀

Your NSE Participant OI system now has 4 major enhancements:

### 1. 📊 Historical Tracking & Accuracy Measurement
Track every prediction and measure accuracy over time.

**Try it:**
```bash
python prediction_tracker.py
```

### 2. 🔥 High-Confidence Alert System
Get urgent notifications only when confidence is HIGH.

**How it works:**
- Automatically generates `high_confidence_alert.txt` when confidence = HIGH
- Sent as separate Telegram message (after regular prediction)
- Eye-catching format with top factors and action recommendation

### 3. 📈 Advanced Signals (Stock Futures/Options)
Prediction now includes both Index and Stock derivatives for better accuracy.

**See it in action:**
```bash
python predict_market_view.py
```

Look for:
```
Client: Index=BULLISH (net: +9,011), Stock=BEARISH
```

### 4. 🧪 Backtesting Framework
Validate predictions against actual NIFTY movements.

**Setup (one-time):**
```python
from backtest_predictions import NiftyDataFetcher

fetcher = NiftyDataFetcher()

# Add historical NIFTY data manually
fetcher.add_manual_entry("24072026", 24500.50, 24650.75)
fetcher.add_manual_entry("25072026", 24650.75, 24580.20)
# ... more dates
```

**Or use Yahoo Finance:**
```bash
pip install yfinance
```

```python
import yfinance as yf
from backtest_predictions import NiftyDataFetcher

nifty = yf.Ticker("^NSEI")
hist = nifty.history(period="3mo")

fetcher = NiftyDataFetcher()
for date, row in hist.iterrows():
    date_str = date.strftime("%d%m%Y")
    fetcher.add_manual_entry(date_str, row['Open'], row['Close'])
```

**Run backtest:**
```bash
python backtest_predictions.py
```

## Daily Workflow (Automated)

Your GitHub Actions workflow now runs 3 steps:

1. **Generate Excel Report** → `nse_participant_oi_horizontal.py`
2. **Generate Market Prediction** → `predict_market_view.py`
   - Creates prediction files
   - Automatically logs to history
   - Generates high-confidence alert if applicable
3. **Send to Telegram** → `send_telegram.py`
   - Sends Excel report
   - Sends prediction
   - Sends high-confidence alert (if exists)

**All automatic at 9 PM IST, Mon-Fri!**

## Manual Testing

Test the complete flow locally:

```bash
# Step 1: Generate Excel report (fetches latest NSE data)
python nse_participant_oi_horizontal.py

# Step 2: Generate prediction (includes all enhancements)
python predict_market_view.py

# Step 3: Check what was generated
ls -lh market_prediction.* high_confidence_alert.txt prediction_history.json

# Step 4: View prediction
cat market_prediction.txt

# Step 5: Check if high-confidence alert was created
cat high_confidence_alert.txt  # Only exists if confidence = HIGH

# Step 6: View accuracy (after multiple predictions)
python prediction_tracker.py

# Step 7: Send to Telegram (requires env variables)
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python send_telegram.py
```

## Understanding Output Files

| File | When Created | Purpose |
|------|--------------|---------|
| `market_prediction.json` | Every run | Structured prediction data |
| `market_prediction.txt` | Every run | Telegram-ready message |
| `high_confidence_alert.txt` | Only HIGH confidence | Urgent alert message |
| `prediction_history.json` | After each prediction | Historical database |
| `nifty_historical_cache.json` | When you add NIFTY data | Backtesting data |
| `backtest_results.json` | After backtest | Backtest metrics |

## Telegram Messages You'll Receive

### Regular Day (Any Confidence)
1. **Excel Report** (always sent)
2. **Market Prediction** (full analysis)

### High-Confidence Day
1. **Excel Report** (always sent)
2. **Market Prediction** (full analysis)
3. **🔥 HIGH CONFIDENCE ALERT** (urgent notification)

## Checking Accuracy

After running for a few weeks:

```bash
# View accuracy report
python prediction_tracker.py
```

**Example output:**
```
═══════════════════════════════════════════════════════════
📊 PREDICTION ACCURACY REPORT
═══════════════════════════════════════════════════════════

📅 Period: Last 30 days
📈 Total Predictions: 20 (15 with outcomes)

🎯 Overall Accuracy: 73.3%
   ✓ Correct: 11 | ✗ Wrong: 4

📋 Breakdown by Confidence:
   🔥 HIGH: 87.5% (7/8)
   ⚡ MEDIUM: 66.7% (4/6)
   💭 LOW: 0.0% (0/1)

═══════════════════════════════════════════════════════════
```

**Tip:** HIGH confidence predictions should have >80% accuracy. If not, the thresholds may need adjustment.

## Updating Actual Outcomes (For Tracking)

To measure accuracy, you need to update predictions with actual outcomes:

```python
from prediction_tracker import PredictionTracker

tracker = PredictionTracker()

# After market closes, update with actual movement
tracker.update_actual_result(
    date_str="24 JUL 2026",
    actual_movement="BULLISH",  # or "BEARISH" or "NEUTRAL"
    nifty_change_percent=0.85   # Percentage change
)

# Check updated accuracy
print(tracker.generate_report(days=30))
```

**Automated option:** Run a script daily that:
1. Fetches yesterday's NIFTY data
2. Calculates movement
3. Updates tracker
4. Generates weekly accuracy report

## Troubleshooting

### No High-Confidence Alert Created
✅ **This is normal!** Alert only generated when:
- Confidence = HIGH
- Average smart money magnitude > 25,000
- Options confirm futures (≥2 participants)
- Strong alignment detected

### Prediction Shows LOW Confidence
✅ **Expected** when:
- Participant positions are weak (< 15,000 contracts)
- Mixed signals (no clear alignment)
- Options don't confirm futures

### Backtest Shows No Data
❌ **You need to populate NIFTY cache first**
- See "Setup (one-time)" section above
- Use Yahoo Finance integration for easy setup

### Accuracy Tracking Shows 0 Predictions
❌ **You need to update with actual outcomes**
- See "Updating Actual Outcomes" section above
- Or wait for automated integration (future enhancement)

## Next Steps

1. **Let it run for 2 weeks** - Collect prediction history
2. **Populate NIFTY data** - Enable backtesting
3. **Monitor accuracy** - Check weekly with `prediction_tracker.py`
4. **Adjust thresholds** - If HIGH confidence accuracy < 80%
5. **Add automation** - Auto-update actual outcomes

## Questions?

- Full documentation: `PREDICTION_SYSTEM_README.md`
- GitHub workflow: `.github/workflows/nse_oi_daily.yml`
- Telegram: `t.me/MarketAnalysisNiftyBankNifty`

---

**Remember:** These are educational tools. Always do your own analysis before trading!
