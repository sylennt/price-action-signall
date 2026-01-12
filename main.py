import ccxt
import pandas as pd

from strategy.price_action import generate_signal
from telegram.notifier import send_signal
from utils.state import already_signaled, mark_signaled

exchange = ccxt.binance()

PAIRS = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]


def fetch_ohlcv(symbol, timeframe, limit=120):
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(
        data, columns=["time", "open", "high", "low", "close", "volume"]
    )
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df.set_index("time", inplace=True)
    return df


def run():
    for pair in PAIRS:
        df_15m = fetch_ohlcv(pair, "15m")
        df_1h = fetch_ohlcv(pair, "1h")

        signal = generate_signal(df_15m, df_1h)
        if not signal:
            continue

        candle_time = signal["candle_time"]

        if already_signaled(pair, candle_time):
            continue

        send_signal(pair, signal)
        mark_signaled(pair, candle_time)


if __name__ == "__main__":
    run()
