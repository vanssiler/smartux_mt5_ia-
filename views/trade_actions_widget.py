from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

class TradeActionsWidget(QWidget):
    def __init__(self, on_analyze, on_buy, on_sell):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Label de status
        self.status_label = QLabel("Status: Aguardando...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        # Botão de Análise
        self.analyze_button = QPushButton("🔍 Analisar")
        self.analyze_button.clicked.connect(on_analyze)
        self.layout.addWidget(self.analyze_button)

        # Botão de Compra
        self.buy_button = QPushButton("🟢 Comprar")
        self.buy_button.clicked.connect(on_buy)
        self.layout.addWidget(self.buy_button)

        # Botão de Venda
        self.sell_button = QPushButton("🔴 Vender")
        self.sell_button.clicked.connect(on_sell)
        self.layout.addWidget(self.sell_button)

    def update_status(self, status_text):
        self.status_label.setText(f"Status: {status_text}")
