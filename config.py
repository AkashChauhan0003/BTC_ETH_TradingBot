import os
import json

# Sheet URL from Railway environment
sheet_url = os.environ.get("sheet_url")

# Telegram credentials from Railway env
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Strategy settings from env (JSON strings)
eth_config = json.loads(os.environ.get("ETH_CONFIG_JSON", "{}"))
btc_config = json.loads(os.environ.get("BTC_CONFIG_JSON", "{}")) if os.environ.get("BTC_CONFIG_JSON") else eth_config

# Strategy type (SCALP, INTRADAY, SWING)
ACTIVE_STRATEGY = os.environ.get("ACTIVE_STRATEGY", "SCALP")
