
import os
import joblib
import pandas as pd
import numpy as np
import ta
from sklearn.ensemble import RandomForestClassifier
from services import mt5_service
from utils.feature_engineering import add_features, add_labels


class MLController:
    def __init__(self):
        self.model = None
        self.last_trained = None
        self.feature_names = []
        self.current_symbol = None

    def get_model_filename(self, symbol):
        return os.path.join("data", f"model_{symbol.upper()}.pkl")

    def predict_signal(self, df):
        try:
            expected_features = self.feature_names
            if not expected_features:
                raise ValueError("⚠️ Features não carregadas.")

            missing = [col for col in expected_features if col not in df.columns]
            if missing:
                raise ValueError(f"🧪 Colunas faltando para previsão: {missing}")

            X = df[expected_features].dropna()
            if X.empty:
                raise ValueError("🧪 Dados de entrada estão vazios após dropna.")

            X_final = X.tail(1)
            print(f"[DEBUG] X_final usado na previsão:\n{X_final}")
            y_pred = self.model.predict(X_final)
            print(f"[DEBUG] Previsão concluída: {y_pred}")
            return y_pred
        except Exception as e:
            print(f"[IA] Erro ao prever: {e}")
            return None

    def load_model(self, symbol):
        try:
            model_path = self.get_model_filename(symbol)
            data = joblib.load(model_path)
            if isinstance(data, dict):
                self.model = data.get("model")
                self.feature_names = data.get("feature_names", [])
                self.last_trained = data.get("last_trained")
                self.current_symbol = symbol
            else:
                self.model = data
                self.feature_names = []
            print(f"✅ Modelo IA carregado para {symbol}")
        except FileNotFoundError:
            print(f"⚠️ Nenhum modelo IA encontrado para {symbol}")

    def save_model(self, symbol):
        if self.model:
            model_path = self.get_model_filename(symbol)
            joblib.dump({
                "model": self.model,
                "feature_names": self.feature_names,
                "last_trained": self.last_trained
            }, model_path)
            print(f"💾 Modelo salvo como {model_path}")

    def train_model(self, symbol):
        print(f"🔄 Treinando IA real com dados de {symbol}...")
        df = mt5_service.get_symbol_data(symbol, n=300)
        if df is None or df.empty:
            print("❌ Sem dados para treinar.")
            return

        df = add_features(df)
        df = add_labels(df)

        feature_cols = [
            'open', 'high', 'low', 'close', 'tick_volume', 'real_volume',
            'macd', 'macd_signal', 'macd_diff',
            'boll_upper', 'boll_lower', 'boll_bandwidth',
            'atr', 'rsi', 'ema_10', 'adx', 'pct_change'
        ]

        df.dropna(inplace=True)
        X = df[feature_cols]
        y = df["target"]
        print(f"[DEBUG] Classes únicas no y: {y.unique()} ({len(y.unique())} classes)")
        if len(y.unique()) < 2:
            print("⚠️ Não é possível treinar IA com menos de 2 classes distintas no target.")
            return

        self.model = RandomForestClassifier()
        X_named = pd.DataFrame(X, columns=feature_cols)
        self.model.fit(X_named, y)
        self.feature_names = feature_cols
        self.last_trained = pd.Timestamp.now()

        self.save_model(symbol)
        print("✅ Modelo treinado com sucesso")

    def get_status(self):
        if self.model:
            time_str = self.last_trained.strftime("%d/%m %H:%M") if self.last_trained else "Desconhecido"
            return f"Modelo para {self.current_symbol} - último treino: {time_str}"
        return "IA não carregada"

    def prepare_features(self, df):
        df = df.copy()
        expected_cols = ['open', 'high', 'low', 'close', 'tick_volume', 'real_volume']
        for col in expected_cols:
            if col not in df.columns:
                df[col] = 0
        df = add_features(df)
        print(f"[DEBUG] Dados após aplicar indicadores: {df.shape}")
        if df.empty or df.shape[0] < 5:
            raise ValueError("🧪 Nenhum dado válido após aplicar os indicadores técnicos.")
        return df

    def predict(self, df):
        try:
            print("[DEBUG] Previsão iniciada - shape de entrada:", df.shape)
            print("[DEBUG] Iniciando previsão com MLController")

            if self.model is None:
                raise ValueError("❌ Nenhum modelo carregado.")

            df = self.prepare_features(df)
            print("[DEBUG] Shape após prepare_features:", df.shape)

            missing = set(self.feature_names) - set(df.columns)
            if missing:
                raise ValueError(f"🧪 Dados incompletos. Faltam: {missing}")

            print("[DEBUG] Colunas disponíveis:", df.columns.tolist())
            print("[DEBUG] Features esperadas:", self.feature_names)

            X = df[self.feature_names].dropna()
            if X.empty:
                raise ValueError("🧪 Dados finais para previsão estão vazios após dropna.")

            print(f"[DEBUG] Shape de X para previsão: {X.shape}")
            preds = self.model.predict(X)
            preds = pd.Series(preds, index=X.index)

            print(f"[DEBUG] Previsão concluída: {preds.values}")
            return preds

        except Exception as e:
            print(f"[IA] Erro ao prever (DENTRO DO predict): {e}")
            return None
