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
        """Арифметика."""
        try:
            # Создание числа по режиму
            if self.mode == "p":
                num = TPNumber(self.editor.string)
            elif self.mode == "f":
                num = TFrac(self.editor.string)
            else:
                num = TComp(self.editor.string)

            if cmd in ('+', '-', '*', '/'):
                self.processor.lop_res = num
                if cmd == '+':
                    self.processor.operation = TOprtn.ADD
                elif cmd == '-':
                    self.processor.operation = TOprtn.SUB
                elif cmd == '*':
                    self.processor.operation = TOprtn.MUL
                elif cmd == '/':
                    self.processor.operation = TOprtn.DVD
                self.editor.clear()
                return num.string  # Показываем введённое число

            elif cmd == '=':
                self.processor.rop = num
                self.processor.oprtn_run()
                if self.processor.error:
                    self.editor.string = self.processor.error
                    return self.processor.error
                result = self.processor.lop_res
                self.editor.string = result.string
                return result.string

            elif cmd == 'C':
                self.editor.clear()
                self.processor.reset()
                return "0"

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

        except Exception as e:
            self.editor.string = f"ERR: {e}"
            return self.editor.string

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
