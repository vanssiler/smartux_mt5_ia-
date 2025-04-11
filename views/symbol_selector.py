from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from config import SYMBOLS


class SymbolSelector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Select Symbol:")
        self.combo_box = QComboBox()
        self.combo_box.addItems(SYMBOLS)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)

    def get_selected_symbol(self):
        return self.combo_box.currentText()

    def on_change(self, callback):
        self.combo_box.currentTextChanged.connect(callback)
