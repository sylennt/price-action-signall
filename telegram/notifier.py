import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_signal(pair, signal):
    message = f"""
📊 CRYPTO PRICE ACTION SIGNAL

Pair: {pair}
Direction: {signal['direction']}
Timeframe: 15m

Entry: {signal['entry']}
Stop Loss: {signal['sl']}
Take Profit: {signal['tp']}

Risk:Reward → 1:2

Logic:
• Trend aligned (1H)
• Liquidity sweep at structure
• Strong impulse candle
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)
