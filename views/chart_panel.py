from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf

from services import mt5_service
from config import TIMEFRAME


class ChartPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        # Cria a figura e o canvas para exibir o gráfico
        self.fig, self.ax = plt.subplots(figsize=(8, 5))
        self.canvas = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas)

        self.current_symbol = None

    def update_chart(self, symbol):
        self.current_symbol = symbol
        self.ax.clear()

        rates = mt5_service.copy_rates(symbol, TIMEFRAME, 50)
        if rates is not None and len(rates) > 0:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True)
            df.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low',
                'close': 'Close', 'tick_volume': 'Volume'
            }, inplace=True)
            mpf.plot(df, type='candle', style='charles', ax=self.ax, volume=False)
            self.ax.set_title(f"{symbol} - Live Chart")
        else:
            self.ax.text(0.5, 0.5, "No data available", ha='center', va='center')

        self.canvas.draw()
