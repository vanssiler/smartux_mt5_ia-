# styles/theme.py

DARK_THEME = """
QWidget {
    background-color: #1e1e1e;
    color: white;
    font-size: 14px;
}
QGroupBox {
    border: 1px solid #444;
    border-radius: 5px;
    margin-top: 10px;
}
QGroupBox:title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
    color: #66ccff;
}
QPushButton {
    background-color: #333;
    color: white;
    padding: 10px;
    border-radius: 6px;
}
QPushButton:hover {
    background-color: #444;
}
QLabel {
    color: white;
}
QLineEdit {
    background-color: #2a2a2a;
    color: white;
    border: 1px solid #555;
    border-radius: 4px;
    padding: 4px;
}
QComboBox {
    background-color: #2a2a2a;
    color: white;
    border-radius: 4px;
}
"""
