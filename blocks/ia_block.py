from PyQt5.QtWidgets import QVBoxLayout, QLabel, QGroupBox
from views.chart_panel import ChartPanel
from views.symbol_selector import SymbolSelector
from views.signal_panel import SignalPanel
from views.ai_chart_panel import AIChartPanel


def create_ia_block(context):
    # Instanciar componentes
    context.chart_panel = ChartPanel()
    context.ai_chart_panel = AIChartPanel()
    context.symbol_selector = SymbolSelector()
    context.signal_panel = SignalPanel()

    # Conectar evento de símbolo
    context.symbol_selector.on_change(context.update_symbol)
    context.signal_panel.analyze_button.clicked.connect(context.run_analysis)

    # Layout vertical
    ia_layout = QVBoxLayout()
    ia_layout.addWidget(QLabel("\U0001F9E0 Análise com IA"))
    ia_layout.addWidget(context.symbol_selector)
    ia_layout.addWidget(context.chart_panel)
    ia_layout.addWidget(context.ai_chart_panel)
    ia_layout.addWidget(context.signal_panel)

    # Agrupamento com título
    ia_box = QGroupBox("Análise com Inteligência Artificial")
    ia_box.setLayout(ia_layout)

    return ia_box
