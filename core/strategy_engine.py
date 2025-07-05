from strategies.smart_ai_strategy import SmartAIStrategy
from strategies.smartai_v2 import SmartAIV2
from core.forward_test_logger import log_forward_test
from utils.binance_data import get_latest_candle
from core.telegram_alert import send_telegram_alert
from core.sl_tp_checker import add_open_trade, check_sl_tp
from datetime import datetime
import time

# Initialize SmartAI strategy instance
# smart_ai = SmartAIStrategy(sl=10, rr=6)
smart_ai = SmartAIV2(sl=10, rr=6, min_confidence=50)

print("[SmartAI] Forward testing started on ETHUSDT strategy_engine...")
last_candle_time = None  # Track last processed candle

while True:
    candle = get_latest_candle(symbol="ETHUSDT", interval="1m")

    if candle and candle["timestamp"] != last_candle_time:
        last_candle_time = candle["timestamp"]
        print(f"Binance candle timestamp: {candle['timestamp']}")

        smart_ai.add_candle(candle)
        signal = smart_ai.generate_signal()

        if signal:
            print(
                f"[SIGNAL] {signal['type']} @ {signal['entry']} | SL: {signal['sl']} | TP: {signal['tp']} | Confidence: {signal['confidence_score']}"
            )

            if signal["confidence_score"] >= smart_ai.min_confidence:
                send_telegram_alert(signal)
                decision = "ENTER TRADE"
                decision = "ENTER TRADE"
                add_open_trade(signal)  # 🔥 This pushes it to 'Scalping Trades'
            else:
                decision = "SKIPPED"

            candle_time = datetime.fromtimestamp(signal["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

            log_forward_test(
                asset="ETHUSDT",
                signal=signal["type"],
                trend="UNKNOWN",
                rsi=0.0,
                macd=0.0,
                signal_line=0.0,
                volume_spike="Volume Spike" in signal["reason"],
                pattern=signal["reason"],
                decision=decision,
                reason="Logged for analysis",
                candle_time=candle_time,
                candle_price=signal["entry"],
                confidence_score=signal["confidence_score"],
                sl=signal["sl"],
                tp=signal["tp"]
            )
        else:
            print("[SmartAI] No signal on this candle.")
        # ✅ Run SL/TP check after processing signal
        check_sl_tp()
        
    time.sleep(5)
