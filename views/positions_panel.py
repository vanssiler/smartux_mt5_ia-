from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QListWidgetItem, QHBoxLayout
)
from services import mt5_service


class PositionsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel("Open Positions")
        self.position_list = QListWidget()
        self.refresh_button = QPushButton("Refresh")
        self.close_button = QPushButton("Close Selected")

        self.layout.addWidget(self.title)
        self.layout.addWidget(self.position_list)

        button_row = QHBoxLayout()
        button_row.addWidget(self.refresh_button)
        button_row.addWidget(self.close_button)
        self.layout.addLayout(button_row)

        self.refresh_button.clicked.connect(self.refresh_positions)

    def refresh_positions(self):
        self.position_list.clear()
        positions = mt5_service.get_open_positions()

        if not positions:
            self.position_list.addItem("No open positions")
            return

        for pos in positions:
            direction = "Buy" if pos.type == 0 else "Sell"
            text = f"{pos.symbol} | {direction} | {pos.volume:.2f} lots | P/L: ${pos.profit:.2f}"
            item = QListWidgetItem(text)
            item.setData(32, pos.ticket)  # Custom role for ticket ID
            self.position_list.addItem(item)

    def get_selected_ticket(self):
        selected_item = self.position_list.currentItem()
        if selected_item:
            return selected_item.data(32)
        return None
