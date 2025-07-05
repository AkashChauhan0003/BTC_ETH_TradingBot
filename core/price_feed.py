import requests
from datetime import datetime

# headers = {
#     "User-Agent": "Mozilla/5.0",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Accept": "application/json"
# }

# def get_nifty_price():
#     try:
#         url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
#         r = requests.get(url, headers=headers, timeout=5)
#         data = r.json()
#         return float(data["data"][0]["lastPrice"])
#     except Exception as e:
#         print("NIFTY error:", e)
#         return None

# def get_banknifty_price():
#     try:
#         url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20BANK"
#         r = requests.get(url, headers=headers, timeout=5)
#         data = r.json()
#         return float(data["data"][0]["lastPrice"])
#     except Exception as e:
#         print("BANKNIFTY error:", e)
#         return None

# def get_crude_price():
#     try:
#         url = "https://api.metals.live/v1/spot"  # returns many commodities
#         r = requests.get(url, timeout=5)
#         data = r.json()
#         crude_price = next((x[1] for x in data if x[0] == "crude oil"), None)
#         return float(crude_price)
#     except Exception as e:
#         print("CRUDE error:", e)
#         return None
def fetch_wazirx_candles(symbol="ethinr", interval="5m", limit=50):
    url = f"https://api.wazirx.com/api/v2/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        candles = []
        for item in data:
            candles.append({
                "timestamp": datetime.fromtimestamp(item[0]/1000),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4])
            })
        return candles
    except Exception as e:
        print(f"Error fetching {symbol} candles:", e)
        return []
    
def get_eth_price():
    try:
        response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT")
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f"❌ Failed to fetch Binance price: {e}")
        return None

def get_btc_price():
    try:
        url = "https://api.wazirx.com/api/v2/tickers/btcinr"
        r = requests.get(url, timeout=5)
        data = r.json()
        return float(data["ticker"]["last"])
    except Exception as e:
        print("BTC error:", e)
        return None