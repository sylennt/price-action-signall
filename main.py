import ccxt
import pandas as pd
import numpy as np
import requests
import os

# ========== CONFIG ==========
PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
TIMEFRAME = "15m"
LIMIT = 200

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ========== EXCHANGE ==========
exchange = ccxt.bybit({
    "enableRateLimit": True,
    "options": {
        "defaultType": "spot"
    }
})

# ========== FUNCTIONS ==========
def fetch_ohlcv(symbol):
    data = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)
    df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close", "volume"])
    return df

def detect_trend(df):
    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()

    if df["ema50"].iloc[-1] > df["ema200"].iloc[-1]:
        return "uptrend"
    elif df["ema50"].iloc[-1] < df["ema200"].iloc[-1]:
        return "downtrend"
    else:
        return "range"

def support_resistance(df):
    support = df["low"].rolling(20).min().iloc[-1]
    resistance = df["high"].rolling(20).max().iloc[-1]
    return support, resistance

def liquidity_sweep(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if last["low"] < prev["low"] and last["close"] > prev["low"]:
        return "buy"
    if last["high"] > prev["high"] and last["close"] < prev["high"]:
        return "sell"
    return None

def send_signal(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, json=payload)

# ========== MAIN LOGIC ==========
def run():
    for pair in PAIRS:
        df = fetch_ohlcv(pair)
        trend = detect_trend(df)
        support, resistance = support_resistance(df)
        sweep = liquidity_sweep(df)

        price = df["close"].iloc[-1]

        if sweep == "buy" and trend == "uptrend" and price > support:
            msg = f"""
📈 BUY SIGNAL ({TIMEFRAME})
Pair: {pair}
Price: {price}
Trend: Uptrend
Support: {support}
            """
            send_signal(msg)

        elif sweep == "sell" and trend == "downtrend" and price < resistance:
            msg = f"""
📉 SELL SIGNAL ({TIMEFRAME})
Pair: {pair}
Price: {price}
Trend: Downtrend
Resistance: {resistance}
            """
            send_signal(msg)

if __name__ == "__main__":
    run()
