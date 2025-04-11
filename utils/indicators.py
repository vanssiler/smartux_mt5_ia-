import pandas as pd

def compute_rsi(data, window=14):
    delta = data["close"].diff()
    gain = delta.clip(lower=0).rolling(window=window).mean()
    loss = -delta.clip(upper=0).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_sma(data, window=14):
    return data["close"].rolling(window=window).mean()

def compute_ema(data, window=14):
    return data["close"].ewm(span=window, adjust=False).mean()

def compute_pct_change(data):
    return data["close"].pct_change()