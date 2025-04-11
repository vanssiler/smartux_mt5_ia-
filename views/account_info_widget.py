from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class AccountInfoWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.balance_label = QLabel("💰 Saldo: --")
        self.equity_label = QLabel("📊 Patrimônio: --")
        self.margin_label = QLabel("📉 Margem: --")

        self.layout.addWidget(self.balance_label)
        self.layout.addWidget(self.equity_label)
        self.layout.addWidget(self.margin_label)

    def update_account_info(self, account_info):
        if not account_info:
            return

        self.balance_label.setText(f"💰 Saldo: {account_info.balance:.2f}")
        self.equity_label.setText(f"📊 Patrimônio: {account_info.equity:.2f}")
        self.margin_label.setText(f"📉 Margem: {account_info.margin:.2f}")
