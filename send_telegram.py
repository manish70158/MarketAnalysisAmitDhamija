"""
Send the generated NSE Participant OI Excel report to Telegram.
Reads TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from environment variables.
"""

import glob
import os
import sys
from datetime import datetime

import requests


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("ERROR: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        sys.exit(1)

    # Find the generated xlsx file
    files = glob.glob("nse_participant_oi_*.xlsx")
    if not files:
        print("ERROR: No .xlsx report file found")
        sys.exit(1)

    # Use the most recently modified file
    report_file = max(files, key=os.path.getmtime)
    caption = f"NSE Participant OI Report - {datetime.now().strftime('%d %b %Y')}"

    print(f"Sending: {report_file}")
    print(f"Caption: {caption}")

    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(report_file, "rb") as f:
        resp = requests.post(
            url,
            data={"chat_id": chat_id, "caption": caption},
            files={"document": (report_file, f)},
            timeout=30,
        )

    if resp.status_code == 200 and resp.json().get("ok"):
        print("✓ Excel report sent successfully")
    else:
        print(f"ERROR: Telegram API returned {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    # Send prediction if available
    if os.path.exists("market_prediction.txt"):
        print("\nSending market prediction...")
        with open("market_prediction.txt", "r") as f:
            prediction_text = f.read()

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(
            url,
            data={"chat_id": chat_id, "text": prediction_text},
            timeout=30,
        )

        if resp.status_code == 200 and resp.json().get("ok"):
            print("✓ Prediction sent successfully")
        else:
            print(f"WARNING: Prediction send failed with status {resp.status_code}")
            print(resp.text)

    # Send high-confidence alert if available (with higher priority formatting)
    if os.path.exists("high_confidence_alert.txt"):
        print("\nSending HIGH CONFIDENCE ALERT...")
        with open("high_confidence_alert.txt", "r") as f:
            alert_text = f.read()

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(
            url,
            data={"chat_id": chat_id, "text": alert_text},
            timeout=30,
        )

        if resp.status_code == 200 and resp.json().get("ok"):
            print("✓ 🔥 High confidence alert sent successfully")
        else:
            print(f"WARNING: Alert send failed with status {resp.status_code}")
            print(resp.text)


if __name__ == "__main__":
    main()
