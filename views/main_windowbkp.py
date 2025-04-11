from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QApplication, QMessageBox
from PyQt5.QtCore import QTimer
import MetaTrader5 as mt5
import pandas as pd

from views.chart_panel import ChartPanel
from views.symbol_selector import SymbolSelector
from views.trade_panel import TradePanel
from views.signal_panel import SignalPanel
from views.account_panel import AccountPanel
from views.positions_panel import PositionsPanel
from views.ai_chart_panel import AIChartPanel  # ✅ Novo painel

from controllers import trade_controller, analysis_controller
from controllers.ml_controller import MLController
from services import mt5_service


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartUx MT5 Dashboard")
        self.setGeometry(100, 100, 1450, 800)

        mt5_service.initialize()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Área de análise IA (esquerda)
        self.chart_panel = ChartPanel()
        self.ai_chart_panel = AIChartPanel()

        self.symbol_selector = SymbolSelector()
        self.symbol_selector.on_change(self.update_symbol)

        self.signal_panel = SignalPanel()
        self.signal_panel.analyze_button.clicked.connect(self.run_analysis)
        self.signal_panel.analyze_button.setStyleSheet("font-weight: bold; background-color: #E0FFE0;")

        ia_layout = QVBoxLayout()
        ia_layout.addWidget(QLabel("🧠 Análise com IA"))
        ia_layout.addWidget(self.symbol_selector)
        ia_layout.addWidget(self.chart_panel)
        ia_layout.addWidget(self.ai_chart_panel)
        ia_layout.addWidget(self.signal_panel)

        ia_box = QGroupBox("Análise de Mercado com IA")
        ia_box.setLayout(ia_layout)
        self.main_layout.addWidget(ia_box, 3)

        # Área de operações manuais (direita)
        self.trade_panel = TradePanel()
        self.trade_panel.buy_button.setStyleSheet("font-weight: bold; background-color: #D0F0FF;")
        self.trade_panel.sell_button.setStyleSheet("font-weight: bold; background-color: #FFD0D0;")

        self.account_panel = AccountPanel()
        self.positions_panel = PositionsPanel()
        self.positions_panel.close_button.clicked.connect(self.close_selected_position)

        self.trade_panel.buy_button.clicked.connect(lambda: self.place_order("buy"))
        self.trade_panel.sell_button.clicked.connect(lambda: self.place_order("sell"))

        operations_layout = QVBoxLayout()
        operations_layout.addWidget(QLabel("🛠️ Operações Manuais"))
        operations_layout.addWidget(self.trade_panel)
        operations_layout.addWidget(self.account_panel)
        operations_layout.addWidget(self.positions_panel)

        operations_box = QGroupBox("Painel de Controle Manual")
        operations_box.setLayout(operations_layout)
        self.main_layout.addWidget(operations_box, 2)

        self.current_symbol = self.symbol_selector.get_selected_symbol()
        self.chart_panel.update_chart(self.current_symbol)

        self.timer_dashboard = QTimer()
        self.timer_dashboard.timeout.connect(self.update_dashboard)
        self.timer_dashboard.start(5000)

        self.timer_chart = QTimer()
        self.timer_chart.timeout.connect(self.refresh_chart)
        self.timer_chart.start(2000)

        self.positions_panel.refresh_positions()

        self.ml_controller = MLController()
        try:
            self.ml_controller.load_model()
        except Exception as e:
            print(f"⚠️ Nenhum modelo encontrado, IA inativa até treinamento.\n{e}")

    def update_dashboard(self):
        account_info = mt5_service.get_account_info()
        self.account_panel.update_account_info(account_info)

    def refresh_chart(self):
        self.chart_panel.update_chart(self.current_symbol)

    def update_symbol(self, symbol):
        self.current_symbol = symbol
        mt5_service.select_symbol(symbol)
        self.chart_panel.update_chart(symbol)
    def run_analysis(self):
        self.signal_panel.set_status("Analyzing...")
        QApplication.processEvents()

        chart_signal = analysis_controller.analyze_chart(self.current_symbol)
        news_signal = analysis_controller.analyze_news(self.current_symbol)
        combined = analysis_controller.combine_signals(chart_signal, news_signal)

        ai_signal = "IA Desativada"
        try:
            # Importa a função para calcular os indicadores técnicos
            from utils.feature_engineering import add_features

            # Coleta mais dados (use n maior para permitir cálculos de indicadores)
            df = mt5_service.get_symbol_data(self.current_symbol, n=150)

            if df.empty or len(df) < 60:
                raise ValueError("Dados insuficientes para IA.")

            # Aplica os indicadores técnicos (as mesmas usadas no treinamento)
            df = add_features(df)

            # Seleciona as últimas 50 linhas com os indicadores aplicados
            df_recent = df.tail(50).copy()

            # Filtra somente as features esperadas pelo modelo
            if self.ml_controller.feature_names is None:
                raise ValueError("Feature names não definidos no modelo.")
            df_for_pred = df_recent[self.ml_controller.feature_names]

            print("✅ Colunas enviadas ao modelo:", df_for_pred.columns.tolist())
            print("✅ Shape final:", df_for_pred.shape)

            predictions = self.ml_controller.predict(df_for_pred)

            label_map = {0: "Sell", 1: "Hold", 2: "Buy"}
            ai_signal = label_map.get(predictions[-1], "Indefinido")

            # Atualiza o gráfico de IA (pode usar o DataFrame original com indicadores para plotagem)
            self.ai_chart_panel.plot_predictions(df.tail(50), predictions)

        except Exception as e:
            print(f"[IA] Erro ao prever: {e}")
            ai_signal = "Erro"

        self.signal_panel.update_signals(chart_signal, news_signal, combined, ai_signal)



    # def run_analysis(self):
        # self.signal_panel.set_status("Analyzing...")
        # QApplication.processEvents()

        # chart_signal = analysis_controller.analyze_chart(self.current_symbol)
        # news_signal = analysis_controller.analyze_news(self.current_symbol)
        # combined = analysis_controller.combine_signals(chart_signal, news_signal)

        # ai_signal = "IA Desativada"
        # try:
        #     df = mt5_service.get_symbol_data(self.current_symbol, n=100)

        #     if df.empty or len(df) < 50:
        #         raise ValueError("Dados insuficientes para IA.")

        #     df_recent = df.tail(50).copy()

        #     # Remove colunas que não são features esperadas pela IA
        #     df_recent = df_recent.drop(columns=[
        #         col for col in df_recent.columns
        #         if col.lower() in ["target", "time", "prediction"]
        #     ], errors="ignore")

        #     if df_recent.empty or df_recent.shape[1] == 0:
        #         raise ValueError("DataFrame sem colunas válidas para IA.")

        #     predictions = self.ml_controller.predict(df_recent)

        #     label_map = {0: "Sell", 1: "Hold", 2: "Buy"}
        #     ai_signal = label_map.get(predictions[-1], "Indefinido")

        #     # ✅ Atualiza gráfico de IA com dados brutos (com time) e previsões
        #     self.ai_chart_panel.plot_predictions(df.tail(50), predictions)

        # except Exception as e:
        #     print(f"[IA] Erro ao prever: {e}")
        #     ai_signal = "Erro"
        

        self.signal_panel.update_signals(chart_signal, news_signal, combined, ai_signal)


    def place_order(self, direction):
        try:
            usd_volume = float(self.trade_panel.volume_input.text())
            usd_sl = float(self.trade_panel.sl_input.text())
            usd_tp = float(self.trade_panel.tp_input.text())
            deviation = int(self.trade_panel.deviation_input.currentText())
            comment = self.trade_panel.comment_input.text()
        except ValueError:
            QMessageBox.critical(self, "Input Error", "Invalid numeric input.")
            return

        constants = mt5_service.get_constants()
        order_type = constants["ORDER_TYPE_BUY"] if direction == "buy" else constants["ORDER_TYPE_SELL"]

        success, message = trade_controller.place_order(
            symbol=self.current_symbol,
            action_type=order_type,
            usd_volume=usd_volume,
            usd_sl=usd_sl,
            usd_tp=usd_tp,
            deviation=deviation,
            comment=comment
        )

        if success:
            QMessageBox.information(self, "Success", message)
            self.positions_panel.refresh_positions()
        else:
            QMessageBox.critical(self, "Trade Failed", message)

    def close_selected_position(self):
        ticket = self.positions_panel.get_selected_ticket()
        if ticket is None:
            QMessageBox.warning(self, "No Selection", "Please select a position to close.")
            return

        success, message = mt5_service.close_position(ticket)
        if success:
            QMessageBox.information(self, "Closed", message)
            self.positions_panel.refresh_positions()
        else:
            QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        mt5_service.shutdown()
        event.accept()
