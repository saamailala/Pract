import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class MemoryOrderGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Запомни порядок")
        self.setWindowState(Qt.WindowMaximized)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.welcome = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Запомни порядок")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Georgia", 56))
        layout.addWidget(title)

        self.start_btn = QPushButton("Начать игру")
        self.start_btn.setFont(QFont("Georgia", 16))
        self.start_btn.setFixedSize(220, 60)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #E8B4BC;
                color: white;
                border: none;
                border-radius: 30px;
            }
            QPushButton:hover { background-color: #D9A9B4; }
        """)
        layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)

        self.rules_btn = QPushButton("Правила")
        self.rules_btn.setFont(QFont("Georgia", 14))
        self.rules_btn.setFixedSize(150, 50)
        self.rules_btn.setCursor(Qt.PointingHandCursor)
        self.rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #E8B4BC;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover { background-color: #D9A9B4; }
        """)
        self.rules_btn.clicked.connect(self.show_rules)
        layout.addWidget(self.rules_btn, alignment=Qt.AlignCenter)

        self.exit_btn = QPushButton("Выход")
        self.exit_btn.setFont(QFont("Georgia", 14))
        self.exit_btn.setFixedSize(150, 50)
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #E8B4BC;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover { background-color: #D9A9B4; }
        """)
        self.exit_btn.clicked.connect(self.close)
        layout.addWidget(self.exit_btn, alignment=Qt.AlignCenter)

        self.welcome.setLayout(layout)
        self.main_layout.addWidget(self.welcome)

    def show_rules(self):
        print("Правила игры")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryOrderGame()
    window.show()
    sys.exit(app.exec())