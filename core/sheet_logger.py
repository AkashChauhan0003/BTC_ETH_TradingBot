import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from config import sheet_url

HEADERS = [
    "Timestamp", "Asset", "Signal", "Entry Price", "SL", "TP", "Status", "Trigger Time"
]

def log_trade(asset, direction, price, sl="", tp=""):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Connect to sheet and tab
    sheet = client.open_by_url(sheet_url)
    tab = sheet.worksheet("Scalping Trades")

    # Add headers if empty
    if not tab.get_all_values():
        tab.append_row(HEADERS)

    now = datetime.now()
    row = [
        now.strftime("%Y-%m-%d %H:%M:%S"),
        asset,
        direction,
        round(price, 2),
        round(sl, 2) if sl else "",
        round(tp, 2) if tp else "",
        "Pending",
        now.strftime("%H:%M:%S")
    ]
    tab.append_row(row)
