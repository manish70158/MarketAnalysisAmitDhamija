# NSE F&O Participant-wise Open Interest Fetcher

Fetches and formats F&O Participant-wise Open Interest data from NSE India with color-coded Excel output.

## Features

- Downloads participant OI data from NSE archives
- Formats data with conditional colors:
  - **Green**: Bullish signals (Build Long, Closed Shorts)
  - **Red**: Bearish signals (Build Short, Closed Longs)
- Generates Excel files matching NSE report format
- Supports manual CSV processing for reliable data extraction

## Setup

1. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Automatic Download (May Fail Due to NSE Anti-Scraping)

```bash
python fetch_nse_participant_oi.py
```

### Method 2: Manual Download + Processing (Recommended)

1. Visit: https://www.nseindia.com/all-reports-derivatives

2. Find "F&O-Participant wise Open Interest (csv)" section

3. Download the CSV file for your desired date (e.g., 24-JUL-2026)

4. Process the downloaded file:
```bash
python fetch_nse_participant_oi.py path/to/downloaded/file.csv
```

## Output Files

- `participant_oi_DD_MMM_YYYY_raw.csv`: Raw CSV data from NSE
- `participant_oi_DD_MMM_YYYY_formatted.xlsx`: Color-formatted Excel file

## Color Coding Legend

| Action | Color | Interpretation |
|--------|-------|----------------|
| Build Long | Green | Bullish - New long positions added |
| Closed Shorts | Green | Bullish - Short positions covered |
| Build Short | Red | Bearish - New short positions added |
| Closed Longs | Red | Bearish - Long positions squared off |
| Build Net | Green/Red | Based on net OI direction |

## Data Structure

The script analyzes:
- Index Futures (Client, DII, FII, Pro)
- Stock Futures (Client, DII, FII, Pro)
- Index Options - Call & Put (Client, DII, FII, Pro)
- Stock Options - Call & Put (Client, DII, FII, Pro)

## Troubleshooting

### Cannot Download from NSE
- NSE has strict anti-scraping measures
- Use Manual Method (recommended)
- Check if date is a trading day (not holiday/weekend)

### CSV Parsing Errors
- Verify the CSV file is complete and not corrupted
- Check if NSE has changed their CSV format
- Ensure the file is from the correct NSE reports page

### Missing Dependencies
```bash
pip install --upgrade requests pandas openpyxl
```

## Date Format

Date should be in format: `DD-MMM-YYYY` (e.g., `24-JUL-2026`)

## Notes

- Start date is set to 24-JUL-2026 by default
- You can modify the `start_date` variable in `main()` function
- NSE data is typically available T+1 (next trading day)
