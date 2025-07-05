import requests
import pandas as pd

def get_recent_data(symbol, interval="1m", limit=100):
    symbol_map = {
        "ETH-INR": "ethinr",
        "BTC-INR": "btcinr"
    }

    market = symbol_map.get(symbol.upper())
    if not market:
        print(f"[ERROR] Unsupported symbol: {symbol}")
        return None

    url = f"https://api.wazirx.com/api/v2/klines?market={market}&interval={interval}&limit={limit}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or len(data) == 0:
            print(f"[ERROR] Empty OHLC data for {symbol}")
            return None

        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume",
            "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
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

        df_filtered = df[["open", "high", "low", "close", "volume"]]
        if df_filtered.empty:
            print(f"[ERROR] DataFrame is empty after filtering for {symbol}")
            return None

        return df_filtered

    except Exception as e:
        print(f"[ERROR] Failed to fetch OHLC for {symbol}: {e}")
        return None
