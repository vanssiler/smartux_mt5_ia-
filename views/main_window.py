from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QApplication, QMessageBox, QLabel, QGroupBox
from PyQt5.QtCore import QTimer
import MetaTrader5 as mt5
import pandas as pd

from views.chart_panel import ChartPanel
from views.symbol_selector import SymbolSelector
from views.signal_panel import SignalPanel
from views.account_panel import AccountPanel
from views.positions_panel import PositionsPanel
from views.ai_chart_panel import AIChartPanel
from views.trade_actions_widget import TradeActionsWidget
from views.trade_input_widget import TradeInputWidget
from views.account_info_widget import AccountInfoWidget
from views.open_positions_widget import OpenPositionsWidget
from views.ai_control_widget import AIControlWidget

from controllers import trade_controller, analysis_controller
from controllers.ml_controller import MLController
from services import mt5_service
from agents.agent_controller import SmartuxAgent

from PyQt5.QtWidgets import QPushButton



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SmartUx MT5 Dashboard")
        self.setGeometry(100, 100, 1600, 850)

        from styles.theme import DARK_THEME
        self.setStyleSheet(DARK_THEME)

        mt5_service.initialize()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Área IA (Esquerda)
        self.chart_panel = ChartPanel()
        self.ai_chart_panel = AIChartPanel()
        self.symbol_selector = SymbolSelector()
        self.symbol_selector.on_change(self.update_symbol)
        self.current_symbol = self.symbol_selector.get_selected_symbol()

        self.signal_panel = SignalPanel()
        self.signal_panel.analyze_button.clicked.connect(self.run_analysis)

        from blocks.ia_block import create_ia_block
        self.main_layout.addWidget(create_ia_block(self), 3)

        # Painel Principal de Operações (Centro)
        self.main_panel = TradeActionsWidget(
            on_analyze=self.run_analysis,
            on_buy=lambda: self.place_order("buy"),
            on_sell=lambda: self.place_order("sell")
        )

        main_panel_box = QGroupBox("Ações Rápidas")
        main_panel_layout = QVBoxLayout()
        main_panel_layout.addWidget(self.main_panel)

        # Inicializa IA e carrega o modelo do símbolo atual
        self.ml_controller = MLController()
        try:
            self.ml_controller.load_model(self.current_symbol)
        except Exception as e:
            print(f"⚠️ Nenhum modelo encontrado para {self.current_symbol}, IA inativa até treinamento.\n{e}")


        self.smartux_agent = SmartuxAgent(self.ml_controller)

        self.ai_control_widget = AIControlWidget(
            on_collect_data=self.collect_data_for_ai,
            on_train_model=self.train_model_for_ai,
            on_save_model=self.save_model,
            on_load_model=self.load_model,
            get_model_status=self.get_model_status
        )
        main_panel_layout.addWidget(self.ai_control_widget)

        self.auto_trade_button = QPushButton("🤖 Auto Trade")
        self.auto_trade_button.clicked.connect(self.auto_trade)
        main_panel_layout.addWidget(self.auto_trade_button)


        main_panel_box.setLayout(main_panel_layout)
        self.main_layout.addWidget(main_panel_box, 1)

        # Painel Direito - Operações Manuais Separadas
        right_panel = QVBoxLayout()

        self.trade_panel = TradeInputWidget(
            on_buy=lambda: self.place_order("buy", manual=True),
            on_sell=lambda: self.place_order("sell", manual=True)
        )
        right_panel.addWidget(self.trade_panel)

        self.account_panel = AccountInfoWidget()
        right_panel.addWidget(self.account_panel)

        self.positions_panel = OpenPositionsWidget(on_close_position=self.close_position_by_ticket)
        right_panel.addWidget(self.positions_panel)

        manual_ops_box = QGroupBox("Painel de Operações")
        manual_ops_box.setLayout(right_panel)
        self.main_layout.addWidget(manual_ops_box, 2)

        self.timer_dashboard = QTimer()
        self.timer_dashboard.timeout.connect(self.update_dashboard)
        self.timer_dashboard.start(5000)

        self.timer_chart = QTimer()
        self.timer_chart.timeout.connect(self.refresh_chart)
        self.timer_chart.start(2000)

        # Atualiza posições abertas a cada segundo
        self.timer_positions = QTimer()
        self.timer_positions.timeout.connect(self.refresh_positions)
        self.timer_positions.start(1000)  # 1 segundo


        positions = mt5_service.get_open_positions()
        self.positions_panel.refresh_positions(positions)

    def close_position_by_ticket(self, ticket):
        success, message = mt5_service.close_position(ticket)
        if success:
            QMessageBox.information(self, "Fechada", message)
        else:
            QMessageBox.critical(self, "Erro", message)


    def refresh_positions(self):
        positions = mt5_service.get_open_positions()
        self.positions_panel.refresh_positions(positions)

        account_info = mt5_service.get_account_info()
        if account_info:
            self.account_panel.update_account_info(account_info)


    def update_dashboard(self):
        self.refresh_positions()


    def refresh_chart(self):
        self.chart_panel.update_chart(self.current_symbol)

    def update_symbol(self, symbol):
        self.current_symbol = symbol
        mt5_service.select_symbol(symbol)
        self.chart_panel.update_chart(symbol)

    def run_analysis(self):
        self.main_panel.update_status("Analisando...")
        QApplication.processEvents()

        # Sinais técnicos e de notícia
        chart_signal = analysis_controller.analyze_chart(self.current_symbol)
        news_signal = analysis_controller.analyze_news(self.current_symbol)
        combined = analysis_controller.combine_signals(chart_signal, news_signal)

        ai_signal = "IA Desativada"
        try:
            # Verifica se o modelo está carregado
            if not self.ml_controller.model:
                raise ValueError("⚠️ Modelo IA não carregado.")

            # Coleta dados do ativo
            df = mt5_service.get_symbol_data(self.current_symbol, n=150)
            if df is None or df.empty:
                raise ValueError("❌ Dados ausentes para IA.")

            # Executa a previsão com IA
            result = self.smartux_agent.analyze(self.current_symbol, df)

            ai_signal = f"IA: {result['label']} ({result['confidence']}) até {result['time']}"
            if result["label"].lower() != "hold":
                self.ai_chart_panel.plot_predictions(df.tail(50), result["predictions"])


        except Exception as e:
            print(f"[IA] Análise ignorada: {e}")
            ai_signal = "IA: Inativa ou sem sinal"

        # Atualiza interface
        self.signal_panel.update_signals(chart_signal, news_signal, combined, ai_signal)
        self.main_panel.update_status(f"Sinal IA: {ai_signal}")


    def collect_data_for_ai(self, symbol):
        print(f"📥 Coletando dados para: {symbol}")
        # Aqui você pode chamar: self.ml_controller.collect_data(symbol)

    def train_model_for_ai(self, symbol):
        print(f"🧠 Treinando modelo para: {symbol}")
        self.ml_controller.train_model(symbol)

    def save_model(self):
        self.ml_controller.save_model(self.current_symbol)
        print("💾 Modelo salvo.")


    def load_model(self):
        self.ml_controller.load_model(self.current_symbol)
        print("📂 Modelo carregado.")


    def get_model_status(self):
        return self.ml_controller.get_status()

    def place_order(self, direction, manual=False):
        try:
            if manual:
                usd_volume = float(self.trade_panel.volume_input.text())
                usd_sl = float(self.trade_panel.sl_input.text())
                usd_tp = float(self.trade_panel.tp_input.text())
                deviation = int(self.trade_panel.deviation_input.currentText())
                comment = self.trade_panel.comment_input.text()
            else:
                usd_volume = 0.1
                usd_sl = 5
                usd_tp = 10
                deviation = 10
                comment = "Painel Principal"
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
            positions = mt5_service.get_open_positions()
            self.positions_panel.refresh_positions(positions)
        else:
            QMessageBox.critical(self, "Trade Failed", message)

    def close_selected_position(self):
        index = self.positions_panel.get_selected_ticket()
        if index is None:
            QMessageBox.warning(self, "No Selection", "Selecione uma posição para fechar.")
            return

        positions = mt5_service.get_open_positions()
        if index >= len(positions):
            QMessageBox.warning(self, "Erro", "Índice de posição inválido.")
            return

        ticket = positions[index].ticket
        success, message = mt5_service.close_position(ticket)
        if success:
            QMessageBox.information(self, "Fechada", message)
            self.positions_panel.refresh_positions(mt5_service.get_open_positions())
        else:
            QMessageBox.critical(self, "Erro", message)

    def auto_trade(self):
        df = mt5_service.get_symbol_data(self.current_symbol, n=150)
        if df is None or df.empty:
            QMessageBox.warning(self, "Auto Trade", "❌ Sem dados para operar.")
            return

        try:
            decision = self.smartux_agent.auto_trade_decision(self.current_symbol, df)
            if decision is None:
                QMessageBox.information(self, "Auto Trade", "🔕 IA recomenda: Hold")
                return

            print(f"🤖 AutoTrade: {decision}")

            constants = mt5_service.get_constants()
            order_type = constants["ORDER_TYPE_BUY"] if decision["direction"] == "buy" else constants["ORDER_TYPE_SELL"]

            success, msg = trade_controller.place_order(
                symbol=self.current_symbol,
                action_type=order_type,
                usd_volume=1.0,  # pode ajustar
                usd_sl=decision["sl_usd"],
                usd_tp=decision["tp_usd"],
                deviation=10,
                comment="AutoTrade"
            )

            if success:
                QMessageBox.information(self, "Auto Trade", f"✅ Ordem executada\n{msg}")
            else:
                QMessageBox.critical(self, "Auto Trade", f"⚠️ Falha ao executar\n{msg}")

        except Exception as e:
            QMessageBox.critical(self, "Erro Auto Trade", f"Erro: {e}")


    def closeEvent(self, event):
        mt5_service.shutdown()
        event.accept()
