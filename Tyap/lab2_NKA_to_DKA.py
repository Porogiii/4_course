from typing import Set, Dict, List, Tuple, FrozenSet
from collections import deque


class DFA:
    def __init__(self, states: Set[str], alphabet: Set[str],
                 transitions: Dict[Tuple[str, str], str],
                 start_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def is_deterministic(self) -> bool:
        """Проверка, является ли автомат детерминированным"""
        for state in self.states:
            for symbol in self.alphabet:
                transitions_count = sum(1 for (s, sym) in self.transitions
                                        if s == state and sym == symbol)
                if transitions_count != 1:
                    return False
        return True

    def remove_unreachable_states(self) -> 'DFA':
        """Шаг 1: Исключить все недостижимые состояния"""
        reachable = set()
        stack = [self.start_state]

        while stack:
            state = stack.pop()
            if state not in reachable:
                reachable.add(state)
                for symbol in self.alphabet:
                    next_state = self.transitions.get((state, symbol))
                    if next_state and next_state not in reachable:
                        stack.append(next_state)

        # Строим новый автомат только с достижимыми состояниями
        new_states = reachable
        new_final_states = self.final_states & reachable
        new_transitions = {}
        for (state, symbol), target in self.transitions.items():
            if state in reachable and target in reachable:
                new_transitions[(state, symbol)] = target

        return DFA(new_states, self.alphabet, new_transitions, self.start_state, new_final_states)

    def build_equivalence_classes(self) -> List[Set[str]]:
        """Шаг 2: Построить классы эквивалентности"""
        # Шаг 1 алгоритма: n = 0, R(0) = {F, Q\F}
        F = self.final_states
        Q_F = self.states - F

        R_prev = [F, Q_F]
        R_prev = [cls for cls in R_prev if len(cls) > 0]  # Убираем пустые классы

        print(f"R(0) = {R_prev}")

        n = 0
        while True:
            n += 1
            R_current = []

            # Шаг 2: Строим R(n) на основании R(n-1)
            for current_class in R_prev:
                if len(current_class) == 1:
                    R_current.append(current_class)
                    continue

                # Разбиваем класс на подклассы
                subclasses = self._split_equivalence_class(current_class, R_prev)
                R_current.extend(subclasses)

            print(f"R({n}) = {R_current}")

            # Шаг 3: Если R(n) = R(n-1), то работа заканчивается
            if self._are_partitions_equal(R_current, R_prev):
                break

            R_prev = R_current

        return R_current

    def _split_equivalence_class(self, eq_class: Set[str], partition: List[Set[str]]) -> List[Set[str]]:
        """Разбивает класс эквивалентности на подклассы"""
        behavior_map = {}

        for state in eq_class:
            # Определяем поведение состояния - в какие классы ведут переходы
            behavior = []
            for symbol in sorted(self.alphabet):
                target = self.transitions.get((state, symbol))
                # Находим класс, содержащий целевое состояние
                target_class = None
                for cls in partition:
                    if target in cls:
                        target_class = cls
                        break
                behavior.append(frozenset(target_class) if target_class else None)

            behavior_tuple = tuple(behavior)

            if behavior_tuple not in behavior_map:
                behavior_map[behavior_tuple] = set()
            behavior_map[behavior_tuple].add(state)

        return list(behavior_map.values())

    def _are_partitions_equal(self, part1: List[Set[str]], part2: List[Set[str]]) -> bool:
        """Проверяет, равны ли два разбиения"""
        if len(part1) != len(part2):
            return False

        # Преобразуем в множества frozenset для сравнения
        set1 = {frozenset(cls) for cls in part1}
        set2 = {frozenset(cls) for cls in part2}

        return set1 == set2

    def minimize(self) -> 'DFA':
        """Алгоритм минимизации автомата"""
        if not self.is_deterministic():
            raise ValueError("Автомат должен быть детерминированным для минимизации")

        # Шаг 1: Исключить недостижимые состояния
        reachable_dfa = self.remove_unreachable_states()
        print("После удаления недостижимых состояний:")
        print(f"Состояния: {reachable_dfa.states}")

        # Шаг 2: Построить классы эквивалентности
        equivalence_classes = reachable_dfa.build_equivalence_classes()
        print(f"\nФинальные классы эквивалентности: {equivalence_classes}")

        # Шаг 3: Каждый класс становится состоянием нового автомата
        # Шаг 4: Строим функцию переходов
        return self._build_minimized_from_equivalence_classes(reachable_dfa, equivalence_classes)

    def _build_minimized_from_equivalence_classes(self, reachable_dfa: 'DFA',
                                                  equivalence_classes: List[Set[str]]) -> 'DFA':
        """Строит минимальный автомат из классов эквивалентности"""
        # Создаем отображение старых состояний в новые
        state_mapping = {}
        new_states = set()

        for i, eq_class in enumerate(equivalence_classes):
            new_state = f"q{i}"
            new_states.add(new_state)
            for old_state in eq_class:
                state_mapping[old_state] = new_state

        # Новое начальное состояние
        new_start_state = state_mapping[reachable_dfa.start_state]

        # Новые конечные состояния
        new_final_states = set()
        for final_state in reachable_dfa.final_states:
            new_final_states.add(state_mapping[final_state])

        # Новая функция переходов на основе reachable_dfa
        new_transitions = {}
        for (old_state, symbol), old_target in reachable_dfa.transitions.items():
            new_state = state_mapping[old_state]
            new_target = state_mapping[old_target]
            new_transitions[(new_state, symbol)] = new_target

        return DFA(new_states, self.alphabet, new_transitions, new_start_state, new_final_states)

    def __str__(self) -> str:
        result = "Детерминированный конечный автомат (ДКА):\n"
        result += f"Состояния: {sorted(self.states)}\n"
        result += f"Алфавит: {sorted(self.alphabet)}\n"
        result += f"Начальное состояние: {self.start_state}\n"
        result += f"Конечные состояния: {sorted(self.final_states)}\n"
        result += "Переходы:\n"
        for (state, symbol), target in sorted(self.transitions.items()):
            result += f"  δ({state}, {symbol}) = {target}\n"
        return result


class NFA:
    """Недетерминированный конечный автомат"""

    def __init__(self, states: Set[str], alphabet: Set[str],
                 transitions: Dict[Tuple[str, str], Set[str]],
                 start_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states

    def to_dfa(self) -> DFA:
        """Преобразование НКА в ДКА алгоритмом подмножеств"""
        # Начинаем с epsilon-замыкания начального состояния
        start_set = self._epsilon_closure({self.start_state})
        dfa_start = self._set_to_state_name(start_set)

        dfa_states = set()
        dfa_final_states = set()
        dfa_transitions = {}

        queue = deque([start_set])
        processed = set()

        while queue:
            current_set = queue.popleft()
            current_state_name = self._set_to_state_name(current_set)

            if frozenset(current_set) in processed:
                continue

            processed.add(frozenset(current_set))
            dfa_states.add(current_state_name)

            # Проверяем, является ли состояние конечным
            if any(state in self.final_states for state in current_set):
                dfa_final_states.add(current_state_name)

            # Строим переходы для каждого символа
            for symbol in self.alphabet:
                if symbol == 'ε':  # Пропускаем epsilon-переходы
                    continue

                next_set = set()
                for state in current_set:
                    # Получаем все переходы из текущего состояния по символу
                    transitions_from_state = set()
                    for (s, sym), targets in self.transitions.items():
                        if s == state and sym == symbol:
                            transitions_from_state.update(targets)

                    # Добавляем epsilon-замыкание для каждого достигнутого состояния
                    for target in transitions_from_state:
                        next_set.update(self._epsilon_closure({target}))

                if next_set:
                    next_state_name = self._set_to_state_name(next_set)
                    dfa_transitions[(current_state_name, symbol)] = next_state_name

                    if frozenset(next_set) not in processed:
                        queue.append(next_set)

        return DFA(dfa_states, self.alphabet, dfa_transitions, dfa_start, dfa_final_states)

    def _epsilon_closure(self, states: Set[str]) -> Set[str]:
        """Вычисляет epsilon-замыкание множества состояний"""
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            # Ищем все epsilon-переходы из этого состояния
            epsilon_targets = set()
            for (s, sym), targets in self.transitions.items():
                if s == state and sym == 'ε':
                    epsilon_targets.update(targets)

            for target in epsilon_targets:
                if target not in closure:
                    closure.add(target)
                    stack.append(target)

        return closure

    def _set_to_state_name(self, state_set: Set[str]) -> str:
        """Преобразует множество состояний в имя состояния ДКА"""
        if not state_set:
            return "∅"
        return "{" + ",".join(sorted(state_set)) + "}"


def check_and_convert_to_dfa(automaton) -> DFA:
    """Проверяет автомат на детерминированность и преобразует в ДКА при необходимости"""
    if isinstance(automaton, DFA):
        if automaton.is_deterministic():
            print("Автомат является детерминированным.")
            return automaton
        else:
            print("Автомат не является детерминированным. Преобразуем в ДКА...")
            # Если DFA не детерминированный, преобразуем его в NFA и затем в DFA
            nfa_transitions = {}
            for (state, symbol), target in automaton.transitions.items():
                key = (state, symbol)
                if key not in nfa_transitions:
                    nfa_transitions[key] = set()
                nfa_transitions[key].add(target)

            nfa = NFA(automaton.states, automaton.alphabet, nfa_transitions,
                      automaton.start_state, automaton.final_states)
            return nfa.to_dfa()

    elif isinstance(automaton, NFA):
        print("Автомат является недетерминированным. Преобразуем в ДКА...")
        return automaton.to_dfa()

    else:
        raise ValueError("Неизвестный тип автомата")


def minimize_automaton(automaton) -> DFA:
    """Проверяет и преобразует автомат в ДКА (если нужно) и минимизирует его"""
    print("=== ПРОВЕРКА АВТОМАТА ===")

    # Преобразуем в ДКА если нужно
    dfa = check_and_convert_to_dfa(automaton)

    print("\nДетерминированный автомат:")
    print(dfa)

    # Минимизируем ДКА
    print("\n=== МИНИМИЗАЦИЯ ДКА ===")
    minimized_dfa = dfa.minimize()

    return minimized_dfa


# Примеры использования
def create_example_nfa():
    """Создает пример недетерминированного автомата"""
    states = {'q0', 'q1', 'q2'}
    alphabet = {'0', '1'}

    transitions = {
        ('q0', '0'): {'q1'},
        ('q0', '1'): {'q0', 'q1'},
        ('q1', '1'): {'q2'},
    }

    start_state = 'q0'
    final_states = {'q2'}

    return NFA(states, alphabet, transitions, start_state, final_states)


def create_lecture_example():
    """Создает автомат из примера с лекции"""
    states = {'q0', 'q1', 'q2', 'q3', 'q4', 'q5'}
    alphabet = {'0', '1'}

    transitions = {
        ('q0', '0'): 'q1',
        ('q0', '0'): 'q1',
        ('q0', '1'): 'q2',
        ('q1', '0'): 'q4',
        ('q1', '1'): 'q2',
        ('q2', '0'): 'q3',
        ('q2', '1'): 'q0',
        ('q3', '0'): 'q5',
        ('q3', '1'): 'q2',
        ('q4', '0'): 'q5',
        ('q4', '1'): 'q5',
        ('q5', '0'): 'q4',
        ('q5', '1'): 'q4'
    }

    start_state = 'q0'
    final_states = {'q4', 'q5'}

    return DFA(states, alphabet, transitions, start_state, final_states)


def test_with_nfa():
    """Тестирование с недетерминированным автоматом"""
    print("=== ТЕСТ С НЕДЕТЕРМИНИРОВАННЫМ АВТОМАТОМ ===\n")

    nfa = create_example_nfa()
    minimized = minimize_automaton(nfa)

    print("\nФинальный минимальный ДКА:")
    print(minimized)


def test_with_dfa():
    """Тестирование с детерминированным автоматом"""
    print("=== ТЕСТ С ДЕТЕРМИНИРОВАННЫМ АВТОМАТОМ ===\n")

    dfa = create_lecture_example()
    minimized = minimize_automaton(dfa)

    print("\nФинальный минимальный ДКА:")
    print(minimized)


if __name__ == "__main__":
    # Тестируем с разными типами автоматов
    test_with_dfa()
    print("\n" + "=" * 50 + "\n")
    test_with_nfa()