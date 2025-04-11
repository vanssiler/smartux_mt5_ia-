from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QComboBox,
    QLabel, QPushButton
)

class TradeInputWidget(QWidget):
    def __init__(self, on_buy, on_sell):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.volume_input = QLineEdit("1")
        self.sl_input = QLineEdit("10")
        self.tp_input = QLineEdit("2")
        self.deviation_input = QComboBox()
        self.deviation_input.addItems(["10", "20", "30", "50", "100"])
        self.comment_input = QLineEdit()

        self.layout.addWidget(QLabel("💵 Trade Value (USD):"))
        self.layout.addWidget(self.volume_input)

        self.layout.addWidget(QLabel("❌ Stop Loss (USD):"))
        self.layout.addWidget(self.sl_input)

        self.layout.addWidget(QLabel("✅ Take Profit (USD):"))
        self.layout.addWidget(self.tp_input)

        self.layout.addWidget(QLabel("🎯 Deviation:"))
        self.layout.addWidget(self.deviation_input)

        self.layout.addWidget(QLabel("📝 Comment:"))
        self.layout.addWidget(self.comment_input)

        self.buy_button = QPushButton("Buy")
        self.buy_button.clicked.connect(on_buy)

        self.sell_button = QPushButton("Sell")
        self.sell_button.clicked.connect(on_sell)

        self.layout.addWidget(self.buy_button)
        self.layout.addWidget(self.sell_button)
