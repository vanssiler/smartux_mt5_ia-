import pandas as pd
import os
from controllers.ml_controller import MLController

print("🔧 Carregando dados...")

# 📂 Carregar dataset com features expandidas
file_path = os.path.join("data", "EURUSD_m5_features.csv")
df = pd.read_csv(file_path)

# 🧹 Limpeza de colunas desnecessárias
df.drop(columns=["time"], errors="ignore", inplace=True)

# 🎯 Verifica se 'target' está presente
if "target" not in df.columns:
    raise ValueError("⚠️ Coluna 'target' ausente no dataset. Geração de labels necessária.")

print("📊 Colunas disponíveis:", df.columns.tolist())
print(f"📈 Total de amostras: {len(df)}")

# 🧠 Treinar modelo
print("🧠 Treinando modelo com IA...")

ml = MLController()
ml.train(df)
