class DPDA:
    def __init__(self, transitions, initial_state, initial_stack_symbol, final_states):
        """
        Инициализация ДМП-автомата

        Args:
            transitions: словарь переходов вида {(state, input_char, stack_top): (next_state, stack_operation)}
            initial_state: начальное состояние
            initial_stack_symbol: начальный символ магазина
            final_states: множество конечных состояний
        """
        self.transitions = transitions
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol
        self.final_states = final_states

    def process_string(self, input_string):
        """
        Обработка входной цепочки

        Returns:
            tuple: (принята ли цепочка, причина отказа если не принята, история состояний)
        """
        # Текущее состояние и стек
        current_state = self.initial_state
        stack = [self.initial_stack_symbol]

        # История для отладки
        history = [(current_state, stack.copy(), 'Начало')]

        # Обработка каждого символа входной цепочки
        for i, char in enumerate(input_string):
            # Получаем вершину стека
            stack_top = stack[-1] if stack else None

            # Ищем переход для текущего состояния, входного символа и вершины стека
            transition_key = (current_state, char, stack_top)

            if transition_key in self.transitions:
                next_state, stack_operation = self.transitions[transition_key]

                # Выполняем операцию со стеком
                if stack_operation == 'pop':
                    if stack:  # Проверяем, что стек не пуст
                        stack.pop()
                    else:
                        return False, f"Ошибка: попытка извлечения из пустого стека на позиции {i}", history
                elif stack_operation.startswith('push:'):
                    # Добавляем символы в стек (в обратном порядке, так как стек LIFO)
                    symbols_to_push = list(stack_operation[5:])
                    stack.extend(reversed(symbols_to_push))
                elif stack_operation == 'none':
                    # Ничего не делаем со стеком
                    pass
                else:
                    return False, f"Неизвестная операция со стеком: {stack_operation}", history

                # Переходим в следующее состояние
                current_state = next_state
                history.append((current_state, stack.copy(), f"Обработан символ '{char}'"))

            else:
                # Нет подходящего перехода
                return False, f"Нет перехода для (состояние={current_state}, символ='{char}', стек={stack_top}) на позиции {i}", history

        # После обработки всех символов проверяем epsilon-переходы (переходы по пустому символу)
        changed = True
        while changed:
            changed = False
            stack_top = stack[-1] if stack else None
            epsilon_transition_key = (current_state, '', stack_top)

            if epsilon_transition_key in self.transitions:
                next_state, stack_operation = self.transitions[epsilon_transition_key]

                # Выполняем операцию со стеком
                if stack_operation == 'pop':
                    if stack:
                        stack.pop()
                    else:
                        return False, "Ошибка: попытка извлечения из пустого стека при epsilon-переходе", history
                elif stack_operation.startswith('push:'):
                    symbols_to_push = list(stack_operation[5:])
                    stack.extend(reversed(symbols_to_push))
                elif stack_operation == 'none':
                    pass

                current_state = next_state
                history.append((current_state, stack.copy(), "Epsilon-переход"))
                changed = True

        # Проверяем, находимся ли в конечном состоянии
        stack_top = stack[-1] if stack else None
        if current_state in self.final_states:
            return True, "Цепочка принята", history
        else:
            return False, f"Цепочка обработана, но автомат в неконечном состоянии: {current_state}", history


def read_input_from_file(filename):
    """Чтение входной цепочки из файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден")
        return None
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        return None


def print_transition_history(history):
    """Вывод истории переходов"""
    print("\nИстория переходов:")
    print("-" * 50)
    for i, (state, stack, description) in enumerate(history):
        stack_str = ''.join(stack) if stack else "ε"
        print(f"Шаг {i}: состояние={state}, стек={stack_str}, действие={description}")


def main():
    """
    Пример ДМП-автомата для языка L = {a^n b^n | n >= 0}
    """

    # Определяем функцию переходов
    transitions = {
        # Чтение 'a' и добавление в стек
        ('q0', 'a', 'Z'): ('q0', 'push:A'),
        ('q0', 'a', 'A'): ('q0', 'push:A'),

        # Чтение 'b' и извлечение из стека
        ('q0', 'b', 'A'): ('q1', 'pop'),
        ('q1', 'b', 'A'): ('q1', 'pop'),

        # Epsilon-переход в конечное состояние при пустом стеке
        ('q1', '', 'Z'): ('q2', 'none'),
    }

    # Создаем автомат
    dpda = DPDA(
        transitions=transitions,
        initial_state='q0',
        initial_stack_symbol='Z',
        final_states={'q2'}
    )

    # Читаем входную цепочку из файла
    input_string = read_input_from_file('input.txt')
    if input_string is None:
        # Если файл не найден, используем тестовые примеры
        print("Файл input.txt не найден. Использую тестовые примеры:")
        test_strings = ['aabb', 'ab', '', 'aaabbb', 'aab', 'abb', 'abc']

        for test_string in test_strings:
            print(f"\nПроверка цепочки: '{test_string}'")
            print("=" * 40)

            accepted, reason, history = dpda.process_string(test_string)

            if accepted:
                print("✓ Цепочка ПРИНЯТА")
            else:
                print(f"✗ Цепочка ОТВЕРГНУТА: {reason}")

            print_transition_history(history)

    else:
        # Обрабатываем цепочку из файла
        print(f"Проверка цепочки из файла: '{input_string}'")
        print("=" * 40)

        accepted, reason, history = dpda.process_string(input_string)

        if accepted:
            print("✓ Цепочка ПРИНЯТА")
        else:
            print(f"✗ Цепочка ОТВЕРГНУТА: {reason}")

        print_transition_history(history)


# Дополнительный пример: ДМП-автомат для языка правильных скобочных последовательностей
def bracket_dpda_example():
    """
    Пример ДМП-автомата для языка правильных скобочных последовательностей
    """
    print("\n" + "=" * 60)
    print("Пример 2: ДМП-автомат для скобочных последовательностей")
    print("=" * 60)

    transitions = {
        # Открывающая скобка - добавляем в стек
        ('q0', '(', 'Z'): ('q0', 'push:('),
        ('q0', '(', '('): ('q0', 'push:('),

        # Закрывающая скобка - извлекаем из стека
        ('q0', ')', '('): ('q0', 'pop'),

        # Epsilon-переход в конечное состояние при пустом стеке
        ('q0', '', 'Z'): ('q1', 'none'),
    }

    dpda = DPDA(
        transitions=transitions,
        initial_state='q0',
        initial_stack_symbol='Z',
        final_states={'q1'}
    )

    test_brackets = ['()', '(())', '()()', '((()))', '(()', ')(', '())', '']

    for test_string in test_brackets:
        print(f"\nПроверка цепочки: '{test_string}'")
        print("-" * 30)

        accepted, reason, history = dpda.process_string(test_string)

        if accepted:
            print("✓ Цепочка ПРИНЯТА")
        else:
            print(f"✗ Цепочка ОТВЕРГНУТА: {reason}")

        # Выводим только краткую историю для этого примера
        if history:
            final_state, final_stack, _ = history[-1]
            stack_str = ''.join(final_stack) if final_stack else "ε"
            print(f"Финальное состояние: {final_state}, стек: {stack_str}")


if __name__ == "__main__":
    main()
    bracket_dpda_example()