import pandas as pd
import numpy as np


def detect_swings(df, lookback=3):
    highs = []
    lows = []

    for i in range(lookback, len(df) - lookback):
        if df['high'].iloc[i] == max(df['high'].iloc[i-lookback:i+lookback+1]):
            highs.append((df.index[i], df['high'].iloc[i]))

        if df['low'].iloc[i] == min(df['low'].iloc[i-lookback:i+lookback+1]):
            lows.append((df.index[i], df['low'].iloc[i]))

    return highs, lows


def market_structure(df):
    highs, lows = detect_swings(df)

    if len(highs) < 2 or len(lows) < 2:
        return None, None, None

    last_high = highs[-1][1]
    last_low = lows[-1][1]

    # Uptrend
    if highs[-1][1] > highs[-2][1] and lows[-1][1] > lows[-2][1]:
        return "BUY", last_low, last_high

    # Downtrend
    if highs[-1][1] < highs[-2][1] and lows[-1][1] < lows[-2][1]:
        return "SELL", last_low, last_high

    return None, None, None


def liquidity_sweep(df, direction, support, resistance):
    candle = df.iloc[-1]

    if direction == "BUY":
        return candle.low < support and candle.close > support

    if direction == "SELL":
        return candle.high > resistance and candle.close < resistance

    return False


def impulse_candle(df, multiplier=1.5):
    body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
    avg_body = np.mean(abs(df['close'] - df['open']).iloc[-11:-1])
    return body >= avg_body * multiplier


def generate_signal(df_15m, df_1h):
    direction, support, resistance = market_structure(df_1h)
    if not direction:
        return None

    if not liquidity_sweep(df_15m, direction, support, resistance):
        return None

    if not impulse_candle(df_15m):
        return None

    entry = df_15m['close'].iloc[-1]

    if direction == "BUY":
        sl = df_15m['low'].iloc[-1]
        tp = entry + (entry - sl) * 2
    else:
        sl = df_15m['high'].iloc[-1]
        tp = entry - (sl - entry) * 2

    return {
        "direction": direction,
        "entry": round(entry, 2),
        "sl": round(sl, 2),
        "tp": round(tp, 2),
        "candle_time": str(df_15m.index[-1])
    }

