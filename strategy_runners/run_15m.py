import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from datetime import datetime
from core.sl_tp_checker import add_open_trade
from strategies.smartai_v2 import SmartAIV2
from utils.binance_data import get_latest_candle
from core.forward_test_logger import log_forward_test
from core.telegram_alert import send_telegram_alert


smart_ai = SmartAIV2(sl=10, rr=6, min_confidence=50)
last_candle_time = None

print("[SmartAI 15m] Forward testing started on ETHUSDT 15-minute candles...")

while True:
    candle = get_latest_candle(symbol="ETHUSDT", interval="15m")

    if candle and candle["timestamp"] != last_candle_time:
        last_candle_time = candle["timestamp"]
        smart_ai.add_candle(candle)
        signal = smart_ai.generate_signal()

        if signal:
            print(f"[15m SIGNAL] {signal['type']} @ {signal['entry']} | SL: {signal['sl']} | TP: {signal['tp']} | Confidence: {signal['confidence_score']}")

            candle_time = datetime.fromtimestamp(signal["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

            if signal["confidence_score"] >= smart_ai.min_confidence:
                decision = "ENTER TRADE"
                add_open_trade(signal, timeframe="15m")
            else:
                decision = "SKIPPED"

            if signal["confidence_score"] >= 70:
                send_telegram_alert(signal)

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
                tp=signal["tp"],
                sheet_name="15m Forward Test"
            )

        else:
            print("[SmartAI 15m] No signal on this candle.")

    time.sleep(5)
