import sys

transitions_rpn = {
    ('q0', 'n', 'Z'): ('q0', 'none', 'n'),
    ('q0', 'n', '+'): ('q0', 'none', 'n'),
    ('q0', '­n', '-'): ('q0', 'none', 'n'),
    ('q0', 'n', '*'): ('q0', 'none', 'n'),
    ('q0', 'n', '/'): ('q0', 'none', 'n'),
    ('q0', 'n', '('): ('q0', 'none', 'n'),

    ('q0', '(', 'Z'): ('q0', 'push:(', ''),
    ('q0', '(', '+'): ('q0', 'push:(', ''),
    ('q0', '(', '-'): ('q0', 'push:(', ''),
    ('q0', '(', '*'): ('q0', 'push:(', ''),
    ('q0', '(', '/'): ('q0', 'push:(', ''),
    ('q0', '(', '('): ('q0', 'push:(', ''),

    ('q0', ')', '('): ('q0', 'pop', ''),
    ('q0', ')', '+'): ('q_(', 'pop', '+'),
    ('q0', ')', '-'): ('q_(', 'pop', '-'),
    ('q0', ')', '*'): ('q_(', 'pop', '*'),
    ('q0', ')', '/'): ('q_(', 'pop', '/'),

    ('q_(', '', '('): ('q0', 'pop', ''),
    ('q_(', '', '+'): ('q_(', 'pop', '+'),
    ('q_(', '', '-'): ('q_(', 'pop', '-'),
    ('q_(', '', '*'): ('q_(', 'pop', '*'),
    ('q_(', '', '/'): ('q_(', 'pop', '/'),

    # + и - НЕ выталкивают * и /
    ('q0', '+', 'Z'): ('q0', 'push:+', ''),
    ('q0', '+', '('): ('q0', 'push:+', ''),
    ('q0', '+', '+'): ('q_+', 'pop', '+'),
    ('q0', '+', '-'): ('q_+', 'pop', '-'),
    # ← НЕТ переходов для * и / — остаёмся в q0 и кладём +

    ('q_+', '', 'Z'): ('q0', 'push:+', ''),
    ('q_+', '', '('): ('q0', 'push:+', ''),
    ('q_+', '', '+'): ('q_+', 'pop', '+'),
    ('q_+', '', '-'): ('q_+', 'pop', '-'),
    # ← НЕТ для * и /

    ('q0', '-', 'Z'): ('q0', 'push:-', ''),
    ('q0', '-', '('): ('q0', 'push:-', ''),
    ('q0', '-', '+'): ('q_-', 'pop', '+'),
    ('q0', '-', '-'): ('q_-', 'pop', '-'),

    ('q_-', '', 'Z'): ('q0', 'push:-', ''),
    ('q_-', '', '('): ('q0', 'push:-', ''),
    ('q_-', '', '+'): ('q_-', 'pop', '+'),
    ('q_-', '', '-'): ('q_-', 'pop', '-'),

    ('q0', '*', 'Z'): ('q0', 'push:*', ''),
    ('q0', '*', '('): ('q0', 'push:*', ''),
    ('q0', '*', '+'): ('q0', 'push:*', ''),
    ('q0', '*', '-'): ('q0', 'push:*', ''),
    ('q0', '*', '*'): ('q_*', 'pop', '*'),
    ('q0', '*', '/'): ('q_*', 'pop', '/'),

    ('q_*', '', 'Z'): ('q0', 'push:*', ''),
    ('q_*', '', '('): ('q0', 'push:*', ''),
    ('q_*', '', '+'): ('q0', 'push:*', ''),
    ('q_*', '', '-'): ('q0', 'push:*', ''),
    ('q_*', '', '*'): ('q_*', 'pop', '*'),
    ('q_*', '', '/'): ('q_*', 'pop', '/'),

    ('q0', '/', 'Z'): ('q0', 'push:/', ''),
    ('q0', '/', '('): ('q0', 'push:/', ''),
    ('q0', '/', '+'): ('q0', 'push:/', ''),
    ('q0', '/', '-'): ('q0', 'push:/', ''),
    ('q0', '/', '*'): ('q_/', 'pop', '*'),
    ('q0', '/', '/'): ('q_/', 'pop', '/'),

    ('q_/', '', 'Z'): ('q0', 'push:/', ''),
    ('q_/', '', '('): ('q0', 'push:/', ''),
    ('q_/', '', '+'): ('q0', 'push:/', ''),
    ('q_/', '', '-'): ('q0', 'push:/', ''),
    ('q_/', '', '*'): ('q_/', 'pop', '*'),
    ('q_/', '', '/'): ('q_/', 'pop', '/'),

    ('q0', '', 'Z'): ('qf', 'pop', ''),
    ('q0', '', '+'): ('q_pop_all', 'pop', '+'),
    ('q0', '', '-'): ('q_pop_all', 'pop', '-'),
    ('q0', '', '*'): ('q_pop_all', 'pop', '*'),
    ('q0', '', '/'): ('q_pop_all', 'pop', '/'),

    ('q_pop_all', '', 'Z'): ('qf', 'pop', ''),
    ('q_pop_all', '', '+'): ('q_pop_all', 'pop', '+'),
    ('q_pop_all', '', '-'): ('q_pop_all', 'pop', '-'),
    ('q_pop_all', '', '*'): ('q_pop_all', 'pop', '*'),
    ('q_pop_all', '', '/'): ('q_pop_all', 'pop', '/'),
}

transitions_lang = {
    ('q0', 'a', 'Z'): ('q1', 'push:a', ''),
    ('q1', 'a', 'a'): ('q1', 'push:a', ''),
    ('q1', 'a', 'Z'): ('q1', 'push:a', ''),
    ('q1', 'c', 'a'): ('q2', 'none', ''),
    ('q2', 'c', 'a'): ('q2', 'none', ''),
    ('q2', 'b', 'a'): ('q3', 'pop', ''),
    ('q3', 'b', 'a'): ('q3', 'pop', ''),
    ('q2', '', 'a'): ('qf', 'none', ''),
    ('q3', '', 'a'): ('qf', 'none', ''),

    ('q0', '', 'Z'): ('reject', 'none', ''),
    ('q0', 'c', 'Z'): ('reject', 'none', ''),
    ('q0', 'b', 'Z'): ('reject', 'none', ''),
    ('q1', 'c', 'Z'): ('reject', 'none', ''),
    ('q1', 'b', 'a'): ('reject', 'none', ''),
    ('q3', 'b', 'Z'): ('reject', 'none', ''),
    ('q3', '', 'Z'): ('reject', 'none', ''),
    ('q2', '', 'Z'): ('reject', 'none', ''),
}

def tokenize(expression):
    tokens = []
    i = 0
    while i < len(expression):
        if expression[i].isspace():
            i += 1
            continue
        if expression[i].isdigit():
            num = ''
            while i < len(expression) and expression[i].isdigit():
                num += expression[i]
                i += 1
            tokens.append(('n', num))
            continue
        if expression[i] in '+-*/()':
            tokens.append((expression[i], expression[i]))
            i += 1
            continue
        raise ValueError(f"Недопустимый символ: {expression[i]}")
    return tokens

def convert_to_rpn_verbose(expression):
    print(f"\nВходное выражение: {expression}")
    print("=" * 70)
    print(f"{'Шаг':<4} {'Вход':<18} {'Состояние':<10} {'Стек':<25} {'Выход (ОПЗ)':<30}")
    print("-" * 70)

    try:
        tokens = tokenize(expression)
    except ValueError as e:
        print(f"Ошибка: {e}")
        return

    state = 'q0'
    stack = ['Z']
    output = []
    i = 0
    step = 0

    while True:
        step += 1

        if state == 'qf' and len(stack) <= 1:
            print(f"{step:<4} {'ГОТОВО':<18} {'qf':<10} {'Пусто':<25} {' '.join(output):<30}")
            print("-" * 70)
            print(f"Результат в ОПЗ: {' '.join(output)}")
            return

        if i < len(tokens):
            symbol, actual = tokens[i]
            input_str = f"{actual} (тип: {symbol})"
        else:
            symbol = ''
            input_str = "ε (конец)"

        top = stack[-1] if stack else None
        key = (state, symbol, top) if top else None

        if key not in transitions_rpn and top:
            key = (state, '', top)
            if key in transitions_rpn:
                input_str = "ε-переход"

        if key not in transitions_rpn:
            print(f"Ошибка: нет перехода для {state}, '{symbol}', {top}")
            return

        new_state, action, out = transitions_rpn[key]

        print(f"{step:<4} {input_str:<18} {state:<10} {' '.join(stack):<25} {' '.join(output):<30}")

        if out and out != 'none':
            output.append(actual if out == 'n' else out)

        if action.startswith('push:'):
            stack.append(action[5:])
        elif action == 'pop':
            if stack:
                stack.pop()

        state = new_state
        if symbol:
            i += 1

def check_language(s):
    print(f"\nПроверяем строку: → {s} ←")
    print("=" * 80)
    print(f"{'Шаг':<4} {'Ввод':<8} {'Сост.':<10} {'Стек':<25} {'Действие'}")
    print("-" * 80)

    state = 'q0'
    stack = ['Z']
    i = 0
    step = 0

    while True:
        step += 1

        if state == 'qf':
            print(f"{step:<4} {'ГОТОВО':<8} {'qf':<10} {'Пусто':<25} {'ПРИНЯТО!'}")
            print("-" * 80)
            return

        if state == 'reject':
            print(f"{step:<4} {'ОТКЛОНЕНО':<8} {'reject':<10} {'—':<25} {'НЕ ПРИНАДЛЕЖИТ'}")
            print("-" * 80)
            return

        sym = s[i] if i < len(s) else ''
        inp = sym if i < len(s) else 'ε'

        top = stack[-1]

        key = (state, sym, top)
        if key not in transitions_lang:
            if i >= len(s):
                key = (state, '', top)
                if key in transitions_lang:
                    inp = 'ε-переход'
                else:
                    key = None
            else:
                key = None

        if key not in transitions_lang:
            print(f"{step:<4} {inp:<8} {state:<10} {' '.join(stack):<25} {'НЕТ ПЕРЕХОДА → ОТКЛОНЕНО'}")
            print("-" * 80)
            return

        new_state, action, _ = transitions_lang[key]
        comment = "ничего"
        if action.startswith('push:'):
            comment = f"push {action[5:]}"
        elif action == 'pop':
            comment = "pop"

        print(f"{step:<4} {inp:<8} {state}→{new_state:<5} {' '.join(stack):<25} {comment}")

        if action.startswith('push:'):
            stack.append(action[5:])
        elif action == 'pop':
            if stack and stack[-1] != 'Z':
                stack.pop()

        state = new_state
        if sym:
            i += 1

def main():
    print("1 → Обратная полька")
    print("2 → Проверка языка")
    print("0 → Выход")

    while True:
        choice = input("\nВыберите режим (0-2): ").strip()

        if choice == '1':
            print("РЕЖИМ 1: Обратная полька")
            while True:
                expr = input("\nВыражение (или 'назад'): ").strip()
                if expr.lower() in ['назад', 'back', '0']:
                    break
                if expr:
                    convert_to_rpn_verbose(expr)

        elif choice == '2':
            print("РЕЖИМ 2: Проверка языка")
            while True:
                s = input("\nСтрока (a,b,c) или 'назад': ").strip()
                if s.lower() in ['назад', 'back', '0']:
                    break
                if not all(c in 'abc' for c in s):
                    print("Только a, b, c!")
                    continue
                check_language(s)

        elif choice == '0':
            break
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main()