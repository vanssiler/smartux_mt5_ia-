# data/collect_mt5_data.py

import os
import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime

# === CONFIG ===
SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M5  # 5-minute candles
BARS = 5000                   # Number of candles to fetch
OUTPUT_FOLDER = "data"
OUTPUT_FILE = f"{SYMBOL}_m5.csv"

# === INIT METATRADER ===
print(f"Connecting to MetaTrader 5...")
if not mt5.initialize():
    print(f"❌ Initialization failed: {mt5.last_error()}")
    exit()

# === FETCH HISTORICAL DATA ===
print(f"Fetching {BARS} candles for {SYMBOL}...")
rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, BARS)
mt5.shutdown()

if rates is None:
    print("❌ Failed to fetch rates.")
    exit()

# === FORMAT DATAFRAME ===
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df['symbol'] = SYMBOL

# === SAVE TO CSV ===
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
df.to_csv(output_path, index=False)

print(f"✅ Data saved to: {output_path}")
print(df.head())
