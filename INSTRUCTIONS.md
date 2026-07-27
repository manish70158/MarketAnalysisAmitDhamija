# NSE F&O Participant OI - Exact Format Instructions

## 📸 What You Get
An Excel file that matches your screenshot EXACTLY:
- ✅ 2x3 grid layout (6 sections)
- ✅ Color-coded rows (Green=Bullish, Red=Bearish)
- ✅ Index Futures, Stock Futures
- ✅ Index Options (Call/Put), Stock Options (Call/Put)
- ✅ Participant-wise data (Client, DII, FII, Pro)

## 🚀 Quick Start

### Step 1: See the Demo
```bash
source venv/bin/activate
python demo_exact_format.py
```
This creates: `EXACT_FORMAT_Participant_OI_24_JUL_2026.xlsx`

Open it to see the exact format matching your screenshot!

### Step 2: Download Real NSE Data

1. Visit: **https://www.nseindia.com/all-reports-derivatives**

2. Find: **"F&O-Participant wise Open Interest (csv)"**

3. Select date: **24-JUL-2026** (or your desired date)

4. Click download button to save the CSV file

5. Save the file (e.g., `fao_participant_oi_24JUL2026.csv`)

### Step 3: Inspect the CSV Structure
```bash
python inspect_nse_csv.py fao_participant_oi_24JUL2026.csv
```

This will show:
- Column names
- Data structure
- Sample values
- Help identify where participant data is located

### Step 4: Process with Real Data

Once you have the CSV file, run:
```bash
python nse_participant_oi_formatter.py fao_participant_oi_24JUL2026.csv
```

**Note:** The parser may need adjustment based on actual NSE CSV structure. After running `inspect_nse_csv.py`, share the output so I can update the parser if needed.

## 📁 Files Overview

| File | Purpose |
|------|---------|
| `demo_exact_format.py` | Creates demo Excel with exact screenshot format |
| `inspect_nse_csv.py` | Analyzes NSE CSV structure |
| `nse_participant_oi_formatter.py` | Main formatter (needs NSE CSV) |
| `EXACT_FORMAT_Participant_OI_24_JUL_2026.xlsx` | Demo output file |

## 🎨 Format Details

### Layout Structure
```
┌─────────────────────────────────────────────────┐
│  F&O Participant-wise OI - 24-JUL-2026 (Title)  │
├──────────────────────┬──────────────────────────┤
│   Index Futures      │   Index Call Options     │
│  ┌──────────────┐    │  ┌──────────────┐       │
│  │ Client  🟢   │    │  │ Client  🔴   │       │
│  │ DII     🟢   │    │  │ DII     🟢   │       │
│  │ FII     🔴   │    │  │ FII     🔴   │       │
│  │ Pro     🟢   │    │  │ Pro     🟢   │       │
│  └──────────────┘    │  └──────────────┘       │
├──────────────────────┼──────────────────────────┤
│  Index Put Options   │   Stock Futures          │
│  ┌──────────────┐    │  ┌──────────────┐       │
│  │ Client  🟢   │    │  │ Client  🟢   │       │
│  │ DII     🔴   │    │  │ DII     🟢   │       │
│  │ FII     🟢   │    │  │ FII     🔴   │       │
│  │ Pro     🔴   │    │  │ Pro     🟢   │       │
│  └──────────────┘    │  └──────────────┘       │
├──────────────────────┼──────────────────────────┤
│  Stock Call Options  │  Stock Put Options       │
│  ┌──────────────┐    │  ┌──────────────┐       │
│  │ Client  🔴   │    │  │ Client  🟢   │       │
│  │ DII     🟢   │    │  │ DII     🔴   │       │
│  │ FII     🔴   │    │  │ FII     🟢   │       │
│  │ Pro     🟢   │    │  │ Pro     🔴   │       │
│  └──────────────┘    │  └──────────────┘       │
└──────────────────────┴──────────────────────────┘
```

### Each Section Contains:
- **Participant**: Client, DII, FII, Pro
- **Long OI**: Long position changes (+/-)
- **Short OI**: Short position changes (+/-)
- **Action**: Build Long, Build Short, Closed Longs, Closed Shorts
- **View**: Bullish (🟢) or Bearish (🔴)

## 🎯 Color Logic

| Long OI | Short OI | Action | Color |
|---------|----------|--------|-------|
| ↑ More  | ↑ Less   | Build Long | 🟢 Green (Bullish) |
| ↑       | ↓        | Closed Shorts | 🟢 Green (Bullish) |
| ↑ Less  | ↑ More   | Build Short | 🔴 Red (Bearish) |
| ↓       | ↑        | Closed Longs | 🔴 Red (Bearish) |
| ↓ More  | ↓ Less   | Closed Longs | 🔴 Red (Bearish) |
| ↓ Less  | ↓ More   | Closed Shorts | 🟢 Green (Bullish) |

## 🔧 Troubleshooting

### NSE website not allowing download?
- Use incognito/private browsing
- Try different browser
- Check if market is closed (weekends/holidays)

### CSV format different than expected?
1. Run `inspect_nse_csv.py your_file.csv`
2. Share the output
3. Parser can be adjusted accordingly

### Excel not opening correctly?
- Ensure openpyxl is installed: `pip install openpyxl`
- Try opening with Microsoft Excel or LibreOffice

## 📞 Next Steps

1. ✅ Run demo to see the format
2. ⬇️ Download CSV from NSE
3. 🔍 Inspect CSV structure
4. ⚙️ Update parser if needed (based on inspection)
5. 🎨 Generate formatted Excel

---

**Made to match your screenshot exactly!** 📸
