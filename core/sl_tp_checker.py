import json
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import sheet_url
from core.price_feed import get_eth_price, get_btc_price
from datetime import datetime

HEADERS = [
    "Timestamp", "Asset", "Signal", "Entry Price", "SL", "TP",
    "Status", "Trigger Time", "Hit TP40", "Hit TP50", "Hit TP60", "Timeframe"
]

def check_sl_tp():
    print("🔍 Checking SL/TP status...")

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Load credentials from env variable
    creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)  
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url)
    tab = sheet.worksheet("Scalping Trades")

    all_rows = tab.get_all_values()

    # Auto-add headers if sheet is empty
    if not all_rows:
        print("📝 Initializing header row...")
        tab.append_row(HEADERS)
        return

    headers = all_rows[0]
    rows = all_rows[1:]

    # Ensure new columns exist
    required_cols = ["Hit TP40", "Hit TP50", "Hit TP60"]
    for col in required_cols:
        if col not in headers:
            print("🔁 Updating sheet headers to include TP hit markers...")
            tab.clear()
            tab.append_row(HEADERS)
            return

    idx_status = headers.index("Status")
    idx_asset = headers.index("Asset")
    idx_price = headers.index("Entry Price")
    idx_sl = headers.index("SL")
    idx_tp = headers.index("TP")
    idx_signal = headers.index("Signal")
    idx_trigger_time = headers.index("Trigger Time")
    idx_tp40 = headers.index("Hit TP40")
    idx_tp50 = headers.index("Hit TP50")
    idx_tp60 = headers.index("Hit TP60")

    updated = False

    for i, row in enumerate(rows):
        status = row[idx_status].strip().lower()
        print("🔍 Checking SL/TP status...",status)
        if status != "pending":
            continue

        asset = row[idx_asset]
        try:
            entry = float(row[idx_price])
            sl = float(row[idx_sl]) if row[idx_sl] else None
            tp = float(row[idx_tp]) if row[idx_tp] else None
        except ValueError:
            continue

        signal = row[idx_signal]
        row_number = i + 2

        if asset in ["ETH-INR", "ETHUSDT"]:
            price = get_eth_price()
            print("🔍 Checking SL/TP status...",price) ;   
        elif asset in ["BTC-INR", "BTCUSDT"]:
            price = get_btc_price()
        else:
            print(f"⚠️ Unsupported asset: {asset}")
            continue

        if not price:
            continue

        # Calculate partial TP levels
        tp40 = entry + 40 if signal == "BUY" else entry - 40
        tp50 = entry + 50 if signal == "BUY" else entry - 50
        tp60 = tp  # full TP already provided

        hit_tp40 = price >= tp40 if signal == "BUY" else price <= tp40
        hit_tp50 = price >= tp50 if signal == "BUY" else price <= tp50
        hit_tp60 = price >= tp60 if signal == "BUY" else price <= tp60
        print(f"📈 Checking trade {row_number} - Live price = {price}, TP = {tp}")          

        # Update intermediate TP columns
        row_values = tab.row_values(row_number)

        if hit_tp40:
            row_values[idx_tp40] = "✅"
        if hit_tp50:
            row_values[idx_tp50] = "✅"
        if hit_tp60:
            row_values[idx_tp60] = "✅"
        # Final result
        hit = None
        if signal == "BUY":
            if tp and price >= tp:
                hit = "Target Hit"
            elif sl and price <= sl:
                hit = "SL Hit"
        elif signal == "SELL":
            if tp and price <= tp:
                hit = "Target Hit"
            elif sl and price >= sl:
                hit = "SL Hit"

        if hit:
            row_values[idx_status] = hit
            row_values[idx_trigger_time] = datetime.now().strftime("%H:%M:%S")

            # 🚀 Only one API call per row!
            try:
                tab.update(f"A{row_number}:M{row_number}", [row_values[:13]])
                updated = True
            except Exception as e:
                print(f"⚠️ Failed to update row {row_number}: {e}")

    if not updated:
        print("✅ No SL/TP triggered this cycle.")


def add_open_trade(signal, timeframe="1m"):
    import gspread
    from config import sheet_url
    from oauth2client.service_account import ServiceAccountCredentials
    from datetime import datetime

    HEADERS = [
        "Timestamp", "Asset", "Signal", "Entry Price", "SL", "TP",
        "Status", "Trigger Time", "Hit TP40", "Hit TP50", "Hit TP60", "Timeframe"
    ]

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Load credentials from env variable
    creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)    
    client = gspread.authorize(creds)

    sheet = client.open_by_url(sheet_url)
    tab = sheet.worksheet("Scalping Trades")

    # 💡 Check and reset headers if needed
    existing_headers = tab.row_values(1)
    if existing_headers != HEADERS:
        print("🛠 Headers out of sync. Resetting...")
        tab.clear()
        tab.append_row(HEADERS)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ❌ Fix: prevent duplicate by timestamp + timeframe (not just timestamp)
    existing_rows = tab.get_all_values()
    duplicate = False
    for row in existing_rows[1:]:  # skip header
        if len(row) >= 13 and row[0] == now and row[12] == timeframe:
            duplicate = True
            break

    if duplicate:
        print(f"⚠️ Skipping duplicate entry for {timeframe} at {now}")
        return

    row = [
        now,
        "ETHUSDT",
        signal["type"],
        signal["entry"],
        signal["sl"],
        signal["tp"],
        "pending",
        "", "", "", "",  # TP40 / TP50 / TP60
        timeframe        # ✅ logs this so we can filter later
    ]

    tab.append_row(row)
    print(f"📩 Trade logged for {timeframe} — {signal['type']} @ {signal['entry']}")
