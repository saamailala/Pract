import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

class MemoryOrderGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Запомни порядок")
        self.setWindowState(Qt.WindowMaximized)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryOrderGame()
    window.show()
    sys.exit(app.exec())