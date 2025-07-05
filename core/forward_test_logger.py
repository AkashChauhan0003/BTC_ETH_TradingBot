import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import sheet_url, ACTIVE_STRATEGY


def log_forward_test(
    *,
    asset,
    signal,
    trend,
    rsi,
    macd,
    signal_line,
    volume_spike,
    pattern,
    decision,
    reason,
    candle_time,
    candle_price,
    confidence_score=0,
    sl=0,
    tp=0,
    sheet_name=None  # ✅ Add this
):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    # Load credentials from env variable
    creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)      
    client = gspread.authorize(creds)

    try:
        sheet = client.open_by_url(sheet_url)

        # Determine sheet name based on strategy
        # Allow override from caller
        print(f"📄 Creating new TestTEstTEst'{sheet_name}' sheet... from forward test logger")

        if not sheet_name:
            if ACTIVE_STRATEGY == "SCALP":
                sheet_name = "Scalp Forward Test"
            elif ACTIVE_STRATEGY == "INTRADAY":
                sheet_name = "Intraday Forward Test"
            elif ACTIVE_STRATEGY == "SWING":
                sheet_name = "Swing Forward Test"
            else:
                sheet_name = "Forward Test Log"

        try:
            tab = sheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"📄 Creating new '{sheet_name}' sheet...")
            tab = sheet.add_worksheet(title=sheet_name, rows="1000", cols="20")
            headers = [
                "Timestamp", "Asset", "Trend", "Signal", "Confidence",
                "Candle Time", "Close Price", "RSI", "MACD", "Signal Line",
                "Volume Spike", "Pattern", "Decision", "Reason","SL","TP"
            ]
            tab.append_row(headers)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [
                now,
                asset,
                trend,
                signal,
                confidence_score,
                candle_time,
                round(candle_price, 2),
                round(rsi, 2),
                round(macd, 2),
                round(signal_line, 2),
                str(volume_spike),
                pattern,
                decision,
                reason,
                round(sl, 2),
                round(tp, 2)
            ]
        tab.append_row(row)
        print("✅ Forward test log entry saved.")
    except Exception as e:
        print(f"❌ Forward test logging failed: {e}")
