from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
import mplfinance as mpf


class AIChartPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.canvas = None  # O canvas será criado após o primeiro plot

    def plot_predictions(self, df, predictions):
        try:
            # 🚫 Verificações básicas
            if predictions is None or len(predictions) == 0:
                print("[IAChartPanel] ⚠️ Nenhuma previsão disponível para plotar.")
                return

            if df is None or df.empty:
                print("[IAChartPanel] ⚠️ DataFrame vazio.")
                return

            if len(predictions) > len(df):
                print("[IAChartPanel] ⚠️ Previsões maiores que os dados disponíveis.")
                return

            # Prepara DataFrame
            df = df.tail(len(predictions)).copy()
            df["Prediction"] = predictions
            df["time"] = pd.to_datetime(df["time"])
            df.set_index("time", inplace=True)

            # Valida colunas
            required_cols = ["open", "high", "low", "close", "tick_volume", "Prediction"]
            for col in required_cols:
                if col not in df.columns:
                    print(f"[IAChartPanel] ⚠️ Coluna ausente: {col}")
                    return

            df.rename(columns={"tick_volume": "volume"}, inplace=True)

            # ⚠️ Verifica se ainda está vazio após o processamento
            if df.empty:
                print("[IAChartPanel] ⚠️ DataFrame vazio após ajustes.")
                return

            # Cria sinais
            buy_signals = pd.Series(index=df.index, dtype=float)
            sell_signals = pd.Series(index=df.index, dtype=float)

            for i, row in df.iterrows():
                if row["Prediction"] == 2:
                    buy_signals[i] = row["low"] * 0.995
                elif row["Prediction"] == 0:
                    sell_signals[i] = row["high"] * 1.005

            # Verifica se há algum valor em buy/sell antes do plot
            if buy_signals.dropna().empty and sell_signals.dropna().empty:
                print("[IAChartPanel] ⚠️ Nenhum sinal de compra ou venda para exibir.")
                return

            addplots = [
                mpf.make_addplot(buy_signals, type='scatter', marker='^', color='green', markersize=120, panel=0),
                mpf.make_addplot(sell_signals, type='scatter', marker='v', color='red', markersize=120, panel=0),
            ]

            fig, _ = mpf.plot(
                df,
                type='candle',
                style='yahoo',
                volume=True,
                addplot=addplots,
                ylabel='Preço',
                returnfig=True,
                tight_layout=True,
                datetime_format='%H:%M'
            )

            if self.canvas:
                self.layout.removeWidget(self.canvas)
                self.canvas.setParent(None)

            self.canvas = FigureCanvas(fig)
            self.layout.addWidget(self.canvas)
            self.canvas.draw()

        except Exception as e:
            print(f"[IAChartPanel] ❌ Erro ao plotar gráfico: {e}")


