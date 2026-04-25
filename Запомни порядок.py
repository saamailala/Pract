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

        self.welcome.setLayout(layout)
        self.main_layout.addWidget(self.welcome)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryOrderGame()
    window.show()
    sys.exit(app.exec())