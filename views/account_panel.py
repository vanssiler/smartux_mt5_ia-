from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class AccountPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.account_label = QLabel("Account: ---")
        self.balance_label = QLabel("Balance: ---")
        self.equity_label = QLabel("Equity: ---")

        self.layout.addWidget(self.account_label)
        self.layout.addWidget(self.balance_label)
        self.layout.addWidget(self.equity_label)

    def update_account_info(self, account_info):
        if account_info:
            self.account_label.setText(f"Account: {account_info.login}")
            self.balance_label.setText(f"Balance: ${account_info.balance:.2f}")
            self.equity_label.setText(f"Equity: ${account_info.equity:.2f}")
        else:
            self.account_label.setText("Account: ---")
            self.balance_label.setText("Balance: ---")
            self.equity_label.setText("Equity: ---")
