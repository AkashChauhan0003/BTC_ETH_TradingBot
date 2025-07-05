from utils.indicators import (
    calculate_ema, calculate_atr, calculate_rsi, calculate_macd
)
from utils.multi_timeframe_strategy import get_trend
from utils.smart_ai_strategy import is_bearish_engulfing, is_bullish_engulfing, is_volume_spike
from utils.strategy_thresholds import (
    RSI_PERIOD, RSI_BUY_MAX, RSI_SELL_MIN,
    MACD_FAST, MACD_SLOW, MACD_SIGNAL,
    VOLUME_SPIKE_THRESHOLD,
    ENGULFING_MIN_BODY_RATIO,
    REQUIRE_RSI_CONFIRMATION, REQUIRE_MACD_CONFIRMATION,
    REQUIRE_VOLUME_SPIKE, REQUIRE_PATTERN_CONFIRMATION
)
from core.forward_test_logger import log_forward_test

def generate_swing_signal(df, asset_name="ASSET"):
    trend = get_trend(df)
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
    score = 0

    if trend == "UP":
        pattern = "Bullish Engulfing" if is_bullish_engulfing(last, prev, config) else "None"
        if REQUIRE_PATTERN_CONFIRMATION and pattern == "None":
            reason = "No bullish engulfing"
        elif REQUIRE_RSI_CONFIRMATION and rsi > RSI_BUY_MAX:
            reason = "RSI too high"
        elif REQUIRE_MACD_CONFIRMATION and macd_line.iloc[-1] < signal_line.iloc[-1]:
            reason = "MACD not aligned"
        elif REQUIRE_VOLUME_SPIKE and not vol_spike:
            reason = "No volume spike"
        else:
            signal = "BUY"
            sl = last['low'] - atr
            tp = last['close'] + 5 * atr
            score = 95

    elif trend == "DOWN":
        pattern = "Bearish Engulfing" if is_bearish_engulfing(last, prev) else "None"
        if REQUIRE_PATTERN_CONFIRMATION and pattern == "None":
            reason = "No bearish engulfing"
        elif REQUIRE_RSI_CONFIRMATION and rsi < RSI_SELL_MIN:
            reason = "RSI too low"
        elif REQUIRE_MACD_CONFIRMATION and macd_line.iloc[-1] > signal_line.iloc[-1]:
            reason = "MACD not aligned"
        elif REQUIRE_VOLUME_SPIKE and not vol_spike:
            reason = "No volume spike"
        else:
            signal = "SELL"
            sl = last['high'] + atr
            tp = last['close'] - 5 * atr
            score = 95

    decision = "Accepted" if signal else "Rejected"
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
