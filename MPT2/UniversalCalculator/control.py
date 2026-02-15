from anumber import TANumber, TPNumber, TFrac, TComp
from aeditor import AEditor, PEditor, FEditor, CEditor
from memory import TMemory
from processor import TProc, TOprtn, TFunc


class TCtrl:

    def __init__(self, mode: str = "p"):
        self.mode = mode
        self._state = 0

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
    def display(self):
        return self.editor.string

    def do_editor_command(self, cmd: int):
        """0-9, ±(10), .(11), ⌫(13)."""
        self.editor.edit(cmd)
        return self.editor.string

    def do_calc_command(self, cmd: str):
        try:
            editor_str = self.editor.string.strip() or "0"
            if self.mode == "p":
                num = TPNumber(editor_str)
            elif self.mode == "f":
                num = TFrac(editor_str)
            else:
                num = TComp(editor_str)

            if not hasattr(self, '_calc_stack'):
                self._calc_stack = [num]
                self._op_stack = []
            else:
                self._calc_stack.append(num)

            if cmd in '+-*/':
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

                self._calc_stack = []
                self._op_stack = []
                return final_result.string

            elif cmd == 'C':
                self.editor.clear()
                self._calc_stack = []
                self._op_stack = []
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

            return self.editor.string

        except Exception as e:
            self.editor.string = f"ERR: {e}"
            self._calc_stack = []
            self._op_stack = []
            return self.editor.string

    def get_priority(self, op: str):
        return {'*': 3, '/': 3, '+': 2, '-': 2}[op]

    def _op_to_enum(self, op: str):
        return {'+': TOprtn.ADD, '-': TOprtn.SUB, '*': TOprtn.MUL, '/': TOprtn.DVD}[op]

    def do_memory_command(self, cmd: str):
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

    def get_priority(self, op: str):
        return {'*': 3, '/': 3, '+': 2, '-': 2}[op]

    def do_chain_operation(self, cmd: str):
        try:
            if self.mode == "p":
                num = TPNumber(self.editor.string)
            elif self.mode == "f":
                num = TFrac(self.editor.string)
            else:
                num = TComp(self.editor.string)

            pending_op = getattr(self, '_pending_op', None)
            pending_num = getattr(self, '_pending_num', num)

            if pending_op:
                if pending_op == '+':
                    pending_num = pending_num.add(num)
                elif pending_op == '-':
                    pending_num = pending_num.sub(num)
                elif pending_op == '*':
                    pending_num = pending_num.mul(num)
                elif pending_op == '/':
                    pending_num = pending_num.div(num)

            if cmd == '=':
                self.editor.string = pending_num.string
                self._pending_op = None
                return pending_num.string
            else:
                self._pending_num = pending_num
                self._pending_op = cmd
                self.editor.clear()
                self.processor.lop_res = pending_num
                self.processor.operation = self._op_to_toprtn(cmd)
                return pending_num.string

        except Exception as e:
            self.editor.string = f"ERR: {e}"
            return self.editor.string

    def _op_to_toprtn(self, op: str):
        return {'+': TOprtn.ADD, '-': TOprtn.SUB, '*': TOprtn.MUL, '/': TOprtn.DVD}[op]
