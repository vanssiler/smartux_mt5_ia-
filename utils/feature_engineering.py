import pandas as pd
import ta  # Technical Analysis library


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona indicadores técnicos ao DataFrame de candles.

    Espera colunas: ['open', 'high', 'low', 'close', 'tick_volume']

    Retorna o DataFrame com colunas extras:
    - RSI, SMA(10/50), EMA(10), % change
    - MACD (line, signal, diff)
    - Bollinger Bands (upper, lower, bandwidth)
    - ATR, ADX
    """
    df = df.copy()

    required = {"open", "high", "low", "close", "tick_volume"}
    if not required.issubset(df.columns):
        raise ValueError(f"❌ DataFrame precisa conter as colunas: {required}")

    # Indicadores básicos
    df["rsi"] = ta.momentum.RSIIndicator(close=df["close"]).rsi()
    df["sma_10"] = df["close"].rolling(window=10).mean()
    df["sma_50"] = df["close"].rolling(window=50).mean()
    df["ema_10"] = df["close"].ewm(span=10, adjust=False).mean()
    df["pct_change"] = df["close"].pct_change()

    # MACD
    macd = ta.trend.MACD(close=df["close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()

    # Bollinger Bands
    boll = ta.volatility.BollingerBands(close=df["close"], window=20, window_dev=2)
    df["boll_upper"] = boll.bollinger_hband()
    df["boll_lower"] = boll.bollinger_lband()
    df["boll_bandwidth"] = df["boll_upper"] - df["boll_lower"]

    # ATR
    atr = ta.volatility.AverageTrueRange(high=df["high"], low=df["low"], close=df["close"])
    df["atr"] = atr.average_true_range()

    # ADX
    adx = ta.trend.ADXIndicator(high=df["high"], low=df["low"], close=df["close"])
    df["adx"] = adx.adx()

    # Limpa linhas com NaN
    df.dropna(inplace=True)

    return df


def add_labels(df: pd.DataFrame, threshold: float = 0.0003) -> pd.DataFrame:
    """
    Adiciona a coluna 'target' com base na variação futura do preço.

    Labels:
    - 2 = Buy
    - 1 = Hold
    - 0 = Sell

    Args:
        df: DataFrame com coluna 'close'
        threshold: Mínima variação para classificar buy/sell

    Returns:
        DataFrame com coluna 'target'
    """
    df = df.copy()

    df["future_close"] = df["close"].shift(-5)
    df["delta"] = df["future_close"] - df["close"]

    def classify(change):
        if change > threshold:
            return 2  # Buy
        elif change < -threshold:
            return 0  # Sell
        else:
            return 1  # Hold

    df["target"] = df["delta"].apply(classify)

    df.drop(columns=["future_close", "delta"], inplace=True)
    df.dropna(inplace=True)

    return df
