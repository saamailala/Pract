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
    """Основа для всех всплывающих окон, чтобы не копипастить"""

    def __init__(self, title, width, height, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)  # убираем заголовок винды, рисуем свой
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)  # чтобы скругления нормально смотрелись

        # Делаем красивую рамку с закруглениями
        frame = QFrame()
        frame.setStyleSheet("background-color: #FDF5F5; border: 2px solid #E8B4BC; border-radius: 30px;")

        layout = QVBoxLayout(frame)
        layout.setSpacing(15)
        layout.setContentsMargins(35, 30, 35, 30)

        # Заголовок окна
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Georgia", 22, QFont.Light))
        title_label.setStyleSheet("color: #6B4F5A; border: none;")
        layout.addWidget(title_label)

        self.content_layout = layout  # сюда докидываем всё остальное

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(frame)
        self.setLayout(main_layout)

    def add_button(self, text, callback):
        """Создаёт розовую кнопку, всё как мы любим"""
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
    """Окно с правилами игры, показывается при запуске"""

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
    """Спрашиваем игрока — точно хочешь выйти?"""

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
    """Выбор сложности — лёгкий, средний, сложный, эксперт"""

    def __init__(self, current, parent=None):
        super().__init__("Выберите сложность", 500, 380, parent)

        # Наши режимы сложности
        self.difficulties = {
            1: {"name": "Легкий", "speed": 800, "buttons": 4, "info": "800 мс • 4 кнопки"},
            2: {"name": "Средний", "speed": 600, "buttons": 6, "info": "600 мс • 6 кнопок"},
            3: {"name": "Сложный", "speed": 400, "buttons": 8, "info": "400 мс • 8 кнопок"},
            4: {"name": "Эксперт", "speed": 250, "buttons": 10, "info": "250 мс • 10 кнопок"}
        }

        self.group = QButtonGroup(self)
        self.radios = {}

        # Создаём радиокнопки для выбора
        for i, diff in self.difficulties.items():
            radio = QRadioButton(diff["name"])
            radio.setFont(QFont("Georgia", 15))
            radio.setStyleSheet("""
                QRadioButton { color: #6B4F5A; spacing: 10px; }
                QRadioButton::indicator { width: 18px; height: 18px; border-radius: 9px; border: 2px solid #E8B4BC; background-color: #FDF5F5; }
                QRadioButton::indicator:checked { background-color: #E8B4BC; }
            """)
            radio.setChecked(current == diff["name"])  # отмечаем текущую сложность
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
        """Возвращает выбранную сложность"""
        return self.difficulties[self.group.checkedId()]


class MemoryOrderGame(QMainWindow):
    """Главная игра — запомни порядок"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Запомни порядок")
        self.setWindowState(Qt.WindowMaximized)  # запускаем на весь экран

        # Состояние игры
        self.sequence = []         # что показала игра
        self.player_sequence = []  # что нажал игрок
        self.level = 1
        self.buttons = []
        self.is_showing = False    # идёт ли показ последовательности
        self.clickable = False     # можно ли нажимать кнопки
        self.player_name = "Аноним"
        self.records = self._load_records()

        # Текущая сложность
        self.difficulty = {"name": "Легкий", "speed": 800, "buttons": 4}

        # Звуки
        self.sounds = {}
        self._init_sounds()

        # Центральный виджет и главный лейаут
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаём экраны
        self._create_welcome_screen()
        self._create_game_ui()
        self._create_game_over_ui()

        # Показываем приветствие и через полсекунды — правила
        self.show_welcome_screen()
        QTimer.singleShot(500, lambda: RulesDialog(self).exec())

    def _init_sounds(self):
        """Загружаем звуки клика, повышения уровня и проигрыша"""
        sound_files = ["click.wav", "levelup.wav", "gameover.wav"]
        for name in sound_files:
            sound = QSoundEffect()
            sound.setVolume(0.4)
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name)
            if os.path.exists(path):
                sound.setSource(QUrl.fromLocalFile(path))
            self.sounds[name.replace(".wav", "")] = sound

    def _load_records(self):
        """Подгружаем таблицу рекордов из JSON, если есть"""
        try:
            if os.path.exists("records.json"):
                with open("records.json", "r", encoding="utf-8") as f:
                    records = json.load(f)
                    for r in records:
                        r.setdefault("name", "Аноним")
                    records.sort(key=lambda x: x.get("date", ""), reverse=True)  # новые сверху
                    return records
        except:
            pass
        return []

    def _save_record(self):
        """Сохраняем результат в JSON, храним не больше 15 записей"""
        record = {
            "name": self.player_name,
            "level": self.level - 1,
            "difficulty": self.difficulty["name"],
            "date": datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        self.records.append(record)
        self.records.sort(key=lambda x: x.get("date", ""), reverse=True)
        self.records = self.records[:15]  # обрезаем до 15

        try:
            with open("records.json", "w", encoding="utf-8") as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
        except:
            pass

    def _create_button_style(self, color, btn_size, font_size, disabled=False):
        """Стили для игровых кнопок — обычные и неактивные"""
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
        """Экран приветствия с именем, сложностью и кнопками"""
        self.welcome = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignCenter)

        # Декоративные надписи и название игры
        for text in ["✧ ✦ ✧", "Запомни порядок", "❀ ❁ ❀"]:
            label = QLabel(text)
            label.setAlignment(Qt.AlignCenter)
            label.setFont(
                QFont("Georgia" if text == "Запомни порядок" else "Segoe UI", 56 if text == "Запомни порядок" else 18))
            label.setStyleSheet(
                f"color: #6B4F5A; border: none;" if text == "Запомни порядок" else "color: #E0C8D0; border: none;")
            layout.addWidget(label)

        # Поле для ввода имени
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

        # Текущая сложность
        self.diff_label = self._create_label(f"Сложность: {self.difficulty['name']}", 14, "#8B6B76")
        layout.addWidget(self.diff_label)

        diff_btn = self._create_button("Изменить сложность", 220, 50, 14, self.open_difficulty_dialog)
        layout.addWidget(diff_btn, alignment=Qt.AlignCenter)

        start_btn = self._create_button("Начать игру", 220, 60, 16, self.start_from_welcome)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        # Кнопки: правила, рекорды, выход
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
        """Основной игровой экран"""
        self.game = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(20, 20, 20, 20)

        # Верхняя панель: заголовок и кнопка выхода
        top = QWidget()
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(QWidget())  # распорка слева
        self.title_label = self._create_label("Запомни порядок", 32, "#6B4F5A")
        top_layout.addWidget(self.title_label, 1)

        exit_btn = self._create_button("✕  Главное меню", 140, 36, 11, self.show_exit_confirmation)
        top_layout.addWidget(exit_btn)
        layout.addWidget(top)

        # Инфо: имя игрока, уровень, сложность
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

        # Сетка с игровыми кнопками
        self.buttons_grid = QGridLayout()
        self.buttons_grid.setSpacing(20)
        self.buttons_grid.setAlignment(Qt.AlignCenter)
        layout.addLayout(self.buttons_grid, 1)

        self.game.setLayout(layout)

    def _create_game_over_ui(self):
        """Экран окончания игры"""
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
        """Быстрое создание label с нужным шрифтом и цветом"""
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Georgia", size, italic=italic))
        label.setStyleSheet(f"color: {color}; border: none;")
        return label

    def _create_button(self, text, width, height, font_size, callback):
        """Быстрое создание кнопки в едином стиле"""
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

    def _get_button_size(self):
        """Размер кнопок зависит от их количества"""
        if self.difficulty["buttons"] <= 6: return 100, 28
        if self.difficulty["buttons"] <= 8: return 90, 24
        return 80, 22

    def _update_buttons_grid(self):
        """Пересоздаём игровое поле под новую сложность"""
        # Удаляем старые кнопки
        for btn in self.buttons:
            btn.deleteLater()
        self.buttons = []

        while self.buttons_grid.count():
            item = self.buttons_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Палитра цветов для кнопок
        self.button_colors = ["#F3E3E5", "#EFDADE", "#EBD1D6", "#E7C8CE", "#F2D0D9", "#EDC5D0", "#E8BAC7", "#E3AFC0",
                              "#DEA4B6", "#D999AC"]
        cols = self.difficulty["buttons"] // 2  # сколько кнопок в ряду
        btn_size, font_size = self._get_button_size()

        # Создаём кнопки
        for i in range(self.difficulty["buttons"]):
            btn = QPushButton(str(i + 1))
            btn.setFont(QFont("Georgia", font_size, QFont.Bold))
            btn.setFixedSize(btn_size, btn_size)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(
                self._create_button_style(self.button_colors[i % len(self.button_colors)], btn_size, font_size))
            btn.clicked.connect(lambda idx=i: self._on_button_click(idx))
            btn.setEnabled(False)  # пока нельзя нажимать
            self.buttons.append(btn)
            self.buttons_grid.addWidget(btn, i // cols, i % cols)

    def _on_button_click(self, index):
        """Игрок нажал на кнопку — запоминаем и подсвечиваем"""
        if not self.is_showing and self.clickable and self.buttons[index].isEnabled():
            self.clickable = False  # на время подсветки блокируем
            self.player_sequence.append(index)
            if self.sounds.get("click"):
                self.sounds["click"].play()

            # Подсветка при нажатии
            btn_size, font_size = self._get_button_size()
            self.buttons[index].setStyleSheet(self._create_button_style("#D9BCC2", btn_size, font_size))
            QTimer.singleShot(200, lambda: self._restore_button_color(index))
            QTimer.singleShot(200, self._check_sequence)  # проверяем через 200 мс

    def _restore_button_color(self, index):
        """Возвращаем кнопке её обычный цвет"""
        if index < len(self.buttons):
            btn_size, font_size = self._get_button_size()
            self.buttons[index].setStyleSheet(
                self._create_button_style(self.button_colors[index % len(self.button_colors)], btn_size, font_size))
            self.clickable = True  # снова можно нажимать

    def _check_sequence(self):
        """Проверяем, правильно ли игрок повторяет последовательность"""
        if not self.player_sequence:
            return
        if self.player_sequence[-1] != self.sequence[len(self.player_sequence) - 1]:
            self._game_over()  # ошибка — конец
        elif len(self.player_sequence) == len(self.sequence):
            self._level_complete()  # всё верно — следующий уровень

    def _level_complete(self):
        """Уровень пройден!"""
        self.level += 1
        self.level_label.setText(f"Уровень {self.level}")
        if self.sounds.get("levelup"):
            self.sounds["levelup"].play()
        QTimer.singleShot(200, self._start_level)

    def _game_over(self):
        """Игра окончена — сохраняем результат и показываем экран"""
        self.clickable = False
        for btn in self.buttons:
            btn.setEnabled(False)
        self._save_record()
        self.result_label.setText(f"{self.player_name}, вы дошли до {self.level} уровня")
        if self.sounds.get("gameover"):
            self.sounds["gameover"].play()
        self.show_game_over_ui()

    def _start_level(self):
        """Начинаем уровень: генерим последовательность и показываем"""
        for btn in self.buttons:
            btn.setEnabled(False)

        # Добавляем новую кнопку в последовательность
        if self.level == 1:
            self.sequence = [random.randint(0, self.difficulty["buttons"] - 1)]
        else:
            self.sequence.append(random.randint(0, self.difficulty["buttons"] - 1))

        self.player_sequence = []
        self.is_showing = True
        self.clickable = False
        self.title_label.setText("Запоминайте...")
        QTimer.singleShot(500, self._show_sequence)

    def _show_sequence(self):
        """Подсвечиваем кнопки по очереди с нужной скоростью"""
        speed = self.difficulty["speed"]
        for i, idx in enumerate(self.sequence):
            QTimer.singleShot(int(speed * i), lambda i=idx: self._highlight_button(i))
        QTimer.singleShot(int(speed * len(self.sequence) + 300), self._allow_input)

    def _highlight_button(self, index):
        """Подсветка одной кнопки во время показа"""
        if not self.is_showing:
            return
        btn_size, font_size = self._get_button_size()
        self.buttons[index].setStyleSheet(self._create_button_style("#D9BCC2", btn_size, font_size))
        QTimer.singleShot(300, lambda: self._restore_button_color(index))

    def _allow_input(self):
        """Разрешаем игроку нажимать кнопки"""
        self.is_showing = False
        self.clickable = True
        self.title_label.setText("Ваш ход")
        for btn in self.buttons:
            btn.setEnabled(True)

    def start_from_welcome(self):
        """Начинаем игру с экрана приветствия"""
        name = self.name_input.text().strip()
        self.player_name = name if name else "Аноним"
        self._update_buttons_grid()
        self.show_game_ui()
        self.player_label.setText(f"Игрок: {self.player_name}")
        self._start_game()

    def _start_game(self):
        """Сброс и старт игры"""
        self.level = 1
        self.sequence = []
        self.level_label.setText(f"Уровень {self.level}")
        self.diff_game_label.setText(self.difficulty["name"])
        self._start_level()

    def play_again(self):
        """Переиграть после проигрыша"""
        self.level = 1
        self.sequence = []
        self.player_sequence = []
        self.clickable = False
        self._update_buttons_grid()
        self.show_game_ui()
        self.player_label.setText(f"Игрок: {self.player_name}")
        self.diff_game_label.setText(self.difficulty["name"])
        self._start_game()

    def go_to_main_menu(self):
        """Вернуться на главный экран"""
        self.show_welcome_screen()

    def show_records(self):
        """Показать таблицу рекордов"""

        class RecordsDialog(BaseDialog):
            def __init__(self, records, parent=None):
                super().__init__("Таблица рекордов", 700, 500, parent)

                # Краткая статистика
                stats = QHBoxLayout()
                stats.addWidget(self._create_stat_label(f"Всего записей: {len(records)}", 12))
                if records:
                    best = max(records, key=lambda x: x.get("level", 0))
                    stats.addWidget(
                        self._create_stat_label(f"Лучший: {best.get('level', '?')} ур. ({best.get('name', 'Аноним')})",
                                                12, True))
                self.content_layout.addLayout(stats)

                self.records = records
                self.table = QTableWidget()
                self.table.setColumnCount(5)
                self.table.setHorizontalHeaderLabels(["#", "Имя", "Уровень", "Сложность", "Дата"])
                self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # только чтение
                self.table.setStyleSheet("""
                    QTableWidget { background-color: transparent; border: none; }
                    QTableWidget::item { 
                        color: #6B4F5A; 
                        font-family: Georgia; 
                        border: none; 
                        background: transparent;
                        padding: 5px;
                    }
                    QHeaderView::section { 
                        background-color: #E8B4BC; 
                        color: white; 
                        font-family: Georgia; 
                        padding: 8px; 
                        border: none; 
                    }
                """)
                self._update_table()
                self.content_layout.addWidget(self.table)

                btn = self.add_button("Закрыть", self.accept)
                btn_layout = QHBoxLayout()
                btn_layout.addStretch()
                btn_layout.addWidget(btn)
                btn_layout.addStretch()
                self.content_layout.addLayout(btn_layout)

            def _create_stat_label(self, text, size, bold=False):
                label = QLabel(text)
                label.setFont(QFont("Georgia", size, QFont.Bold if bold else QFont.Normal))
                label.setStyleSheet("color: #8B6B76; border: none;")
                return label

            def _update_table(self):
                """Заполняем таблицу данными"""
                self.table.setRowCount(len(self.records))
                for i, r in enumerate(self.records):
                    # Номер
                    num_item = QTableWidgetItem(str(i + 1))
                    num_item.setFont(QFont("Georgia", 11))
                    num_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, 0, num_item)

                    # Имя
                    name_item = QTableWidgetItem(r.get("name", "Аноним"))
                    name_item.setFont(QFont("Georgia", 11))
                    self.table.setItem(i, 1, name_item)

                    # Уровень
                    level_item = QTableWidgetItem(str(r.get("level", "?")))
                    level_item.setFont(QFont("Georgia", 11))
                    level_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, 2, level_item)

                    # Сложность
                    diff_item = QTableWidgetItem(r.get("difficulty", "?"))
                    diff_item.setFont(QFont("Georgia", 11))
                    self.table.setItem(i, 3, diff_item)

                    # Дата
                    date_item = QTableWidgetItem(r.get("date", "?"))
                    date_item.setFont(QFont("Georgia", 11))
                    self.table.setItem(i, 4, date_item)

        RecordsDialog(self.records, self).exec()

    def open_difficulty_dialog(self):
        """Открыть окно выбора сложности"""
        dialog = DifficultyDialog(self.difficulty["name"], self)
        if dialog.exec() == QDialog.Accepted:
            self.difficulty = dialog.get_difficulty()
            self.diff_label.setText(f"Сложность: {self.difficulty['name']}")
            self.diff_game_label.setText(self.difficulty["name"])

    def show_exit_confirmation(self):
        """Диалог подтверждения выхода в меню"""
        if ExitConfirmDialog(self.level, self).exec() == QDialog.Accepted:
            self._save_record()
            self.show_welcome_screen()

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
        """Прячем всё, что есть на экране"""
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryOrderGame()
    window.show()
    sys.exit(app.exec())