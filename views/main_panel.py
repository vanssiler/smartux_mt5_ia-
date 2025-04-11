from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSizePolicy
from PyQt5.QtCore import Qt

class MainPanel(QWidget):
    def __init__(self, on_analyze, on_buy, on_sell):
        super().__init__()

        self.on_analyze = on_analyze
        self.on_buy = on_buy
        self.on_sell = on_sell

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)

        # Status label
        self.status_label = QLabel("Status: Aguardando...")
        self.status_label.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)

        # Analisar
        self.analyze_button = QPushButton("🔍 Analisar")
        self.analyze_button.clicked.connect(self.on_analyze)
        layout.addWidget(self.analyze_button)

        # Comprar
        self.buy_button = QPushButton("🟢 Comprar")
        self.buy_button.clicked.connect(self.on_buy)
        layout.addWidget(self.buy_button)

        # Vender
        self.sell_button = QPushButton("🔴 Vender")
        self.sell_button.clicked.connect(self.on_sell)
        layout.addWidget(self.sell_button)

        # Estilização dos botões
        for btn in [self.analyze_button, self.buy_button, self.sell_button]:
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 18px;
                    padding: 12px;
                    border-radius: 10px;
                    background-color: #2e2e2e;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #444;
                }
            """)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.setLayout(layout)

    def update_status(self, message):
        self.status_label.setText(f"Status: {message}")
