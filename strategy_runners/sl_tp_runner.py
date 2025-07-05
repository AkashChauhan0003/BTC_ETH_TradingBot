import time
from core.sl_tp_checker import check_sl_tp

print("🧠 SL/TP checker started...")

while True:
    check_sl_tp()
    time.sleep(30)  # Run every 60 seconds