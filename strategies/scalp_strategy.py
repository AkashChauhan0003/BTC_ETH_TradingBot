from utils.indicators import (
    calculate_ema, calculate_atr, calculate_rsi, calculate_macd
)
from utils.multi_timeframe_strategy import get_trend
from utils.smart_ai_strategy import is_bearish_engulfing, is_bullish_engulfing, is_volume_spike
from utils.strategy_thresholds import (
    RSI_PERIOD, RSI_BUY_MAX, RSI_SELL_MIN,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL
)
from core.forward_test_logger import log_forward_test


def generate_scalp_signal(df, config, asset_name="ASSET"):
    trend = get_trend(df)
    atr = calculate_atr(df.copy(), period=14).iloc[-1]
    rsi = calculate_rsi(df['close'], period=RSI_PERIOD).iloc[-1]
    macd_line, signal_line, _ = calculate_macd(df['close'], MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    last = df.iloc[-1]
    prev = df.iloc[-2]
    vol_spike = is_volume_spike(df, config.get("VOLUME_SPIKE_THRESHOLD", 2.0))

    score = 0
    signal = None
    sl = None
    tp = None
    pattern = "None"
    reason = ""
    decision = "Rejected"

    if trend == "UP":
        if is_bullish_engulfing(last, prev):
            pattern = "Bullish Engulfing"
            score += 25
        else:
            reason += "No bullish engulfing | "

        if rsi < config.get("RSI_BUY_MAX", RSI_BUY_MAX):
            score += 25
        else:
            reason += "RSI too high | "

        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            score += 25
        else:
            reason += "MACD not aligned | "

        if vol_spike:
            score += 25
        else:
            reason += "No volume spike | "

        if score >= 75:
            signal = "BUY"
            sl = last['low'] - atr
            tp = last['close'] + 1.5 * atr
            reason = "Confirmed"
            decision = "Accepted"

    elif trend == "DOWN":
        if is_bearish_engulfing(last, prev):
            pattern = "Bearish Engulfing"
            score += 25
        else:
            reason += "No bearish engulfing | "

        if rsi > config.get("RSI_SELL_MIN", RSI_SELL_MIN):
            score += 25
        else:
            reason += "RSI too low | "

        if macd_line.iloc[-1] < signal_line.iloc[-1]:
            score += 25
        else:
            reason += "MACD not aligned | "

        if vol_spike:
            score += 25
        else:
            reason += "No volume spike | "

        if score >= 75:
            signal = "SELL"
            sl = last['high'] + atr
            tp = last['close'] - 1.5 * atr
            reason = "Confirmed"
            decision = "Accepted"

    # Final log to Google Sheet
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

    return signal, sl, tp
