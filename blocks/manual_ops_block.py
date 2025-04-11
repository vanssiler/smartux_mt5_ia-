from PyQt5.QtWidgets import QVBoxLayout, QLabel, QGroupBox
from views.trade_panel import TradePanel
from views.account_panel import AccountPanel
from views.positions_panel import PositionsPanel
from controllers.ml_controller import MLController
from agents.agent_controller import SmartuxAgent


def create_manual_ops_block(context):
    context.trade_panel = TradePanel()
    context.account_panel = AccountPanel()
    context.positions_panel = PositionsPanel()

    # Garantir símbolo atual definido
    if not hasattr(context, "current_symbol"):
        context.current_symbol = context.symbol_selector.get_selected_symbol()

    # Inicializar IA (caso ainda não tenha)
    if not hasattr(context, "ml_controller"):
        context.ml_controller = MLController()
        try:
            context.ml_controller.load_model()
        except Exception as e:
            print(f"⚠️ Nenhum modelo encontrado, IA inativa até treinamento.\n{e}")

    if not hasattr(context, "smartux_agent"):
        context.smartux_agent = SmartuxAgent(context.ml_controller)

    # Conectar botões
    context.positions_panel.close_button.clicked.connect(context.close_selected_position)
    context.trade_panel.buy_button.clicked.connect(lambda: context.place_order("buy", manual=True))
    context.trade_panel.sell_button.clicked.connect(lambda: context.place_order("sell", manual=True))

    # Atualizar posições ao iniciar
    context.positions_panel.refresh_positions()

    layout = QVBoxLayout()
    layout.addWidget(QLabel("🛠️ Operações Manuais"))
    layout.addWidget(context.trade_panel)
    layout.addWidget(context.account_panel)
    layout.addWidget(context.positions_panel)

    box = QGroupBox("Painel de Operações")
    box.setLayout(layout)

    return box
