from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox, QSpinBox
)
from PyQt5.QtCore import QDateTime

class AIControlWidget(QWidget):
    def __init__(self, on_collect_data, on_train_model, on_save_model, on_load_model, get_model_status):
        super().__init__()

        self.on_collect_data = on_collect_data
        self.on_train_model = on_train_model
        self.on_save_model = on_save_model
        self.on_load_model = on_load_model
        self.get_model_status = get_model_status

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("⚙️ Controle da IA"))

        # Seletor de símbolo
        self.symbol_selector = QComboBox()
        self.symbol_selector.addItems(["EURUSD", "USDJPY", "GBPUSD"])  # Pode ser dinâmico depois
        self.layout.addWidget(QLabel("Símbolo para IA:"))
        self.layout.addWidget(self.symbol_selector)

        # Botões principais
        self.collect_button = QPushButton("📥 Coletar Dados")
        self.collect_button.clicked.connect(self.handle_collect_data)
        self.layout.addWidget(self.collect_button)

        self.train_button = QPushButton("🧠 Treinar IA")
        self.train_button.clicked.connect(self.handle_train_model)
        self.layout.addWidget(self.train_button)

        self.save_button = QPushButton("💾 Salvar Modelo")
        self.save_button.clicked.connect(self.on_save_model)
        self.layout.addWidget(self.save_button)

        self.load_button = QPushButton("📂 Carregar Modelo")
        self.load_button.clicked.connect(self.on_load_model)
        self.layout.addWidget(self.load_button)

        # Status
        self.status_label = QLabel("📊 Status: IA não treinada.")
        self.layout.addWidget(self.status_label)

        self.update_status_label()

        # ✅ NOVO: Campo para escolher quantidade de velas
        self.candles_spinbox = QSpinBox()
        self.candles_spinbox.setRange(20, 1000)
        self.candles_spinbox.setValue(100)
        self.candles_spinbox.setSuffix(" velas")
        self.layout.addWidget(QLabel("Velas p/ Análise IA"))
        self.layout.addWidget(self.candles_spinbox)

    def handle_collect_data(self):
        symbol = self.symbol_selector.currentText()
        self.on_collect_data(symbol)
        QMessageBox.information(self, "Coleta Concluída", f"Dados coletados para {symbol}.")

    def handle_train_model(self):
        symbol = self.symbol_selector.currentText()
        self.on_train_model(symbol)
        self.update_status_label()
        QMessageBox.information(self, "IA Treinada", f"Modelo treinado com sucesso para {symbol}.")

    def update_status_label(self):
        status = self.get_model_status()
        self.status_label.setText(f"📊 Status: {status}")

    def get_candles_count(self):
        return self.candles_spinbox.value()
