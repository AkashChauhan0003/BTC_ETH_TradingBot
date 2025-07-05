from utils.indicators import (
    calculate_ema, calculate_atr, calculate_rsi, calculate_macd
)
from utils.strategy_thresholds import (
    RSI_PERIOD, RSI_BUY_MAX, RSI_SELL_MIN,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    VOLUME_SPIKE_THRESHOLD,
    ENGULFING_MIN_BODY_RATIO, HAMMER_WICK_BODY_RATIO,
    REQUIRE_RSI_CONFIRMATION, REQUIRE_MACD_CONFIRMATION,
    REQUIRE_VOLUME_SPIKE, REQUIRE_PATTERN_CONFIRMATION
)
from core.forward_test_logger import log_forward_test
import pandas as pd

def get_trend(df):
    if df is None or len(df) < 60:
        return "SIDEWAYS"

    fast_ema = calculate_ema(df['close'], 9)
    mid_ema = calculate_ema(df['close'], 21)
    slow_ema = calculate_ema(df['close'], 50)

    if fast_ema.iloc[-1] > mid_ema.iloc[-1] > slow_ema.iloc[-1]:
        return "UP"
    elif fast_ema.iloc[-1] < mid_ema.iloc[-1] < slow_ema.iloc[-1]:
        return "DOWN"
    else:
        return "SIDEWAYS"

def is_volume_spike(df,config, threshold=2.0):
    recent_vol = df['volume'].iloc[-1]
    avg_vol = df['volume'].rolling(20).mean().iloc[-2]
    return recent_vol >= avg_vol * threshold

def is_bullish_engulfing(last, prev, config=None):
    body_ratio = config.get("ENGULFING_MIN_BODY_RATIO", 1.5) if config else 1.5
    return (
        last['close'] > last['open'] and
        prev['close'] < prev['open'] and
        (last['close'] - last['open']) > body_ratio * (prev['open'] - prev['close'])
    )

def is_bearish_engulfing(last, prev, config=None):
    body_ratio = config.get("ENGULFING_MIN_BODY_RATIO", 1.5) if config else 1.5
    return (
        last['close'] < last['open'] and
        prev['close'] > prev['open'] and
        (prev['close'] - prev['open']) > body_ratio * (last['open'] - last['close'])
    )

def generate_signal(df, config, asset_name="ASSET"):
    trend = get_trend(df)

    if trend == "SIDEWAYS":
        confidence = 0
        reason = "Trend not aligned"
        decision = "Rejected"
        print("[DEBUG] Attempting to log forward test...")
        try:
            log_forward_test(
    asset="ETHUSDT",
    signal=signal or "-",
    trend=trend,
    rsi=rsi,
    macd=macd_line.iloc[-1],
    signal_line=signal_line.iloc[-1],
    volume_spike=vol_spike,
    pattern=pattern,
    decision="Accepted" if signal else "Rejected",
    reason=reason,
    candle_time=str(last.name),
    candle_price=last['close'],
    confidence_score=score
)
        except Exception as e:
            print("❌ Failed to log forward test (trend rejection):", str(e))
        print(f"❌ Rejected: {reason}")
        return None, None, None, confidence

    atr = calculate_atr(df, period=14).iloc[-1]
    rsi = calculate_rsi(df['close'], period=RSI_PERIOD).iloc[-1]
    macd_line, signal_line, _ = calculate_macd(df['close'], MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    last = df.iloc[-1]
    prev = df.iloc[-2]
    vol_spike = is_volume_spike(df, config.get("VOLUME_SPIKE_THRESHOLD", 2.0))  # type: ignore

    pattern = None
    reason = "Confirmed"
    signal = None
    sl = None
    tp = None
    confidence = 0

    if trend == "UP":
        pattern = "Bullish Engulfing" if is_bullish_engulfing(last, prev, config) else "None"
        if pattern != "None":
            confidence += 25
        if REQUIRE_PATTERN_CONFIRMATION and pattern == "None":
            reason = "No bullish engulfing"
        elif REQUIRE_RSI_CONFIRMATION and rsi > RSI_BUY_MAX:
            reason = "RSI too high"
        else:
            confidence += 25

        if REQUIRE_MACD_CONFIRMATION:
            if macd_line.iloc[-1] > signal_line.iloc[-1]:
                confidence += 25
            else:
                reason = "MACD not aligned"

        if REQUIRE_VOLUME_SPIKE:
            if vol_spike:
                confidence += 25
            else:
                reason = "No volume spike"

        if confidence >= 75:
            signal = "BUY"
            sl = last['low'] - atr
            tp = last['close'] + 3 * atr

    elif trend == "DOWN":
        pattern = "Bearish Engulfing" if is_bearish_engulfing(last, prev) else "None"
        if pattern != "None":
            confidence += 25
        if REQUIRE_PATTERN_CONFIRMATION and pattern == "None":
            reason = "No bearish engulfing"
        elif REQUIRE_RSI_CONFIRMATION and rsi < RSI_SELL_MIN:
            reason = "RSI too low"
        else:
            confidence += 25

        if REQUIRE_MACD_CONFIRMATION:
            if macd_line.iloc[-1] < signal_line.iloc[-1]:
                confidence += 25
            else:
                reason = "MACD not aligned"

        if REQUIRE_VOLUME_SPIKE:
            if vol_spike:
                confidence += 25
            else:
                reason = "No volume spike"

        if confidence >= 75:
            signal = "SELL"
            sl = last['high'] + atr
            tp = last['close'] - 3 * atr

    decision = "Accepted" if signal else "Rejected"
    print("[DEBUG] Attempting to log forward test...")
    try:
        log_forward_test(
    asset="ETHUSDT",
    signal=signal or "-",
    trend=trend,
    rsi=rsi,
    macd=macd_line.iloc[-1],
    signal_line=signal_line.iloc[-1],
    volume_spike=vol_spike,
    pattern=pattern,
    decision="Accepted" if signal else "Rejected",
    reason=reason,
    candle_time=str(last.name),
    candle_price=last['close'],
    confidence_score=score
)
    except Exception as e:
        print("❌ Failed to log forward test:", str(e))

    if signal:
        print(f"✅ Signal: {signal} confirmed with score {confidence}")
    else:
        print(f"❌ Rejected: {reason} | Confidence Score: {confidence}")
    return signal, sl, tp, confidence
