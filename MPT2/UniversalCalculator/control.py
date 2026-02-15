# control.py – ПОЛНЫЙ РАБОЧИЙ
from anumber import TANumber, TPNumber, TFrac, TComp
from aeditor import AEditor, PEditor, FEditor, CEditor  # 🔥 ИСПРАВЛЕНО: все импорты!
from memory import TMemory
from processor import TProc, TOprtn, TFunc  # 🔥 Добавлен TFunc!


class TCtrl:
    """Управление калькулятором."""

    def __init__(self, mode: str = "p"):
        self.mode = mode
        self._state = 0

        # 🔥 ИСПРАВЛЕНО: правильный редактор по режиму
        if mode == "p":
            self.editor: AEditor = PEditor()
        elif mode == "f":
            self.editor = FEditor()
        else:  # "c"
            self.editor = CEditor()

        zero_num = TPNumber("0")
        self.processor = TProc(zero_num, zero_num)
        self.memory = TMemory(zero_num)

    @property
    def display(self) -> str:
        return self.editor.string

    def do_editor_command(self, cmd: int) -> str:
        """0-9, ±(10), .(11), ⌫(13)."""
        self.editor.edit(cmd)
        return self.editor.string

    def do_calc_command(self, cmd: str) -> str:
        """🔥 ТОЧНЫЙ парсер: 5-5*5=-20."""
        try:
            # Читаем число
            editor_str = self.editor.string.strip() or "0"
            if self.mode == "p":
                num = TPNumber(editor_str)
            elif self.mode == "f":
                num = TFrac(editor_str)
            else:
                num = TComp(editor_str)

            # Инициализация
            if not hasattr(self, '_calc_stack'):
                self._calc_stack = [num]  # Стек чисел
                self._op_stack = []  # Стек операций
            else:
                self._calc_stack.append(num)

            if cmd in '+-*/':
                # 🔥 Shunting-yard: выполняем приоритеты
                while (self._op_stack and self.get_priority(cmd) <= self.get_priority(self._op_stack[-1])):
                    op = self._op_stack.pop()
                    b = self._calc_stack.pop()
                    a = self._calc_stack.pop()

                    if op == '+':
                        result = a.add(b)
                    elif op == '-':
                        result = a.sub(b)
                    elif op == '*':
                        result = a.mul(b)
                    elif op == '/':
                        result = a.div(b)

                    self._calc_stack.append(result)

                self._op_stack.append(cmd)
                self.editor.clear()
                return self._calc_stack[-1].string

            elif cmd == '=':
                # Выполняем ВСЕ операции
                while self._op_stack:
                    op = self._op_stack.pop()
                    b = self._calc_stack.pop()
                    a = self._calc_stack.pop()

                    if op == '+':
                        result = a.add(b)
                    elif op == '-':
                        result = a.sub(b)
                    elif op == '*':
                        result = a.mul(b)
                    elif op == '/':
                        result = a.div(b)

                    self._calc_stack.append(result)

                final_result = self._calc_stack.pop()
                self.editor.string = final_result.string

                # Сброс
                self._calc_stack = []
                self._op_stack = []
                return final_result.string

            elif cmd == 'C':
                self.editor.clear()
                self._calc_stack = []
                self._op_stack = []
                return "0"

            # sqr/inv
            elif cmd == 'sqr':
                self.processor.rop = num
                self.processor.func_run(TFunc.SQR)
                self.editor.string = self.processor.rop.string
                return self.editor.string
            elif cmd == 'inv':
                self.processor.rop = num
                self.processor.func_run(TFunc.REV)
                self.editor.string = self.processor.rop.string
                return self.editor.string

            return self.editor.string

        except Exception as e:
            self.editor.string = f"ERR: {e}"
            self._calc_stack = []
            self._op_stack = []
            return self.editor.string

    def get_priority(self, op: str) -> int:
        """* / = 3, + - = 2."""
        return {'*': 3, '/': 3, '+': 2, '-': 2}[op]

    def _op_to_enum(self, op: str) -> TOprtn:
        """Строка → TOprtn."""
        return {'+': TOprtn.ADD, '-': TOprtn.SUB, '*': TOprtn.MUL, '/': TOprtn.DVD}[op]

    def do_memory_command(self, cmd: str) -> str:
        """Память."""
        try:
            if self.mode == "p":
                num = TPNumber(self.editor.string)
            elif self.mode == "f":
                num = TFrac(self.editor.string)
            else:
                num = TComp(self.editor.string)

            if cmd == 'MS':
                self.memory.mem_store(num)
            elif cmd == 'M+':
                self.memory.mem_add(num)
            elif cmd == 'MR':
                restored = self.memory.mem_restore()
                self.editor.string = restored.string
            elif cmd == 'MC':
                self.memory.mem_clear()

            return self.editor.string
        except Exception as e:
            return f"ERR: {e}"

    def get_priority(self, op: str) -> int:
        """Приоритет операций."""
        return {'*': 3, '/': 3, '+': 2, '-': 2}[op]

    def do_chain_operation(self, cmd: str) -> str:
        """Цепочка операций с приоритетом."""
        try:
            # Читаем число
            if self.mode == "p":
                num = TPNumber(self.editor.string)
            elif self.mode == "f":
                num = TFrac(self.editor.string)
            else:
                num = TComp(self.editor.string)

            pending_op = getattr(self, '_pending_op', None)
            pending_num = getattr(self, '_pending_num', num)

            if pending_op:
                # Выполняем предыдущую операцию
                if pending_op == '+':
                    pending_num = pending_num.add(num)
                elif pending_op == '-':
                    pending_num = pending_num.sub(num)
                elif pending_op == '*':
                    pending_num = pending_num.mul(num)
                elif pending_op == '/':
                    pending_num = pending_num.div(num)

            if cmd == '=':
                # Финальный результат
                self.editor.string = pending_num.string
                self._pending_op = None
                return pending_num.string
            else:
                # Сохраняем для следующей операции
                self._pending_num = pending_num
                self._pending_op = cmd
                self.editor.clear()
                self.processor.lop_res = pending_num  # Для совместимости
                self.processor.operation = self._op_to_toprtn(cmd)
                return pending_num.string  # Показываем промежуточный результат

        except Exception as e:
            self.editor.string = f"ERR: {e}"
            return self.editor.string

    def _op_to_toprtn(self, op: str) -> TOprtn:
        """Операция → TOprtn."""
        return {'+': TOprtn.ADD, '-': TOprtn.SUB, '*': TOprtn.MUL, '/': TOprtn.DVD}[op]
