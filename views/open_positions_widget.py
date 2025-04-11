from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QHBoxLayout
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt

class OpenPositionsWidget(QWidget):
    def __init__(self, on_close_position):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title = QLabel("📋 Posições Abertas")
        self.positions_list = QListWidget()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.positions_list)

        self.positions_data = []
        self.on_close_position = on_close_position  # Callback para fechar

    def refresh_positions(self, positions):
        self.positions_list.clear()
        self.positions_data = positions

        for idx, p in enumerate(positions):
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(5, 2, 5, 2)

            tipo = "Buy" if p.type == 0 else "Sell"
            label = QLabel(f"{p.symbol} | {tipo} | {p.volume:.2f} | {p.price_open:.5f} | Lucro: {p.profit:.2f}")

            # Botão ❌ com estilo
            close_button = QPushButton("❌")
            close_button.setFixedSize(24, 24)
            close_button.setStyleSheet("""
                QPushButton {
                    font-weight: bold;
                    color: red;
                    background: transparent;
                    border: none;
                }
                QPushButton:hover {
                    color: darkred;
                }
            """)
            close_button.clicked.connect(lambda _, i=idx: self._close_position(i))

            # Cor de fundo com base no lucro/prejuízo
            if p.profit > 0:
                item_widget.setStyleSheet("background-color: #d0f5d0; color:#000; border-radius: 4px; padding: 2px;")
            elif p.profit < 0:
                item_widget.setStyleSheet("background-color: #f5d0d0; color:#000; border-radius: 4px; padding: 2px;")
            else:
                item_widget.setStyleSheet("background-color: #eeeeee; color:#000; border-radius: 4px; padding: 2px;")

            item_layout.addWidget(label)
            item_layout.addStretch()
            item_layout.addWidget(close_button)

            list_item = QListWidgetItem()
            list_item.setSizeHint(item_widget.sizeHint())
            self.positions_list.addItem(list_item)
            self.positions_list.setItemWidget(list_item, item_widget)

    def get_selected_ticket(self):
        index = self.positions_list.currentRow()
        if index < 0 or index >= len(self.positions_data):
            return None
        return self.positions_data[index].ticket

    def _close_position(self, index):
        if 0 <= index < len(self.positions_data):
            ticket = self.positions_data[index].ticket
            self.on_close_position(ticket)
