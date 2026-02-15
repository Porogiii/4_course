import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from control import TCtrl


class UniversalCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор универсальный")
        self.setGeometry(100, 100, 440, 700)
        self.setMinimumSize(400, 650)

        self.mode = "p"
        self.ctrl = TCtrl(self.mode)

        self.init_ui()
        self.update_display()

    def init_ui(self):
        # Меню
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Справка")
        help_action = QAction("Справка (F1)", self)
        help_action.setShortcut("F1")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        # Тулбар режимов
        toolbar = QToolBar("Режимы")
        self.addToolBar(toolbar)
        toolbar.addWidget(QLabel("Режим:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["p-ичные", "Дроби", "Комплекс"])
        self.mode_combo.currentTextChanged.connect(self.change_mode)
        toolbar.addWidget(self.mode_combo)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Дисплей
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setFont(QFont("Consolas", 28, QFont.Weight.Bold))
        self.display.setStyleSheet("""
            QLineEdit {
                padding: 25px 20px; margin: 20px;
                border: 3px solid #666; border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                    stop:0 #2c3e50, stop:1 #34495e);
                color: #ffffff;
            }
        """)
        layout.addWidget(self.display)

        # Статус памяти
        self.mem_label = QLabel("Память: пусто")
        self.mem_label.setStyleSheet("color: #95a5a6; font-size: 12px; padding: 10px; background: #ecf0f1;")
        layout.addWidget(self.mem_label)

        # Cетка 7x4
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setContentsMargins(25, 15, 25, 25)

        # Кнопки
        buttons = [
            [('MC', 0, 0), ('MR', 0, 1), ('MS', 0, 2), ('M+', 0, 3)],
            [('C', 1, 0), ('±', 1, 1), ('.', 1, 2), ('⌫', 1, 3)],
            [('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3)],
            [('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3)],
            [('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3)],
            [('0', 5, 0), ('x²', 5, 1), ('1/x', 5, 2), ('+', 5, 3)]
        ]

        for row_group in buttons:
            for text, row, col in row_group:
                btn = self.create_button(text, row, col)
                grid.addWidget(btn, row, col)

        # Кнопка "="
        eq_layout = QHBoxLayout()
        eq_layout.addStretch(1)
        eq_btn = QPushButton("=")
        eq_btn.setFixedSize(260, 70)
        eq_btn.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        eq_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #27ae60,stop:1 #2ecc71);
                border: none; border-radius: 14px; color: white;
            }
            QPushButton:hover { background: #2ecc71; }
            QPushButton:pressed { background: #27ae60; }
        """)
        eq_btn.clicked.connect(lambda: self.button_click("="))
        eq_layout.addWidget(eq_btn)
        eq_layout.addStretch(1)
        grid.addLayout(eq_layout, 6, 0, 1, 4)

        layout.addLayout(grid)

    def create_button(self, text: str, row: int, col: int):
        btn = QPushButton(text)
        btn.setMinimumSize(75, 55)
        btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))

        # Цветовая схема
        if text in ('/', '*', '-', '+'):
            c1, c2 = "#9b59b6", "#8e44ad"
        elif text in ('MC', 'MR', 'MS', 'M+'):
            c1, c2 = "#3498db", "#2980b9"
        elif text in ('C', '±', '.', '⌫'):
            c1, c2 = "#e74c3c", "#c0392b"
        elif text in ('x²', '1/x'):
            c1, c2 = "#f39c12", "#e67e22"
        else:  # цифры
            c1, c2 = "#95a5a6", "#7f8c8d"

        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 {c1},stop:1 {c2});
                border: 2px solid {c2}; border-radius: 10px; color: white;
            }}
            QPushButton:hover {{ background: {c2}; }}
            QPushButton:pressed {{ background: {c1}88; }}
        """)

        btn.clicked.connect(lambda _, t=text: self.button_click(t))
        return btn

    def button_click(self, text):
        """Обработчик."""
        try:
            if text.isdigit():
                self.ctrl.do_editor_command(int(text))
            elif text in '+-*/=':
                self.ctrl.do_calc_command(text)
            elif text == 'C':
                self.ctrl.do_calc_command('C')
            elif text == '±':
                self.ctrl.do_editor_command(10)
            elif text in ('.', '⌫'):
                cmds = {'.': 11, '⌫': 13}
                self.ctrl.do_editor_command(cmds[text])
            elif text in ('MC', 'MR', 'MS', 'M+'):
                self.ctrl.do_memory_command(text)
            elif text == 'x²':
                self.ctrl.do_calc_command('sqr')
            elif text == '1/x':
                self.ctrl.do_calc_command('inv')

            self.update_display()
        except Exception as e:
            self.display.setText(f"Ошибка: {e}")

    def change_mode(self, text):
        modes = {"p-ичные": "p", "Дроби": "f", "Комплекс": "c"}
        self.mode = modes[text]
        self.ctrl = TCtrl(self.mode)
        self.update_display()

    def update_display(self):
        text = self.ctrl.display or "0"
        if text == "-0":
            text = "0"
        self.display.setText(text)
        self.mem_label.setText(
            f"Память: {'есть' if hasattr(self.ctrl, 'memory') and self.ctrl.memory.mem_on == '_On' else 'пусто'}")

    def show_help(self):
        QMessageBox.information(self, "Помощь",
                                "✅ **Режимы:** p-ичные | Дроби | Комплекс\n\n"
                                "🔢 **Цепочка:** 5 + 5 * 2 = 20\n"
                                "📏 **Дроби:** 1/2 + 1/3 = 5/6\n"
                                "🔺 **Комплекс:** 1 . 2 + 3 . 4 = 4 i* 6\n"
                                "💾 **Память:** MS/M+/MR/MC\n\n"
                                "**F1** – справка")

    def keyPressEvent(self, event):
        txt = event.text()
        if txt.isdigit() or txt in '+-*/=':
            self.button_click(txt)
        elif event.key() == Qt.Key.Key_F1:
            self.show_help()
        super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    calculator = UniversalCalculator()
    calculator.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
