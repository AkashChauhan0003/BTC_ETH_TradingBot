import requests
import pandas as pd
import time

def get_binance_data(symbol="ETHUSDT", interval="5m", limit=100):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            print(f"[ERROR] Empty Binance OHLC for {symbol}")
            return None

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
        ])

        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
        df.set_index("open_time", inplace=True)
        df = df.astype({
            "open": float,
            "high": float,
            "low": float,
            "close": float,
            "volume": float
        })

        return df[["open", "high", "low", "close", "volume"]]

    except Exception as e:
        print(f"[ERROR] Failed to fetch Binance OHLC for {symbol}: {e}")
        return None

def get_latest_candle(symbol="ETHUSDT", interval="5m"):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol.upper()}&interval={interval}&limit=2"
        response = requests.get(url)
        data = response.json()

        if isinstance(data, list) and len(data) >= 2:
            candle = data[-2]  # second last = last closed candle
            return {
                "timestamp": int(candle[0] / 1000),
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5])
            }
        else:
            print("[ERROR] Binance data format unexpected:", data)
            return None

    except Exception as e:
        print("[ERROR] Failed to fetch candle:", e)
        return None

# Example usage
if __name__ == "__main__":
    while True:
        print(get_latest_candle())
        time.sleep(5)    