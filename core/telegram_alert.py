import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from datetime import datetime

def send_telegram_alert(signal):
    try:
        # Format timestamp
        signal_time = datetime.fromtimestamp(signal['timestamp']).strftime("%Y-%m-%d %H:%M:%S")

        message = f"""
📈 *{signal['type']} SIGNAL* – *ETHUSDT*

*Entry:* {signal['entry']}
*SL:* {signal['sl']}  |  *TP:* {signal['tp']}

🎯 *Reason:* SmartAI 3-Candle Entry
🕒 {signal_time}
"""

        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=payload)

        if response.status_code == 200:
            print("📨 Telegram alert sent successfully.")
        else:
            print(f"❌ Telegram alert failed: {response.text}")

    except Exception as e:
        print(f"❌ Telegram exception: {e}")
