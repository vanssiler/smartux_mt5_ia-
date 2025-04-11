import pandas as pd
from utils.indicators import compute_rsi, compute_sma, compute_ema, compute_pct_change

def generate_features(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    # Cálculo de indicadores
    df["rsi"] = compute_rsi(df)
    df["sma_10"] = compute_sma(df, 10)
    df["sma_50"] = compute_sma(df, 50)
    df["ema_10"] = compute_ema(df, 10)
    df["pct_change"] = compute_pct_change(df)

    # Geração de target: sinal de trade
    df["future_close"] = df["close"].shift(-3)
    df["target"] = df.apply(lambda row: "Buy" if row["future_close"] > row["close"] * 1.001
                            else ("Sell" if row["future_close"] < row["close"] * 0.999 else "Hold"), axis=1)

    df.dropna(inplace=True)
    df.to_csv(output_csv, index=False)
    print(f"Arquivo gerado com sucesso: {output_csv}")

if __name__ == "__main__":
    generate_features("EURUSD_m5.csv", "EURUSD_m5_features.csv")