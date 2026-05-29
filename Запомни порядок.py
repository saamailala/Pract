import sys
import random
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont


class RulesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Правила игры")
        self.setFixedSize(500, 320)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

        frame = QFrame()
        frame.setStyleSheet("background-color: #FDF5F5; border: 2px solid #E8B4BC; border-radius: 30px;")

        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(35, 30, 35, 30)

        title = QLabel("Правила игры")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Georgia", 22, QFont.Light))
        title.setStyleSheet("color: #6B4F5A; border: none;")
        layout.addWidget(title)

        rules_text = QLabel(
            "Запомните последовательность подсветки кнопок\n"
            "и повторите её в правильном порядке.\n\n"
            "Ваши результаты сохраняются в таблице рекордов."
        )
        rules_text.setFont(QFont("Georgia", 12))
        rules_text.setStyleSheet("color: #8B6B76; border: none;")
        rules_text.setWordWrap(True)
        layout.addWidget(rules_text)

        ok_btn = QPushButton("Понятно")
        ok_btn.setFont(QFont("Georgia", 14))
        ok_btn.setFixedSize(180, 40)
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #E8B4BC;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #D9A9B4; }
        """)
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn, alignment=Qt.AlignCenter)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(frame)
        self.setLayout(main_layout)


class MemoryOrderGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Запомни порядок")
        self.setWindowState(Qt.WindowMaximized)

        self.sequence = []
        self.player_sequence = []
        self.level = 1
        self.buttons = []
        self.is_showing = False
        self.clickable = False
        self.player_name = "Аноним"

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

        self.game = QWidget()
        game_layout = QVBoxLayout()
        game_layout.setSpacing(30)

        self.title_label = QLabel("Запомни порядок")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Georgia", 32))
        self.title_label.setStyleSheet("color: #6B4F5A;")
        game_layout.addWidget(self.title_label)

        self.game.setLayout(game_layout)
        self.game.hide()

    def show_rules(self):
        dialog = RulesDialog(self)
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryOrderGame()
    window.show()
    sys.exit(app.exec())