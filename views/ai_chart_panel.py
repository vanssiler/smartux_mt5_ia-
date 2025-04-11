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
        # Prepara DataFrame
        df = df.tail(len(predictions)).copy()
        df["Prediction"] = predictions
        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)

        df = df[["open", "high", "low", "close", "tick_volume", "Prediction"]]
        df.rename(columns={"tick_volume": "volume"}, inplace=True)

        # Cria séries com sinais Buy e Sell (NaN nos outros pontos)
        buy_signals = pd.Series(index=df.index, dtype=float)
        sell_signals = pd.Series(index=df.index, dtype=float)

        for i, row in df.iterrows():
            if row["Prediction"] == 2:  # Buy
                buy_signals[i] = row["low"] * 0.995
            elif row["Prediction"] == 0:  # Sell
                sell_signals[i] = row["high"] * 1.005
            else:
                buy_signals[i] = None
                sell_signals[i] = None

        addplots = [
            mpf.make_addplot(buy_signals, type='scatter', marker='^', color='green', markersize=120, panel=0),
            mpf.make_addplot(sell_signals, type='scatter', marker='v', color='red', markersize=120, panel=0),
        ]

        # Cria a nova figura
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

        # Remove canvas antigo, se existir
        if self.canvas:
            self.layout.removeWidget(self.canvas)
            self.canvas.setParent(None)

        self.canvas = FigureCanvas(fig)
        self.layout.addWidget(self.canvas)
        self.canvas.draw()
