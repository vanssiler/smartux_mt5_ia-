from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QHBoxLayout
)


class TradePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Volume (USD)
        self.volume_label = QLabel("Trade Value (USD):")
        self.volume_input = QLineEdit("100")
        self.estimated_volume_label = QLabel("Estimated Volume: ---")
        self.layout.addWidget(self.volume_label)
        self.layout.addWidget(self.volume_input)
        self.layout.addWidget(self.estimated_volume_label)

        # SL (USD)
        self.sl_label = QLabel("Stop Loss (USD):")
        self.sl_input = QLineEdit("50")
        self.layout.addWidget(self.sl_label)
        self.layout.addWidget(self.sl_input)

        # TP (USD)
        self.tp_label = QLabel("Take Profit (USD):")
        self.tp_input = QLineEdit("50")
        self.layout.addWidget(self.tp_label)
        self.layout.addWidget(self.tp_input)

        # SL/TP Preview
        self.sl_price_label = QLabel("SL Price: ---")
        self.tp_price_label = QLabel("TP Price: ---")
        self.layout.addWidget(self.sl_price_label)
        self.layout.addWidget(self.tp_price_label)

        # Deviation
        self.deviation_label = QLabel("Deviation:")
        self.deviation_input = QComboBox()
        self.deviation_input.addItems(["0", "5", "10", "20", "50"])
        self.deviation_input.setCurrentText("50")
        self.layout.addWidget(self.deviation_label)
        self.layout.addWidget(self.deviation_input)

        # Comment
        self.comment_label = QLabel("Comment:")
        self.comment_input = QLineEdit("")
        self.layout.addWidget(self.comment_label)
        self.layout.addWidget(self.comment_input)

        # Buttons
        self.button_layout = QHBoxLayout()
        self.buy_button = QPushButton("Buy")
        self.sell_button = QPushButton("Sell")
        self.button_layout.addWidget(self.buy_button)
        self.button_layout.addWidget(self.sell_button)
        self.layout.addLayout(self.button_layout)
