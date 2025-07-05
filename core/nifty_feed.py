import requests

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json"
}

def get_nifty_price():
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        return float(data["data"][0]["lastPrice"])
    except Exception as e:
        print("NIFTY error:", e)
        return None

def get_banknifty_price():
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20BANK"
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        return float(data["data"][0]["lastPrice"])
    except Exception as e:
        print("BANKNIFTY error:", e)
        return None
