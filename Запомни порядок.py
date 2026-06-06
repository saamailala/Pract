import sys
import random
import os
import json
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout,
                               QHBoxLayout, QWidget, QLabel, QDialog,
                               QButtonGroup, QRadioButton, QGridLayout, QFrame,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QLineEdit, QComboBox)
from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtGui import QFont, QPixmap, QPainter, QBrush, QPen, QColor, QPalette
from PySide6.QtMultimedia import QSoundEffect


class BaseDialog(QDialog):
    STYLE = "QFrame{background:#FDF5F5;border:2px solid #E8B4BC;border-radius:30px}"
    TITLE = "color:#6B4F5A;border:none"
    SUBTITLE = "color:#8B6B76;border:none"
    BTN = "QPushButton{background:#E8B4BC;color:white;border:none;border-radius:20px}QPushButton:hover{background:#D9A9B4}"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setModal(True)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.mw = QFrame(styleSheet=self.STYLE)
        self.setup_ui()
        l = QVBoxLayout(self)
        l.addWidget(self.mw)
        self.setLayout(l)

    def setup_ui(self):
        pass

    def _lbl(self, t, s=24):
        return QLabel(t, alignment=Qt.AlignCenter, font=QFont("Georgia", s, QFont.Light), styleSheet=self.TITLE)

    def _btn(self, t, cb, s=14, w=180):
        b = QPushButton(t, font=QFont("Georgia", s), cursor=Qt.PointingHandCursor, styleSheet=self.BTN)
        b.setFixedHeight(40)
        b.setFixedWidth(w)
        b.clicked.connect(cb)
        return b

    def _btns(self, *btns):
        l = QHBoxLayout()
        l.addStretch()
        for b in btns:
            l.addWidget(b)
        l.addStretch()
        return l


class RulesDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Правила игры")
        self.setFixedSize(500, 320)

    def setup_ui(self):
        l = QVBoxLayout(self.mw)
        l.setSpacing(10)
        l.setContentsMargins(35, 20, 35, 20)
        l.addWidget(self._lbl("Правила игры"))
        r = QLabel(
            "Запомните последовательность подсветки кнопок\nи повторите её в правильном порядке.\n\nВаши результаты сохраняются в таблице рекордов.",
            font=QFont("Georgia", 12), styleSheet="color:#8B6B76;line-height:1.6;border:none",
            wordWrap=True, alignment=Qt.AlignLeft)
        l.addWidget(r)
        l.addLayout(self._btns(self._btn("Понятно", self.accept)))


class ExitConfirmDialog(BaseDialog):
    def __init__(self, level, parent=None):
        self.level = level
        super().__init__(parent)
        self.setWindowTitle("Выход в главное меню")
        self.setFixedSize(500, 320)

    def setup_ui(self):
        l = QVBoxLayout(self.mw)
        l.setSpacing(15)
        l.setContentsMargins(35, 30, 35, 30)
        l.addWidget(self._lbl("Выход в главное меню", 22))
        l.addWidget(QLabel(f"Вы дошли до {self.level} уровня", alignment=Qt.AlignCenter,
                           font=QFont("Georgia", 16), styleSheet=self.SUBTITLE + ";margin-top:10px"))
        l.addWidget(QLabel("Вы уверены, что хотите выйти?", alignment=Qt.AlignCenter,
                           font=QFont("Georgia", 14), styleSheet=self.SUBTITLE + ";margin-top:20px"))
        l.addStretch()
        bl = QHBoxLayout()
        bl.setSpacing(20)
        bl.setAlignment(Qt.AlignCenter)
        bl.addWidget(self._btn("Выйти", self.accept, 13, 120))
        bl.addWidget(self._btn("Нет", self.reject, 13, 120))
        l.addLayout(bl)


class RecordsDialog(BaseDialog):
    COMBO = """QComboBox{background:white;color:#6B4F5A;border:2px solid #E8B4BC;border-radius:15px;padding:5px 10px;outline:none}
        QComboBox:hover{border:2px solid #D9A9B4}QComboBox::drop-down{border:none;width:20px;background:transparent}
        QComboBox::down-arrow{image:none;border:none;width:0;height:0}
        QComboBox QAbstractItemView{border:2px solid #E8B4BC;border-radius:10px;background:white;
        selection-background-color:#FFE4E1;selection-color:#6B4F5A;outline:none;color:#6B4F5A}"""
    TABLE = """QTableWidget{background:transparent;border:none;outline:none}
        QTableWidget::item{padding:5px;color:#6B4F5A;font-family:Georgia;border:none;background:transparent}
        QTableWidget::item:selected{background:#FFE4E1;color:#6B4F5A;outline:none}
        QTableWidget::item:hover{background:#FFE4E1}
        QHeaderView::section{background:#E8B4BC;color:white;font-family:Georgia;font-weight:bold;padding:8px;border:none;font-size:13px}"""

    def __init__(self, data, parent=None):
        self.data = data
        self.sort = "level_desc"
        super().__init__(parent)
        self.setWindowTitle("Рекорды")
        self.setFixedSize(700, 500)

    def _combo(self, items, w):
        c = QComboBox(font=QFont("Georgia", 11), styleSheet=self.COMBO + f"min-width:{w}px")
        c.addItems(items)
        for role in [QPalette.Text, QPalette.ButtonText]:
            c.palette().setColor(role, QColor("#6B4F5A"))
        return c

    def setup_ui(self):
        l = QVBoxLayout(self.mw)
        l.setSpacing(15)
        l.setContentsMargins(35, 35, 35, 35)
        l.addWidget(self._lbl("Таблица рекордов"))
        sl = QHBoxLayout()
        sl.addWidget(QLabel(f"Всего записей: {len(self.data)}", font=QFont("Georgia", 12), styleSheet=self.SUBTITLE))
        sl.addStretch()
        if self.data:
            b = max(self.data, key=lambda x: x.get("level", 0))
            sl.addWidget(QLabel(f"Лучший: {b.get('level', '?')} ур. ({b.get('name', 'Аноним')})",
                                font=QFont("Georgia", 12, QFont.Bold), styleSheet="color:#E8B4BC;border:none"))
        l.addLayout(sl)
        fl = QHBoxLayout()
        fl.setSpacing(20)
        fl.addWidget(QLabel("Сортировать по:", font=QFont("Georgia", 12), styleSheet="color:#6B4F5A;border:none"))
        self.sc = self._combo(["Лучшие результаты", "Последние попытки", "Худшие результаты", "По имени"], 180)
        self.sc.currentIndexChanged.connect(self._change_sort)
        fl.addWidget(self.sc)
        fl.addStretch()
        fl.addWidget(QLabel("Фильтр:", font=QFont("Georgia", 12), styleSheet="color:#6B4F5A;border:none"))
        self.fc = self._combo(["Все сложности", "Легкий", "Средний", "Сложный", "Эксперт"], 120)
        self.fc.currentIndexChanged.connect(self._upd)
        fl.addWidget(self.fc)
        l.addLayout(fl)
        self.tbl = QTableWidget(columnCount=5, editTriggers=QTableWidget.NoEditTriggers,
                                selectionBehavior=QTableWidget.SelectRows, showGrid=False,
                                alternatingRowColors=False, styleSheet=self.TABLE)
        self.tbl.setHorizontalHeaderLabels(["#", "Имя", "Уровень", "Сложность", "Дата"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.verticalHeader().setDefaultSectionSize(30)
        self.tbl.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._upd()
        l.addWidget(self.tbl)
        l.addLayout(self._btns(self._btn("Закрыть", self.accept)))

    def _change_sort(self):
        self.sort = ["level_desc", "date_desc", "level_asc", "name_asc"][self.sc.currentIndex()]
        self._upd()

    def _upd(self):
        fv = self.fc.currentText()
        fd = self.data if fv == "Все сложности" else [r for r in self.data if r.get("difficulty") == fv]
        k = {"level_desc": (lambda x: x.get("level", 0), True),
             "level_asc": (lambda x: x.get("level", 0), False),
             "date_desc": (lambda x: x.get("date", ""), True),
             "name_asc": (lambda x: x.get("name", ""), False)}
        key, rev = k.get(self.sort, k["level_desc"])
        sd = sorted(fd, key=key, reverse=rev)
        self.tbl.setRowCount(len(sd))
        for i, r in enumerate(sd):
            for j, f in enumerate([str(i + 1), r.get("name", "Аноним"), str(r.get("level", "?")),
                                   r.get("difficulty", "?"), r.get("date", "?")]):
                it = QTableWidgetItem(f)
                it.setFont(QFont("Georgia", 11))
                it.setForeground(
                    QColor("#E8B4BC") if (j == 2 and i == 0 and self.sort == "level_desc") else QColor("#6B4F5A"))
                self.tbl.setItem(i, j, it)


class DifficultyDialog(BaseDialog):
    RADIO = """QRadioButton{color:#6B4F5A;spacing:10px;border:none;background:transparent}
        QRadioButton::indicator{width:18px;height:18px;border-radius:9px;border:2px solid #E8B4BC;background:#FDF5F5}
        QRadioButton::indicator:checked{background:#E8B4BC}"""
    BBTN = "QPushButton{background:#E8B4BC;color:white;border:none;border-radius:22px}QPushButton:hover{background:#D9A9B4}"

    def __init__(self, cur, parent=None):
        self.cur = cur
        self.g = QButtonGroup()
        super().__init__(parent)
        self.g.setParent(self)
        self.setWindowTitle("Выбор сложности")
        self.setFixedSize(500, 380)

    def setup_ui(self):
        l = QVBoxLayout(self.mw)
        l.setSpacing(20)
        l.setContentsMargins(35, 35, 35, 35)
        l.addWidget(self._lbl("Выберите сложность", 22))
        for name, id, desc in [("Легкий", 1, "800 мс • 4 кнопки"), ("Средний", 2, "600 мс • 6 кнопок"),
                               ("Сложный", 3, "400 мс • 8 кнопок"), ("Эксперт", 4, "250 мс • 10 кнопок")]:
            rl = QHBoxLayout()
            r = QRadioButton(name, font=QFont("Georgia", 15), styleSheet=self.RADIO, checked=self.cur == name)
            self.g.addButton(r, id)
            rl.addWidget(r)
            rl.addStretch()
            rl.addWidget(QLabel(desc, font=QFont("Georgia", 14), styleSheet=self.SUBTITLE))
            l.addLayout(rl)
        l.addStretch()
        bl = QHBoxLayout()
        bl.setSpacing(20)
        bl.setAlignment(Qt.AlignCenter)
        for t, cb in [("Выбрать", self.accept), ("Отмена", self.reject)]:
            b = QPushButton(t, font=QFont("Georgia", 15), cursor=Qt.PointingHandCursor, styleSheet=self.BBTN)
            b.setFixedSize(150, 45)
            b.clicked.connect(cb)
            bl.addWidget(b)
        l.addLayout(bl)

    def get_difficulty(self):
        return {1: {"name": "Легкий", "speed": 800, "buttons": 4}, 2: {"name": "Средний", "speed": 600, "buttons": 6},
                3: {"name": "Сложный", "speed": 400, "buttons": 8},
                4: {"name": "Эксперт", "speed": 250, "buttons": 10}}.get(
            self.g.checkedId(), {"name": "Легкий", "speed": 800, "buttons": 4})


class MemoryOrderGame(QMainWindow):
    COLORS = ["#F3E3E5", "#EFDADE", "#EBD1D6", "#E7C8CE", "#F2D0D9", "#EDC5D0", "#E8BAC7", "#E3AFC0", "#DEA4B6",
              "#D999AC"]
    BST = """QPushButton{{background:{c};color:#6B4F5A;border:1px solid #D9C0C8;border-radius:{r}px;font-size:{f}px;font-weight:bold;font-family:Georgia}}
        QPushButton:hover{{background:#E3CBD0}}QPushButton:pressed{{background:#D9BCC2;color:white}}QPushButton:disabled{{background:#F5EAEC;color:#C5B0B5}}"""
    MBTN = "QPushButton{background:#E8B4BC;color:white;border:none;border-radius:25px}QPushButton:hover{background:#D9A9B4}"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Запомни порядок")
        self.setWindowState(Qt.WindowMaximized)
        self.bg = QLabel(self)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self.bg.setStyleSheet("background:#FDF5F5")
        self._draw()
        self._init_sounds()
        self._rst()
        self.diff = {"name": "Легкий", "speed": 800, "buttons": 4}
        self.bcnt = self.diff["buttons"]
        self.spd = self.diff["speed"]
        self.recs = self._load()
        self.notif = None
        self.cw = QWidget()
        self.setCentralWidget(self.cw)
        self.ml = QVBoxLayout(self.cw)
        self.ml.setContentsMargins(0, 0, 0, 0)
        self._wui()
        self._gui()
        self._oui()
        self._sw()
        QTimer.singleShot(500, self._rules)

    def _rst(self):
        self.seq = []
        self.pseq = []
        self.lvl = 1
        self.btns = []
        self.showing = False
        self.started = False
        self.clickable = False
        self.show_started = False
        self.name = "Аноним"
        self.sname = "Аноним"

    def _draw(self):
        p = QPixmap(self.size())
        p.fill(QColor("#FDF5F5"))
        pt = QPainter(p)
        pt.setRenderHint(QPainter.Antialiasing)
        pt.setPen(QPen(QColor("#E8B4BC"), 2))
        pt.setBrush(QBrush(QColor("#E8B4BC")))
        pt.setOpacity(0.1)
        for i in range(0, self.width(), 150):
            for j in range(0, self.height(), 150):
                for x, y in [(20, 20), (40, 20), (30, 10), (30, 30)]:
                    pt.drawEllipse(i + x, j + y, 15, 15)
                pt.setBrush(QBrush(QColor("#D9A9B4")))
                pt.drawEllipse(i + 30, j + 20, 10, 10)
                pt.setBrush(QBrush(QColor("#E8B4BC")))
        pt.setPen(QPen(QColor("#C598B0"), 1))
        for i in range(0, self.width(), 200):
            for j in range(0, self.height(), 200):
                pt.drawLine(i + 50, j + 50, i + 80, j + 30)
                pt.drawLine(i + 80, j + 30, i + 100, j + 50)
                pt.drawLine(i + 80, j + 30, i + 90, j + 10)
        pt.setPen(QPen(QColor("#E8B4BC"), 3))
        for i in range(0, self.width(), 50):
            for j in range(0, self.height(), 50):
                pt.drawPoint(i + 25, j + 25)
        pt.end()
        self.bg.setPixmap(p)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        self._draw()

    def _rules(self):
        RulesDialog(self).exec()

    def _recs(self):
        RecordsDialog(self.recs, self).exec()

    def _load(self):
        r = []
        try:
            if os.path.exists("records.json"):
                with open("records.json", "r", encoding="utf-8") as f:
                    old = json.load(f)
                for x in old:
                    x.setdefault("name", "Аноним")
                    r.append(x)
                with open("records.json", "w", encoding="utf-8") as f:
                    json.dump(r, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка: {e}")
        return r

    def _save(self):
        self.recs.append({"name": self.name, "level": self.lvl - 1, "difficulty": self.diff["name"],
                          "date": datetime.now().strftime("%d.%m.%Y %H:%M")})
        self.recs.sort(key=lambda x: x["level"], reverse=True)
        self.recs = self.recs[:15]
        try:
            with open("records.json", "w", encoding="utf-8") as f:
                json.dump(self.recs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка: {e}")

    def _notify(self, lvl, nd):
        if self.notif:
            self.notif.deleteLater()
            self.notif = None
        c = QWidget(styleSheet="background:transparent")
        cl = QVBoxLayout(c)
        cl.setContentsMargins(0, 20, 0, 0)
        cl.setAlignment(Qt.AlignTop)
        lb = QLabel(f"Уровень {lvl}! Сложность повышена до {nd}", alignment=Qt.AlignCenter,
                    font=QFont("Georgia", 18, QFont.Bold),
                    styleSheet="color:#E8B4BC;background:#FDF5F5;border:2px solid #E8B4BC;border-radius:30px;padding:15px 25px")
        cl.addWidget(lb)
        self.ml.insertWidget(0, c, 0, Qt.AlignTop | Qt.AlignHCenter)
        self.notif = c
        QTimer.singleShot(2500, lambda: self._rm_notif(c))

    def _rm_notif(self, n):
        n.deleteLater()
        if self.notif == n:
            self.notif = None

    def _init_sounds(self):
        d = os.path.dirname(os.path.abspath(__file__))
        self.snd = {}
        for n, f, v in [("click", "click.wav", 0.4), ("success", "levelup.wav", 0.3), ("over", "gameover.wav", 0.4)]:
            s = QSoundEffect()
            s.setVolume(v)
            p = os.path.join(d, f)
            if os.path.exists(p):
                s.setSource(QUrl.fromLocalFile(p))
            self.snd[n] = s

    def _play(self, n):
        if n in self.snd and self.snd[n]:
            self.snd[n].play()

    def _exit_dlg(self):
        if ExitConfirmDialog(self.lvl, self).exec() == QDialog.Accepted:
            self._tomenu()

    def _tomenu(self):
        self._save()
        self.showing = False
        self.clickable = False
        self.show_started = False
        for b in self.btns:
            b.setEnabled(False)
        self._sw()
        self.ni.setText(self.sname if self.sname != "Аноним" else "")

    def _sz(self):
        if self.bcnt <= 6:
            return 100, 28
        if self.bcnt <= 8:
            return 90, 24
        return 80, 22

    def _mkbtn(self, i):
        def h():
            if not self.showing and self.clickable and self.btns[i].isEnabled():
                self.clickable = False
                self.pseq.append(i)
                self._play("click")
                sz, fs = self._sz()
                rp = len(self.pseq) > 1 and self.pseq[-2] == i
                c, b = ("#E8B4BC", "2px solid #D9A9B4") if rp else ("#D9BCC2", "1px solid #C5AEB2")
                self.btns[i].setStyleSheet(
                    f"QPushButton{{background:{c};color:white;border:{b};border-radius:{sz // 2}px;font-size:{fs}px;font-weight:bold;font-family:Georgia}}")
                QTimer.singleShot(250 if rp else 200, lambda: self._rstbtn(i))
                QTimer.singleShot(200, self._check)

        return h

    def _rstbtn(self, i):
        if i < len(self.btns):
            sz, fs = self._sz()
            self.btns[i].setStyleSheet(self.BST.format(c=self.bcols[i], r=sz // 2, f=fs))
            self.clickable = True

    def _diffdlg(self):
        d = DifficultyDialog(self.diff["name"], self)
        if d.exec() == QDialog.Accepted:
            self.diff = d.get_difficulty()
            self.bcnt = self.diff["buttons"]
            self.spd = self.diff["speed"]
            self.dl.setText(f"Сложность: {self.diff['name']}")

    def _wui(self):
        self.ww = QWidget(styleSheet="background:transparent")
        l = QVBoxLayout()
        l.setSpacing(20)
        l.setAlignment(Qt.AlignCenter)
        for t, s, c, ls in [("✧ ✦ ✧", 18, "#E0C8D0", "8px"), ("Запомни порядок", 56, "#6B4F5A", "3px"),
                            ("❀ ❁ ❀", 16, "#D9B8C0", "6px")]:
            l.addWidget(QLabel(t, alignment=Qt.AlignCenter,
                               font=QFont("Georgia" if "Запомни" in t else "Segoe UI", s,
                                          QFont.Light if "Запомни" in t else -1),
                               styleSheet=f"color:{c};letter-spacing:{ls};border:none"))
        l.addSpacing(20)
        f = QFrame(
            styleSheet="background:rgba(232,180,188,0.1);border:2px solid #E8B4BC;border-radius:25px;padding:10px")
        fl = QVBoxLayout(f)
        fl.addWidget(QLabel("Введите ваше имя:", alignment=Qt.AlignCenter, font=QFont("Georgia", 12),
                            styleSheet="color:#6B4F5A;border:none"))
        self.ni = QLineEdit(placeholderText="Аноним", maxLength=20, font=QFont("Georgia", 14), alignment=Qt.AlignCenter,
                            styleSheet="background:white;color:#6B4F5A;border:2px solid #E8B4BC;border-radius:20px;padding:5px 15px;font-family:Georgia")
        self.ni.setFixedWidth(300)
        self.ni.setFixedHeight(40)
        fl.addWidget(self.ni, alignment=Qt.AlignCenter)
        l.addWidget(f)
        l.addSpacing(20)
        self.dl = QLabel(f"Сложность: {self.diff['name']}", alignment=Qt.AlignCenter, font=QFont("Georgia", 14),
                         styleSheet="color:#8B6B76;border:none")
        l.addWidget(self.dl)

        diff_btn = QPushButton("Изменить сложность")
        diff_btn.setFont(QFont("Georgia", 14))
        diff_btn.setCursor(Qt.PointingHandCursor)
        diff_btn.setStyleSheet(
            "QPushButton{background:#E8B4BC;color:white;border:none;border-radius:25px}QPushButton:hover{background:#D9A9B4}")
        diff_btn.setFixedWidth(220)
        diff_btn.setFixedHeight(50)
        diff_btn.clicked.connect(self._diffdlg)
        l.addWidget(diff_btn, alignment=Qt.AlignCenter)

        start_btn = QPushButton("Начать игру")
        start_btn.setFont(QFont("Georgia", 16))
        start_btn.setCursor(Qt.PointingHandCursor)
        start_btn.setStyleSheet(
            "QPushButton{background:#E8B4BC;color:white;border:none;border-radius:30px}QPushButton:hover{background:#D9A9B4}")
        start_btn.setFixedWidth(220)
        start_btn.setFixedHeight(60)
        start_btn.clicked.connect(self._startw)
        l.addWidget(start_btn, alignment=Qt.AlignCenter)

        l.addSpacing(10)
        il = QHBoxLayout()
        il.setSpacing(20)
        il.setAlignment(Qt.AlignCenter)
        for t, cb in [("Правила", self._rules), ("Рекорды", self._recs), ("Выход", self.close)]:
            btn = QPushButton(t, font=QFont("Georgia", 14), cursor=Qt.PointingHandCursor, styleSheet=self.MBTN)
            btn.setFixedSize(150, 50)
            btn.clicked.connect(cb)
            il.addWidget(btn)
        l.addLayout(il)
        l.addWidget(QLabel("• ✦ • ✦ •", alignment=Qt.AlignCenter, font=QFont("Segoe UI", 14),
                           styleSheet="color:#E0C8D0;letter-spacing:6px;border:none"))
        self.ww.setLayout(l)

    def _gui(self):
        self.gw = QWidget(styleSheet="background:transparent")
        l = QVBoxLayout()
        l.setSpacing(30)
        l.setContentsMargins(20, 20, 20, 20)
        tp = QWidget(styleSheet="background:transparent")
        tl = QHBoxLayout(tp)
        tl.setContentsMargins(0, 0, 0, 0)
        sp = QWidget()
        sp.setFixedWidth(60)
        tl.addWidget(sp)
        self.tlbl = QLabel("Запомни порядок", alignment=Qt.AlignCenter, font=QFont("Georgia", 32, QFont.Light),
                           styleSheet="color:#6B4F5A;border:none")
        tl.addWidget(self.tlbl, 1)
        eb = QPushButton("✕  Главное меню", font=QFont("Georgia", 11), cursor=Qt.PointingHandCursor,
                         styleSheet="QPushButton{background:#E8B4BC;color:white;border:none;border-radius:18px}QPushButton:hover{background:#D9A9B4}",
                         clicked=self._exit_dlg)
        eb.setFixedSize(140, 36)
        tl.addWidget(eb)
        l.addWidget(tp)
        ip = QWidget(styleSheet="background:transparent")
        il = QHBoxLayout(ip)
        il.setAlignment(Qt.AlignCenter)
        il.setSpacing(30)
        self.pl = QLabel(f"Игрок: {self.name}", font=QFont("Georgia", 12), styleSheet="color:#8B6B76;border:none")
        il.addWidget(self.pl)
        self.ll = QLabel(f"Уровень {self.lvl}", font=QFont("Georgia", 16),
                         styleSheet="color:#8B6B76;font-style:italic;border:none")
        il.addWidget(self.ll)
        self.dgl = QLabel(f"{self.diff['name']}", font=QFont("Georgia", 14), styleSheet="color:#D9A9B4;border:none")
        il.addWidget(self.dgl)
        l.addWidget(ip, alignment=Qt.AlignCenter)
        l.addSpacing(20)
        bc = QWidget(styleSheet="background:transparent")
        self.bgrd = QGridLayout()
        self.bgrd.setSpacing(20)
        self.bgrd.setAlignment(Qt.AlignCenter)
        self._cbtns()
        bc.setLayout(self.bgrd)
        l.addWidget(bc, 1)
        self.gw.setLayout(l)

    def _cbtns(self):
        self.bcols = [self.COLORS[i % len(self.COLORS)] for i in range(self.bcnt)]
        cols = self.bcnt // 2
        sz, fs = self._sz()
        for i in range(self.bcnt):
            b = QPushButton("", font=QFont("Georgia", fs, QFont.Bold), cursor=Qt.PointingHandCursor,
                            styleSheet=self.BST.format(c=self.bcols[i], r=sz // 2, f=fs), clicked=self._mkbtn(i))
            b.setFixedSize(sz, sz)
            b.setEnabled(False)
            self.btns.append(b)
            self.bgrd.addWidget(b, i // cols, i % cols)

    def _rbtns(self):
        sz, fs = self._sz()
        for i, b in enumerate(self.btns):
            b.setText(str(i + 1))
            b.setStyleSheet(self.BST.format(c=self.bcols[i], r=sz // 2, f=fs))

    def _oui(self):
        self.ow = QWidget(styleSheet="background:transparent")
        l = QVBoxLayout()
        l.setSpacing(20)
        l.setAlignment(Qt.AlignCenter)
        l.addWidget(
            QLabel("✧", alignment=Qt.AlignCenter, font=QFont("Segoe UI", 24), styleSheet="color:#E0C8D0;border:none"))
        l.addWidget(QLabel("Игра окончена", alignment=Qt.AlignCenter, font=QFont("Georgia", 48, QFont.Light),
                           styleSheet="color:#6B4F5A;font-style:italic;border:none"))
        self.rl = QLabel("", alignment=Qt.AlignCenter, font=QFont("Georgia", 18),
                         styleSheet="color:#8B6B76;border:none")
        l.addWidget(self.rl)
        l.addSpacing(20)
        bl = QHBoxLayout()
        bl.setSpacing(20)
        bl.setAlignment(Qt.AlignCenter)
        for t, cb in [("Играть снова", self._again), ("Главное меню", self._tomenu_main), ("Выход", self.close)]:
            btn = QPushButton(t, font=QFont("Georgia", 14), cursor=Qt.PointingHandCursor, styleSheet=self.MBTN)
            btn.setFixedSize(150, 50)
            btn.clicked.connect(cb)
            bl.addWidget(btn)
        l.addLayout(bl)
        self.ow.setLayout(l)

    def _again(self):
        self.lvl = 1
        self.seq = []
        self.pseq = []
        self.clickable = False
        self._sg()
        self.pl.setText(f"Игрок: {self.name}")
        self.dgl.setText(f"{self.diff['name']}")
        self.bcnt = self.diff["buttons"]
        self.spd = self.diff["speed"]
        self._updbtns()
        self._rbtns()
        self._start()

    def _tomenu_main(self):
        self.sname = self.name
        self._sw()

    def _updbtns(self):
        for b in self.btns:
            b.deleteLater()
        self.btns = []
        while self.bgrd.count():
            it = self.bgrd.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        self._cbtns()

    def _startw(self):
        self.name = self.ni.text().strip() or "Аноним"
        self.sname = self.name
        self.bcnt = self.diff["buttons"]
        self.spd = self.diff["speed"]
        self._updbtns()
        self._sg()
        self.pl.setText(f"Игрок: {self.name}")
        self._rbtns()
        self._start()

    def _start(self):
        self.started = True
        self.lvl = 1
        self.ll.setText(f"Уровень {self.lvl}")
        self.dgl.setText(f"{self.diff['name']}")
        self._level()

    def _level(self):
        for b in self.btns:
            b.setEnabled(False)
        if self.lvl == 1:
            self.seq = [random.randint(0, self.bcnt - 1)]
        else:
            self.seq.append(random.randint(0, self.bcnt - 1))
        self.pseq = []
        self.showing = True
        self.clickable = False
        self.show_started = False
        self.tlbl.setText("Запоминайте...")
        QTimer.singleShot(500, self._shseq)

    def _shseq(self):
        self.show_started = True
        r = 0
        e = 0
        for i, idx in enumerate(self.seq):
            if i > 0 and self.seq[i] == self.seq[i - 1]:
                r += 1
            else:
                r = 0
            ed = 100 * r if self.diff["name"] == "Эксперт" and r > 0 else 0
            if ed:
                e += ed
            QTimer.singleShot(int(self.spd * i) + e, lambda x=idx: self._hl(x))
        QTimer.singleShot(int(self.spd * len(self.seq) + 300 + e), self._allow)

    def _hl(self, i):
        if not self.show_started or i >= len(self.btns):
            return
        sz, fs = self._sz()
        self.btns[i].setStyleSheet(
            f"QPushButton{{background:#D9BCC2;color:white;border:1px solid #C5AEB2;border-radius:{sz // 2}px;font-size:{fs}px;font-weight:bold;font-family:Georgia}}")
        QTimer.singleShot(300, lambda: self._rstbtn(i))

    def _allow(self):
        self.showing = False
        self.clickable = True
        self.tlbl.setText("Ваш ход")
        for b in self.btns:
            b.setEnabled(True)

    def _check(self):
        if not self.pseq:
            return
        if self.pseq[-1] != self.seq[len(self.pseq) - 1]:
            self._over()
        elif len(self.pseq) == len(self.seq):
            self._done()

    def _done(self):
        self.lvl += 1
        self.ll.setText(f"Уровень {self.lvl}")
        self._play("success")
        QTimer.singleShot(200, self._level)

    def _over(self):
        self.clickable = False
        for b in self.btns:
            b.setEnabled(False)
        self._save()
        self.rl.setText(f"{self.name}, вы дошли до {self.lvl} уровня")
        self._play("over")
        self._so()

    def _sw(self):
        self._clr()
        self.ml.addWidget(self.ww)
        self.ww.show()

    def _sg(self):
        self._clr()
        self.ml.addWidget(self.gw)
        self.gw.show()

    def _so(self):
        self._clr()
        self.ml.addWidget(self.ow)
        self.ow.show()

    def _clr(self):
        while self.ml.count():
            it = self.ml.takeAt(0)
            if it.widget():
                it.widget().hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MemoryOrderGame()
    w.show()
    sys.exit(app.exec())