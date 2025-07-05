import time
import traceback
import subprocess
from core.price_feed import get_eth_price, get_btc_price
from core.strategy_engine import check_trade_signal
from core.telegram_alert import send_alert
from core.sheet_logger import log_trade
from core.sl_tp_checker import check_sl_tp
from config import eth_config, btc_config

print("✅ SmartAI Bot Running...")

while True:
    try:
        eth_price = get_eth_price()
        print("[DEBUG] ETH-INR Live Price:", eth_price)

        if eth_price:
            print("[DEBUG] Running strategy on ETHINR...")
            signal = check_trade_signal("ETHUSDT", eth_price, eth_config)
            print("[DEBUG] Signal result:", signal)

            if signal:
                send_alert("ETHINR", signal, eth_price)
                log_trade(
                    asset="ETH-INR",
                    direction=signal["signal"],
                    price=eth_price,
                    sl=signal.get("sl"),
                    tp=signal.get("tp")
                )

        btc_price = get_btc_price()
        print("[DEBUG] ETH-INR Live Price:", btc_price)

        if btc_price:
            print("[DEBUG] Running strategy on BTC-INR...")

            signal = check_trade_signal("BTCUSDT", btc_price, btc_config)
            print("[DEBUG] Signal result:", signal)
            if signal:
                send_alert("BTC-INR", signal, btc_price)
                log_trade(
                    asset="BTC-INR",
                    direction=signal["signal"],
                    price=btc_price,
                    sl=signal.get("sl"),
                    tp=signal.get("tp")
                )

        check_sl_tp()
        print("✅ Cycle complete. Sleeping 5min...")
        time.sleep(300)

    except Exception as e:
        print("⚠️ Exception occurred:")
        traceback.print_exc()
        time.sleep(300)
