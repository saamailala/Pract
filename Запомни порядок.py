import sys
import random
import os
import json
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from PySide6.QtMultimedia import QSoundEffect


class BaseDialog(QDialog):

    def __init__(self, title, width, height, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

        frame = QFrame()
        frame.setStyleSheet("background-color: #FDF5F5; border: 2px solid #E8B4BC; border-radius: 30px;")

        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(35, 30, 35, 30)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Georgia", 22, QFont.Light))
        title_label.setStyleSheet("color: #6B4F5A; border: none;")
        layout.addWidget(title_label)

        self.content_layout = layout

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(frame)
        self.setLayout(main_layout)

    def add_button(self, text, callback):
        btn = QPushButton(text)
        btn.setFont(QFont("Georgia", 14))
        btn.setFixedSize(180, 40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #E8B4BC;
                color: white;
                border: none;
                border-radius: 20px;
            }
            QPushButton:hover { background-color: #D9A9B4; }
        """)
        btn.clicked.connect(callback)
        return btn


class RulesDialog(BaseDialog):

    def __init__(self, parent=None):
        super().__init__("Правила игры", 500, 320, parent)

        rules = QLabel(
            "Запомните последовательность подсветки кнопок\nи повторите её в правильном порядке.\n\nВаши результаты сохраняются в таблице рекордов.")
        rules.setFont(QFont("Georgia", 12))
        rules.setStyleSheet("color: #8B6B76; border: none;")
        rules.setWordWrap(True)
        rules.setAlignment(Qt.AlignLeft)
        self.content_layout.addWidget(rules)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.add_button("Понятно", self.accept))
        btn_layout.addStretch()
        self.content_layout.addLayout(btn_layout)


class ExitConfirmDialog(BaseDialog):

    def __init__(self, level, parent=None):
        super().__init__("Выход в главное меню", 500, 320, parent)

        self.content_layout.addWidget(self._create_label(f"Вы дошли до {level} уровня", 16))
        self.content_layout.addWidget(self._create_label("Вы уверены, что хотите выйти?", 14))
        self.content_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(self.add_button("Выйти", self.accept))
        btn_layout.addWidget(self.add_button("Нет", self.reject))
        self.content_layout.addLayout(btn_layout)

    def _create_label(self, text, size):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Georgia", size))
        label.setStyleSheet("color: #8B6B76; border: none; margin-top: 10px;")
        return label


class DifficultyDialog(BaseDialog):

    def __init__(self, current, parent=None):
        super().__init__("Выберите сложность", 500, 380, parent)

        self.difficulties = {
            1: {"name": "Легкий", "speed": 800, "buttons": 4, "info": "800 мс • 4 кнопки"},
            2: {"name": "Средний", "speed": 600, "buttons": 6, "info": "600 мс • 6 кнопок"},
            3: {"name": "Сложный", "speed": 400, "buttons": 8, "info": "400 мс • 8 кнопок"},
            4: {"name": "Эксперт", "speed": 250, "buttons": 10, "info": "250 мс • 10 кнопок"}
        }

        self.group = QButtonGroup(self)
        self.radios = {}

        for i, diff in self.difficulties.items():
            radio = QRadioButton(diff["name"])
            radio.setFont(QFont("Georgia", 15))
            radio.setStyleSheet("""
                QRadioButton { color: #6B4F5A; spacing: 10px; }
                QRadioButton::indicator { width: 18px; height: 18px; border-radius: 9px; border: 2px solid #E8B4BC; background-color: #FDF5F5; }
                QRadioButton::indicator:checked { background-color: #E8B4BC; }
            """)
            radio.setChecked(current == diff["name"])
            self.group.addButton(radio, i)
            self.radios[i] = radio

            row = QHBoxLayout()
            row.addWidget(radio)
            row.addStretch()
            row.addWidget(self._create_info_label(diff["info"]))
            self.content_layout.addLayout(row)

        self.content_layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(Qt.AlignCenter)
        btn_layout.addWidget(self.add_button("Выбрать", self.accept))
        btn_layout.addWidget(self.add_button("Отмена", self.reject))
        self.content_layout.addLayout(btn_layout)

    def _create_info_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Georgia", 14))
        label.setStyleSheet("color: #8B6B76; border: none;")
        return label

    def get_difficulty(self):
        return self.difficulties[self.group.checkedId()]


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
        self.records = self._load_records()

        self.difficulty = {"name": "Легкий", "speed": 800, "buttons": 4}

        self.sounds = {}
        self._init_sounds()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self._create_welcome_screen()
        self._create_game_ui()
        self._create_game_over_ui()

        self.show_welcome_screen()
        QTimer.singleShot(500, lambda: RulesDialog(self).exec())

    def _init_sounds(self):
        sound_files = ["click.wav", "levelup.wav", "gameover.wav"]
        for name in sound_files:
            sound = QSoundEffect()
            sound.setVolume(0.4)
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
            if os.path.exists(path):
                sound.setSource(QUrl.fromLocalFile(path))
            self.sounds[name.replace(".wav", "")] = sound

    def _load_records(self):
        try:
            if os.path.exists("records.json"):
                with open("records.json", "r", encoding="utf-8") as f:
                    records = json.load(f)
                    for r in records:
                        r.setdefault("name", "Аноним")
                    records.sort(key=lambda x: x.get("date", ""), reverse=True)
                    return records
        except:
            pass
        return []

    def _save_record(self):
        record = {
            "name": self.player_name,
            "level": self.level - 1,
            "difficulty": self.difficulty["name"],
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        self.records.append(record)
        self.records.sort(key=lambda x: x.get("date", ""), reverse=True)
        self.records = self.records[:15]

        try:
            with open("records.json", "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _create_button_style(self, color, btn_size, font_size, disabled=False):
        if disabled:
            return f"""
                QPushButton {{
                    background-color: #F5EAEC;
                    color: #C5B0B5;
                    border: 1px solid #D9C0C8;
                    border-radius: {btn_size // 2}px;
                    font-size: {font_size}px;
                    font-family: Georgia;
                }}
            """
        return f"""
            QPushButton {{
                background-color: {color};
                color: #6B4F5A;
                border: 1px solid #D9C0C8;
                border-radius: {btn_size // 2}px;
                font-size: {font_size}px;
                font-family: Georgia;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #E3CBD0; }}
            QPushButton:pressed {{ background-color: #D9BCC2; color: white; }}
        """

    def _create_welcome_screen(self):
        self.welcome = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        for text in ["✧ ✦ ✧", "Запомни порядок", "❀ ❁ ❀"]:
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(
                QFont("Georgia" if text == "Запомни порядок" else "Segoe UI", 56 if text == "Запомни порядок" else 18))
            label.setStyleSheet(
                f"color: #6B4F5A; border: none;" if text == "Запомни порядок" else "color: #E0C8D0; border: none;")
            layout.addWidget(label)

        name_frame = QFrame()
        name_frame.setStyleSheet(
            "background-color: rgba(232, 180, 188, 0.1); border: 2px solid #E8B4BC; border-radius: 25px;")
        name_layout = QVBoxLayout(name_frame)
        name_layout.addWidget(self._create_label("Введите ваше имя:", 12, "#6B4F5A"))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Аноним")
        self.name_input.setMaxLength(20)
        self.name_input.setFixedSize(300, 40)
        self.name_input.setAlignment(Qt.AlignCenter)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #6B4F5A;
                border: 2px solid #E8B4BC;
                border-radius: 20px;
                padding: 5px 15px;
                font-family: Georgia;
                font-size: 14px;
            }
            QLineEdit:focus { border: 2px solid #D9A9B4; }
        """)
        name_layout.addWidget(self.name_input, alignment=Qt.AlignCenter)
        layout.addWidget(name_frame)

        self.diff_label = self._create_label(f"Сложность: {self.difficulty['name']}", 14, "#8B6B76")
        layout.addWidget(self.diff_label)

        diff_btn = self._create_button("Изменить сложность", 220, 50, 14, self.open_difficulty_dialog)
        layout.addWidget(diff_btn, alignment=Qt.AlignCenter)

        start_btn = self._create_button("Начать игру", 220, 60, 16, self.start_from_welcome)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)
        info_layout.setAlignment(Qt.AlignCenter)
        for text, callback in [("Правила", lambda: RulesDialog(self).exec()), ("Рекорды", self.show_records),
                               ("Выход", self.close)]:
            btn = self._create_button(text, 150, 50, 14, callback)
            info_layout.addWidget(btn)
        layout.addLayout(info_layout)

        layout.addWidget(self._create_label("• ✦ • ✦ •", 14, "#E0C8D0"))
        self.welcome.setLayout(layout)

    def _create_game_ui(self):
        self.game = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(20, 20, 20, 20)

        top = QWidget()
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(QWidget())
        self.title_label = self._create_label("Запомни порядок", 32, "#6B4F5A")
        top_layout.addWidget(self.title_label, 1)

        exit_btn = self._create_button("✕  Главное меню", 140, 36, 11, self.show_exit_confirmation)
        top_layout.addWidget(exit_btn)
        layout.addWidget(top)

        info = QWidget()
        info_layout = QHBoxLayout(info)
        info_layout.setAlignment(Qt.AlignCenter)
        info_layout.setSpacing(30)
        self.player_label = self._create_label(f"Игрок: {self.player_name}", 12, "#8B6B76")
        self.level_label = self._create_label(f"Уровень {self.level}", 16, "#8B6B76")
        self.diff_game_label = self._create_label(self.difficulty["name"], 14, "#D9A9B4")
        info_layout.addWidget(self.player_label)
        info_layout.addWidget(self.level_label)
        info_layout.addWidget(self.diff_game_label)
        layout.addWidget(info, alignment=Qt.AlignCenter)

        self.buttons_grid = QGridLayout()
        self.buttons_grid.setSpacing(20)
        self.buttons_grid.setAlignment(Qt.AlignCenter)
        layout.addLayout(self.buttons_grid, 1)

        self.game.setLayout(layout)

    def _create_game_over_ui(self):
        self.game_over = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._create_label("✧", 24, "#E0C8D0"))
        layout.addWidget(self._create_label("Игра окончена", 48, "#6B4F5A", True))
        self.result_label = self._create_label("", 18, "#8B6B76")
        layout.addWidget(self.result_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(Qt.AlignCenter)
        for text, callback in [("Играть снова", self.play_again), ("Главное меню", self.go_to_main_menu),
                               ("Выход", self.close)]:
            btn = self._create_button(text, 150, 50, 14, callback)
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)

        self.game_over.setLayout(layout)

    def _create_label(self, text, size, color, italic=False):
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Georgia", size, italic=italic))
        label.setStyleSheet(f"color: {color}; border: none;")
        return label

    def _create_button(self, text, width, height, font_size, callback):
        btn = QPushButton(text)
        btn.setFont(QFont("Georgia", font_size))
        btn.setFixedSize(width, height)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #E8B4BC;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover { background-color: #D9A9B4; }
        """)
        btn.clicked.connect(callback)
        return btn

    def show_welcome_screen(self):
        self._clear_layout()
        self.main_layout.addWidget(self.welcome)
        self.welcome.show()

    def show_game_ui(self):
        self._clear_layout()
        self.main_layout.addWidget(self.game)
        self.game.show()

    def show_game_over_ui(self):
        self._clear_layout()
        self.main_layout.addWidget(self.game_over)
        self.game_over.show()

    def _clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryOrderGame()
    window.show()
    sys.exit(app.exec())