
import pandas as pd
from datetime import timedelta
from utils.feature_engineering import add_features

class SmartuxAgent:
    def __init__(self, ml_controller):
        self.ml_controller = ml_controller

    def analyze(self, symbol, df=None):
        if df is None or df.empty:
            raise ValueError("📉 Dados ausentes para análise com IA.")

        if len(df) < 60:
            raise ValueError("📉 Dados insuficientes para IA (mínimo 60 registros).")

        df = add_features(df)

        if self.ml_controller.feature_names is None:
            raise ValueError("📊 Modelo IA não possui lista de features esperadas.")

        df_recent = df.tail(100).copy()
        print("[DEBUG] df_recent shape:", df_recent.shape)
        df_pred = df_recent[self.ml_controller.feature_names].copy()
        print("[DEBUG] df_pred shape:", df_pred.shape)
        print("[DEBUG] Últimas linhas de df_pred:", df_pred.tail(3))

        df_pred = df_pred.dropna()
        if df_pred.empty or df_pred.shape[0] < 1:
            raise ValueError("🧪 Dados para previsão estão vazios ou incompletos após dropna.")

        preds = self.ml_controller.predict_signal(df_pred)
        if preds is None or len(preds) < 1:
            raise ValueError("❌ Não foi possível gerar uma previsão com IA.")

        prediction = preds[-1]

        # Confiança da previsão com segurança máxima
        confidence = "-"
        if hasattr(self.ml_controller.model, "predict_proba"):
            try:
                df_pred_clean = df_pred[self.ml_controller.feature_names].dropna()
                if df_pred_clean.empty:
                    raise ValueError("⚠️ df_pred vazio após dropna para predict_proba.")

                # Garantir que seja um DataFrame com feature names
                X_proba = pd.DataFrame(df_pred_clean, columns=self.ml_controller.feature_names)
                proba_values = self.ml_controller.model.predict_proba(X_proba)
                proba = proba_values[-1]
                confidence_value = proba[prediction]
                confidence = f"{confidence_value * 100:.2f}%"
            except Exception as e:
                print(f"[IA] Erro ao calcular confiança: {e}")

        last_time = df_recent["time"].iloc[-1] if "time" in df_recent.columns else None
        timeframe = timedelta(minutes=5)
        estimated_time = (last_time + timeframe).strftime("%H:%M") if last_time else "Desconhecido"

        label_map = {0: "Sell", 1: "Hold", 2: "Buy"}
        label = label_map.get(prediction, "Indefinido")

        return {
            "label": label,
            "confidence": confidence,
            "time": estimated_time,
            "predictions": preds
        }

    def auto_trade_decision(self, symbol, df):
        if df is None or df.empty:
            raise ValueError("📉 Dados ausentes para auto trade.")

        if len(df) < 60:
            raise ValueError("📉 Dados insuficientes para IA (mínimo 60 registros).")

        df = add_features(df)

        if self.ml_controller.feature_names is None or not self.ml_controller.feature_names:
            raise ValueError("📊 IA ainda não foi treinada ou não possui features definidas.")

        df_recent = df.tail(100).copy()
        df_pred = df_recent[self.ml_controller.feature_names].dropna()

        if df_pred.empty or df_pred.shape[0] < 1:
            raise ValueError("🧪 Dados insuficientes após o cálculo de features.")

        X_last = df_pred.tail(1)
        print(f"[AUTO_TRADE] Última entrada para previsão:\n{X_last}")

        try:
            prediction = self.ml_controller.model.predict(X_last)[0]
            print(f"[AUTO_TRADE] Previsão IA: {prediction}")
        except Exception as e:
            raise ValueError(f"❌ Erro ao prever com IA: {e}")

        direction_map = {0: "sell", 1: None, 2: "buy"}
        direction = direction_map.get(prediction, None)

        if direction is None:
            print("🔕 IA recomenda: Hold")
            return None

        atr_value = df_recent["atr"].iloc[-1] if "atr" in df_recent.columns else 0.001
        atr_value = max(atr_value, 0.0001)

        risk_reward_ratio = 2
        sl_usd = round(atr_value * 100000, 2)
        tp_usd = round(sl_usd * risk_reward_ratio, 2)

        return {
            "direction": direction,
            "sl_usd": sl_usd,
            "tp_usd": tp_usd
        }
