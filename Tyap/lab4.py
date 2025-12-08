class ShuntingYardParser:
    def __init__(self):
        # Этап 1: КС-грамматика и СУ-схема
        self.grammar = {
            'E': [['E', '+', 'T'], ['E', '-', 'T'], ['T']],
            'T': [['T', '*', 'F'], ['T', '/', 'F'], ['F']],
            'F': [['(', 'E', ')'], ['num']]
        }

        # СУ-схема для перевода в ОПЗ
        self.translation_scheme = {
            ('E', 'E + T'): 'E.translation T.translation +',
            ('E', 'E - T'): 'E.translation T.translation -',
            ('E', 'T'): 'T.translation',
            ('T', 'T * F'): 'T.translation F.translation *',
            ('T', 'T / F'): 'T.translation F.translation /',
            ('T', 'F'): 'F.translation',
            ('F', '( E )'): 'E.translation',
            ('F', 'num'): 'num'
        }

        # Этап 2: МП-преобразователь
        # Множества состояний
        self.states = {'q0', 'q1', 'q2', 'q3', 'q4', 'qf'}
        self.current_state = 'q0'

        # Алфавиты
        self.input_alphabet = {'num', '+', '-', '*', '/', '(', ')', '$'}
        self.stack_alphabet = {'E', 'T', 'F', '+', '-', '*', '/', '(', ')', 'num', '$', 'ε'}
        self.output_alphabet = {'num', '+', '-', '*', '/', ' '}

        # Функция переходов (состояние, входной символ, вершина стека) -> (новое состояние, действия со стеком, вывод)
        self.transitions = {
            # Начальные переходы
            ('q0', 'num', 'ε'): ('q1', 'push num', 'output num'),
            ('q0', '(', 'ε'): ('q1', 'push (', ''),

            # Обработка чисел
            ('q1', 'ε', 'num'): ('q2', 'pop', ''),

            # Обработка операторов и скобок
            ('q2', '+', 'ε'): ('q1', 'push +', ''),
            ('q2', '-', 'ε'): ('q1', 'push -', ''),
            ('q2', '*', 'ε'): ('q1', 'push *', ''),
            ('q2', '/', 'ε'): ('q1', 'push /', ''),
            ('q2', ')', 'ε'): ('q1', 'push )', ''),
            ('q2', '$', 'ε'): ('qf', '', ''),

            # Применение операторов
            ('q1', 'ε', '+'): ('q2', 'pop', 'output +'),
            ('q1', 'ε', '-'): ('q2', 'pop', 'output -'),
            ('q1', 'ε', '*'): ('q2', 'pop', 'output *'),
            ('q1', 'ε', '/'): ('q2', 'pop', 'output /'),

            # Обработка скобок
            ('q1', 'ε', '('): ('q2', 'pop', ''),
            ('q1', 'ε', ')'): ('q2', 'pop', ''),

            # Переходы для приоритетов операторов
            ('q2', 'ε', 'T'): ('q2', 'pop', ''),
            ('q2', 'ε', 'F'): ('q2', 'pop', ''),
            ('q2', 'ε', 'E'): ('q2', 'pop', ''),
        }

        # Приоритеты операторов
        self.precedence = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2,
            '(': 0,
            ')': 0
        }

        self.stack = []
        self.output = []
        self.position = 0
        self.input_string = ""

    def print_grammar_and_scheme(self):
        """Вывод КС-грамматики и СУ-схемы"""
        print("=" * 60)
        print("ЭТАП 1: КС-ГРАММАТИКА И СХЕМА СУ-ПЕРЕВОДА")
        print("=" * 60)

        print("\nКС-грамматика для арифметических выражений:")
        print("E -> E + T | E - T | T")
        print("T -> T * F | T / F | F")
        print("F -> ( E ) | num")

        print("\nСУ-схема для перевода в ОПЗ:")
        print("E -> E + T    { print(E.translation, T.translation, '+') }")
        print("E -> E - T    { print(E.translation, T.translation, '-') }")
        print("E -> T        { print(T.translation) }")
        print("T -> T * F    { print(T.translation, F.translation, '*') }")
        print("T -> T / F    { print(T.translation, F.translation, '/') }")
        print("T -> F        { print(F.translation) }")
        print("F -> ( E )    { print(E.translation) }")
        print("F -> num      { print(num) }")
        print("=" * 60)

    def tokenize(self, expression):
        """Разбиваем выражение на токены"""
        tokens = []
        current_number = ""

        for char in expression:
            if char.isdigit():
                current_number += char
            else:
                if current_number:
                    tokens.append(('num', current_number))
                    current_number = ""

                if char in '+-*/()':
                    tokens.append((char, char))
                elif char != ' ':
                    raise ValueError(f"Недопустимый символ: {char}")

        if current_number:
            tokens.append(('num', current_number))

        tokens.append(('$', '$'))  # Маркер конца
        return tokens

    def get_next_token(self):
        """Получение следующего токена"""
        if self.position < len(self.tokens):
            token = self.tokens[self.position]
            self.position += 1
            return token
        return ('$', '$')

    def process_transition(self, state, input_token, stack_top):
        """Обработка одного перехода МП-преобразователя"""
        # Поиск подходящего перехода
        transition_key = None

        # Пробуем точное совпадение
        if (state, input_token, stack_top) in self.transitions:
            transition_key = (state, input_token, stack_top)
        # Пробуем лямбда-переход
        elif (state, 'ε', stack_top) in self.transitions:
            transition_key = (state, 'ε', stack_top)
        # Пробуем переход по любому входному символу
        elif (state, 'any', stack_top) in self.transitions:
            transition_key = (state, 'any', stack_top)

        if transition_key:
            new_state, stack_action, output_action = self.transitions[transition_key]
            return new_state, stack_action, output_action

        return None, None, None

    def shunting_yard(self, expression):
        """Алгоритм сортировочной станции (Shunting Yard)"""
        output = []
        operators = []

        tokens = self.tokenize(expression)

        for token_type, token_value in tokens:
            if token_type == 'num':
                output.append(token_value)
            elif token_type in '+-*/':
                while (operators and operators[-1] != '(' and
                       self.precedence.get(operators[-1], 0) >= self.precedence.get(token_type, 0)):
                    output.append(operators.pop())
                operators.append(token_type)
            elif token_type == '(':
                operators.append(token_type)
            elif token_type == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                if operators and operators[-1] == '(':
                    operators.pop()

        while operators:
            output.append(operators.pop())

        return ' '.join(output)

    def simulate_mp_transducer(self, expression):
        """Имитация работы МП-преобразователя"""
        print("\n" + "=" * 60)
        print("ЭТАП 3: РАБОТА МП-ПРЕОБРАЗОВАТЕЛЯ")
        print("=" * 60)

        self.tokens = self.tokenize(expression)
        self.position = 0
        self.stack = ['$']  # Начальный маркер стека
        self.output = []
        self.current_state = 'q0'

        print(f"\nВходное выражение: {expression}")
        print("\nШаги работы МП-преобразователя:")
        print("-" * 60)
        print(f"{'Шаг':<5} {'Состояние':<10} {'Вход':<10} {'Стек':<20} {'Выход':<20}")
        print("-" * 60)

        step = 1
        token_index = 0

        while self.current_state != 'qf' and token_index <= len(self.tokens):
            # Получаем текущий входной символ
            if token_index < len(self.tokens):
                input_token, input_value = self.tokens[token_index]
            else:
                input_token, input_value = '$', '$'

            # Получаем вершину стека
            stack_top = self.stack[-1] if self.stack else 'ε'

            # Пробуем обработать текущий входной символ
            new_state, stack_action, output_action = self.process_transition(
                self.current_state, input_token, stack_top
            )

            # Если не нашли переход, пробуем лямбда-переход
            if not new_state:
                new_state, stack_action, output_action = self.process_transition(
                    self.current_state, 'ε', stack_top
                )

            if new_state:
                # Выполняем действие со стеком
                if stack_action:
                    if stack_action.startswith('push'):
                        _, symbol = stack_action.split()
                        self.stack.append(symbol)
                    elif stack_action == 'pop':
                        if self.stack:
                            self.stack.pop()

                # Выполняем вывод
                if output_action:
                    if output_action.startswith('output'):
                        _, symbol = output_action.split()
                        if symbol == 'num':
                            # Находим последнее число в токенах
                            for i in range(token_index - 1, -1, -1):
                                if i < len(self.tokens) and self.tokens[i][0] == 'num':
                                    self.output.append(self.tokens[i][1])
                                    break
                        else:
                            self.output.append(symbol)

                # Выводим состояние
                print(f"{step:<5} {self.current_state:<10} {input_value:<10} "
                      f"{''.join(self.stack):<20} {' '.join(self.output):<20}")

                # Обновляем состояние
                self.current_state = new_state

                # Если использовали входной символ, переходим к следующему
                if input_token != 'ε' and new_state != self.current_state:
                    token_index += 1

                step += 1
            else:
                # Если нет переходов, пробуем применить операторы из стека
                if stack_top in '+-*/' and token_index < len(self.tokens):
                    next_token = self.tokens[token_index][0] if token_index < len(self.tokens) else '$'
                    if (self.precedence.get(stack_top, 0) >= self.precedence.get(next_token, 0) and
                            next_token != '('):
                        # Выталкиваем оператор из стека
                        self.stack.pop()
                        self.output.append(stack_top)
                        print(f"{step:<5} {self.current_state:<10} {'ε':<10} "
                              f"{''.join(self.stack):<20} {' '.join(self.output):<20}")
                        step += 1
                        continue

                # Если все еще нет переходов, это ошибка
                # Давайте добавим отладочную информацию
                print(f"\nОтладочная информация:")
                print(f"Состояние: {self.current_state}")
                print(f"Входной символ: {input_token} ({input_value})")
                print(f"Вершина стека: {stack_top}")
                print(f"Текущий стек: {self.stack}")
                print(f"Текущие токены: {self.tokens}")
                print(f"Текущая позиция: {token_index}/{len(self.tokens)}")

                # Попробуем обработать скобки
                if input_token == '(' and self.current_state == 'q0':
                    # Добавляем открывающую скобку в стек
                    self.stack.append('(')
                    self.current_state = 'q1'
                    token_index += 1
                    print(f"{step:<5} {self.current_state:<10} {input_value:<10} "
                          f"{''.join(self.stack):<20} {' '.join(self.output):<20}")
                    step += 1
                    continue
                elif input_token == ')' and self.current_state == 'q2':
                    # Обрабатываем закрывающую скобку
                    self.stack.pop()  # Убираем '(' из стека
                    self.current_state = 'q1'
                    token_index += 1
                    print(f"{step:<5} {self.current_state:<10} {input_value:<10} "
                          f"{''.join(self.stack):<20} {' '.join(self.output):<20}")
                    step += 1
                    continue

                raise ValueError(f"Нет перехода: состояние={self.current_state}, "
                                 f"вход={input_token}, стек={stack_top}")

        print("-" * 60)
        result = ' '.join(self.output)
        print(f"\nРезультат ОПЗ: {result}")
        return result

    def validate_expression(self, expression):
        """Проверка корректности выражения"""
        # Проверка на пустую строку
        if not expression.strip():
            raise ValueError("Выражение не может быть пустым")

        # Проверка баланса скобок
        balance = 0
        for char in expression:
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
                if balance < 0:
                    raise ValueError("Несбалансированные скобки")

        if balance != 0:
            raise ValueError("Несбалансированные скобки")

        # Проверка на два оператора подряд
        tokens = self.tokenize(expression)
        prev_token = None
        for token_type, _ in tokens:
            if token_type in '+-*/' and prev_token in '+-*/':
                raise ValueError("Два оператора подряд")
            prev_token = token_type

        return True

    def process_expression(self, expression):
        """Обработка выражения с проверкой ошибок"""
        try:
            # Этап 1: Выводим грамматику и схему
            self.print_grammar_and_scheme()

            # Проверяем выражение
            self.validate_expression(expression)

            # Этап 2 и 3: Имитация МП-преобразователя
            result_mp = self.simulate_mp_transducer(expression)

            # Для сравнения: результат алгоритма Shunting Yard
            result_sy = self.shunting_yard(expression)

            print("\n" + "=" * 60)
            print("РЕЗУЛЬТАТЫ:")
            print("=" * 60)
            print(f"Входное выражение:    {expression}")
            print(f"ОПЗ (МП-преобразователь): {result_mp}")
            print(f"ОПЗ (Shunting Yard):      {result_sy}")

            if result_mp.replace(' ', '') == result_sy.replace(' ', ''):
                print("✓ Результаты совпадают!")
            else:
                print("⚠ Результаты различаются!")

            return result_mp

        except ValueError as e:
            print(f"\n❌ Ошибка: {e}")
            return None
        except Exception as e:
            print(f"\n❌ Неожиданная ошибка: {e}")
            return None


def main():
    """Основная функция программы"""
    parser = ShuntingYardParser()

    print("ПЕРЕВОДЧИК АРИФМЕТИЧЕСКИХ ВЫРАЖЕНИЙ В ОБРАТНУЮ ПОЛЬСКУЮ ЗАПИСЬ")
    print("=" * 60)

    # Тестируем конкретное выражение
    test_expression = "(5 + 3) * 2"
    print(f"\nТестирование выражения: {test_expression}")
    result = parser.process_expression(test_expression)

    # Интерактивный режим
    print("\n" + "=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ")
    print("=" * 60)

    while True:
        try:
            print("\nВведите арифметическое выражение (или 'q' для выхода):")
            user_input = input("> ").strip()

            if user_input.lower() == 'q':
                print("Выход из программы.")
                break

            if not user_input:
                print("Введите выражение!")
                continue

            result = parser.process_expression(user_input)

        except KeyboardInterrupt:
            print("\n\nПрограмма прервана.")
            break
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()