from utils.indicators import calculate_ema
from utils.data_collector import get_recent_data
from utils.smart_ai_strategy import generate_signal
import pandas as pd

def get_trend(df):
    if df is None or len(df) < 60:
        return "SIDEWAYS"

    fast_ema = calculate_ema(df['close'], 9)
    mid_ema = calculate_ema(df['close'], 21)
    slow_ema = calculate_ema(df['close'], 50)

    if len(fast_ema) == 0 or len(mid_ema) == 0 or len(slow_ema) == 0:
        return "SIDEWAYS"

    if fast_ema.iloc[-1] > mid_ema.iloc[-1] > slow_ema.iloc[-1]:
        return "UP"
    elif fast_ema.iloc[-1] < mid_ema.iloc[-1] < slow_ema.iloc[-1]:
        return "DOWN"
    else:
        return "SIDEWAYS"

def generate_multi_tf_signal(symbol, asset_config):
    df_5m = get_recent_data(symbol, interval="5m", limit=50)
    df_15m = get_recent_data(symbol, interval="15m", limit=50)
    df_1h = get_recent_data(symbol, interval="1h", limit=50)

    if df_5m is None or df_15m is None or df_1h is None:
        return None, None, None

    trend_5m = get_trend(df_5m)
    trend_15m = get_trend(df_15m)
    trend_1h = get_trend(df_1h)
    print(f"[DEBUG] {symbol} Trends → 5m: {trend_5m}, 15m: {trend_15m}, 1H: {trend_1h}")

    # Only proceed if trends align across all timeframes
    if trend_5m == trend_15m == trend_1h and trend_5m in ["UP", "DOWN"]:
        signal, sl, tp = generate_signal(df_5m,config, asset_config)
        return signal, sl, tp

    return None, None, None