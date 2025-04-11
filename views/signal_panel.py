from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton


class SignalPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.title_label = QLabel("🔍 Sinais de Análise")
        self.chart_label = QLabel("📉 Chart: ---")
        self.news_label = QLabel("📰 News: ---")
        self.combined_label = QLabel("📊 Combined: ---")
        self.ai_label = QLabel("🤖 AI Signal: ---")
        self.status_label = QLabel("")

        self.analyze_button = QPushButton("Executar Análise")

        layout.addWidget(self.title_label)
        layout.addWidget(self.chart_label)
        layout.addWidget(self.news_label)
        layout.addWidget(self.combined_label)
        layout.addWidget(self.ai_label)
        layout.addWidget(self.analyze_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def update_signals(self, chart_signal, news_signal, combined_signal, ai_signal="---"):
        self.chart_label.setText(f"📉 Chart: {chart_signal}")
        self.news_label.setText(f"📰 News: {news_signal}")
        self.combined_label.setText(f"📊 Combined: {combined_signal}")
        self.ai_label.setText(f"🤖 AI Signal: {ai_signal}")
        self.status_label.setText("✅ Análise concluída.")

    def set_status(self, text):
        self.status_label.setText(text)
