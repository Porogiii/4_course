from __future__ import annotations
from typing import List, Optional

def precedence(op: str) -> int:
    if op in ('+', '-'): return 1
    if op in ('*', '/'): return 2
    return 0

class RPNError(Exception):
    def __init__(self, message: str, position: int, char: Optional[str] = None):
        self.message = message
        self.position = position
        self.char = char
        super().__init__(
            f"Ошибка в позиции {position}: {message}"
            + (f" ('{char}')" if char else "")
        )

def print_step(
    step: int,
    state: str,
    input_char: str,
    stack: List[str],
    output: List[str],
    pos: int,
) -> None:
    stack_str = " ".join(stack) if stack else "пуст"
    out_str = " ".join(output) if output else "пусто"
    print(
        f"Шаг {step:2d} | Сост: {state:<8} | Вход: '{input_char}' "
        f"| Стек: [{stack_str}] | Выход: [{out_str}] | Позиция: {pos}"
    )

def to_rpn_with_trace(expression: str) -> str:
    expr = expression.strip()
    if not expr:
        raise RPNError("Пустое выражение", 0)

    state: str = "q0"
    stack: List[str] = ["Z0"]
    output: List[str] = []
    i: int = 0
    n: int = len(expr)
    step: int = 0
    current_num: str = ""
    current_op: Optional[str] = None   # λ‑переход

    print("\n=== НАЧАЛО ПРЕОБРАЗОВАНИЯ В ОПЗ ===")
    print(f"Вход: '{expression}'")
    print("-" * 85)

    while i <= n:
        step += 1
        input_char = expr[i] if i < n else "$"
        pos = i if i < n else n

        if state == "q_num":
            if i < n and expr[i].isdigit():
                current_num += expr[i]
                i += 1
                print_step(step, state, expr[i - 1], stack.copy(), output.copy(), i - 1)
                continue
            else:
                if not current_num:
                    raise RPNError("Неполное число", pos)
                output.append(current_num)
                current_num = ""
                state = "q0"
                print_step(step, state, f"num={output[-1]}", stack.copy(), output.copy(), pos)
                continue

        if state == "q_pop":
            popped = False

            if current_op is not None:
                while (
                    stack[-1] != "Z0"
                    and precedence(current_op) <= precedence(stack[-1])
                ):
                    op_out = stack.pop()
                    output.append(op_out)
                    popped = True
                    print_step(step, state, "λ (pop)", stack.copy(), output.copy(), pos)
                    step += 1
            else:
                while stack[-1] != "Z0":
                    op_out = stack.pop()
                    output.append(op_out)
                    popped = True
                    print_step(step, state, "λ (pop all)", stack.copy(), output.copy(), pos)
                    step += 1

            if popped:
                continue

            if current_op is not None:
                stack.append(current_op)
                current_op = None
                state = "q0"
                print_step(step, state, "λ (push)", stack.copy(), output.copy(), pos)
            else:
                state = "q_end"
            continue

        if state == "q0":
            if i == n:
                input_char = "$"
            elif expr[i].isspace():
                i += 1
                print_step(step, state, "пробел", stack.copy(), output.copy(), i - 1)
                continue
            elif expr[i].isdigit():
                current_num = expr[i]
                i += 1
                state = "q_num"
                print_step(step, state, expr[i - 1], stack.copy(), output.copy(), i - 1)
                continue
            elif expr[i] in "+-*/":
                prev_char = expr[i-1] if i > 0 else ""
                if not prev_char.isdigit() and not prev_char.isspace():
                    raise RPNError("Оператор без левого операнда", i, expr[i])
                current_op = expr[i]
                state = "q_pop"
                i += 1
                print_step(step, "q0→q_pop", current_op, stack.copy(), output.copy(), i - 1)
                continue
            else:
                raise RPNError("Недопустимый символ", i, expr[i])

        if i == n and state == "q0":
            state = "q_pop"
            current_op = None  # вытолкнуть всё
            print_step(step, "q0→q_pop", "$", stack.copy(), output.copy(), pos)
            continue

        print_step(step, state, input_char, stack.copy(), output.copy(), pos)

        if state == "q_end":
            break

    if stack != ["Z0"]:
        raise RPNError("Незавершённое выражение (операторы остались в стеке)", n)

    print("-" * 85)
    result = " ".join(output)
    print(f"ИТОГ: {result}")
    print("=== ПРЕОБРАЗОВАНИЕ УСПЕШНО ЗАВЕРШЕНО ===\n")
    return result


if __name__ == "__main__":
    test_cases = [
        "5 + 3 * 2",     # 5 3 2 * +
        "10 / 2 + 3",    # 10 2 / 3 +
        "5 + + 3",       # ошибка
        "5 +",           # ошибка
        "abc",           # ошибка
        "",              # ошибка
        "5+3*2",         # 5 3 2 * +
    ]

    for expr in test_cases:
        print("\n" + "=" * 70)
        print(f"ВЫРАЖЕНИЕ: {expr!r}")
        print("=" * 70)
        try:
            rpn = to_rpn_with_trace(expr)
        except RPNError as e:
            print(f"\n{e}")
        except Exception as e:
            print(f"\nНеизвестная ошибка: {e}")