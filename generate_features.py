import os
import pandas as pd
from services import mt5_service
from utils.feature_engineering import add_features, add_labels

# === CONFIGURAÇÕES ===
symbol = "EURUSD"
timeframe = "M5"
bars = 500  # você pode aumentar se quiser mais histórico

print("📥 Coletando dados do MetaTrader 5...")
df = mt5_service.get_symbol_data(symbol, n=bars)

if df.empty:
    print("❌ Erro: Dados não encontrados.")
    exit()

print("📊 Dados brutos recebidos:", df.shape)

# === GERAÇÃO DE FEATURES E RÓTULOS ===
print("⚙️ Adicionando indicadores técnicos...")
df = add_features(df)

print("🏷️ Adicionando coluna 'target'...")
df = add_labels(df)

# === SALVAR CSV ===
os.makedirs("data", exist_ok=True)
filename = f"data/{symbol}_{timeframe.lower()}_features.csv"
df.to_csv(filename, index=False)

print(f"✅ CSV com features salvo em: {filename}")
