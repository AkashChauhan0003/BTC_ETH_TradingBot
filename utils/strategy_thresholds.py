# === STRATEGY THRESHOLDS ===
# Adjust these to fine-tune strategy behavior

# RSI confirmation
RSI_PERIOD = 14
RSI_BUY_MAX = 65     # BUY signal only if RSI < 65
RSI_SELL_MIN = 35    # SELL signal only if RSI > 35

# MACD confirmation
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Volume spike (in % above average)
VOLUME_SPIKE_THRESHOLD = 1.8  # 1.8x of average volume

# Candlestick patterns (min body & wick ratios)
ENGULFING_MIN_BODY_RATIO = 1.2
HAMMER_WICK_BODY_RATIO = 2.5

# Optional: Filter combinations
REQUIRE_RSI_CONFIRMATION = True
REQUIRE_MACD_CONFIRMATION = True
REQUIRE_VOLUME_SPIKE = False
REQUIRE_PATTERN_CONFIRMATION = True