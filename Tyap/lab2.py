from typing import Set, Dict, List, Tuple, Union


class DFA:
    def __init__(self, states: Set[str], alphabet: Set[str],
                 transitions: Dict[Tuple[str, str], Union[str, Set[str]]],
                 start_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states
        self._is_deterministic = None

    def is_deterministic(self) -> bool:
        """Проверка, является ли автомат детерминированным"""
        if self._is_deterministic is not None:
            return self._is_deterministic

        for (state, symbol), target in self.transitions.items():
            if isinstance(target, set):
                print(f"Недетерминированный переход: из '{state}' по '{symbol}' -> {target}")
                self._is_deterministic = False
                return False

        transition_counts = {}
        for (state, symbol), target in self.transitions.items():
            key = (state, symbol)
            if key in transition_counts:
                print(f"Конфликт переходов: из '{state}' по '{symbol}' -> '{transition_counts[key]}' и '{target}'")
                self._is_deterministic = False
                return False
            transition_counts[key] = target

        for state in self.states:
            for symbol in self.alphabet:
                if (state, symbol) not in self.transitions:
                    print(f"Отсутствует переход: из '{state}' по '{symbol}'")
                    self._is_deterministic = False
                    return False

        self._is_deterministic = True
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
                    target = self.transitions.get((state, symbol))
                    if target:
                        if isinstance(target, set):
                            for next_state in target:
                                if next_state not in reachable:
                                    stack.append(next_state)
                        else:
                            if target not in reachable:
                                stack.append(target)

        new_states = reachable
        new_final_states = self.final_states & reachable
        new_transitions = {}
        for (state, symbol), target in self.transitions.items():
            if state in reachable:
                if isinstance(target, set):
                    reachable_targets = target & reachable
                    if reachable_targets:
                        new_transitions[(state, symbol)] = reachable_targets
                else:
                    if target in reachable:
                        new_transitions[(state, symbol)] = target

        return DFA(new_states, self.alphabet, new_transitions, self.start_state, new_final_states)

    def build_equivalence_classes(self) -> List[Set[str]]:
        """Шаг 2: Построить классы эквивалентности"""
        F = self.final_states
        Q_F = self.states - F

        R_prev = [F, Q_F]
        R_prev = [cls for cls in R_prev if len(cls) > 0]

        print(f"R(0) = {R_prev}")

        n = 0
        while True:
            n += 1
            R_current = []

            for current_class in R_prev:
                if len(current_class) == 1:
                    R_current.append(current_class)
                    continue

                subclasses = self._split_equivalence_class(current_class, R_prev)
                R_current.extend(subclasses)

            if self._are_partitions_equal(R_current, R_prev):
                break
            else:
                print(f"R({n}) = {R_current}")

            R_prev = R_current

        return R_current

    def _split_equivalence_class(self, eq_class: Set[str], partition: List[Set[str]]) -> List[Set[str]]:
        """Разбивает класс эквивалентности на подклассы"""
        behavior_map = {}

        for state in eq_class:
            behavior = []
            for symbol in sorted(self.alphabet):
                target = self.transitions.get((state, symbol))
                if target is None:
                    behavior.append(None)
                elif isinstance(target, set):
                    target_classes = set()
                    for t_state in target:
                        for i, cls in enumerate(partition):
                            if t_state in cls:
                                target_classes.add(i)
                                break
                    behavior.append(frozenset(target_classes))
                else:
                    target_class = None
                    for i, cls in enumerate(partition):
                        if target in cls:
                            target_class = i
                            break
                    behavior.append(target_class)

            behavior_tuple = tuple(behavior)

            if behavior_tuple not in behavior_map:
                behavior_map[behavior_tuple] = set()
            behavior_map[behavior_tuple].add(state)

        return list(behavior_map.values())

    def _are_partitions_equal(self, part1: List[Set[str]], part2: List[Set[str]]) -> bool:
        """Проверяет, равны ли два разбиения"""
        if len(part1) != len(part2):
            return False

        set1 = {frozenset(cls) for cls in part1}
        set2 = {frozenset(cls) for cls in part2}

        return set1 == set2

    def minimize(self) -> 'DFA':
        """Алгоритм минимизации автомата"""
        if not self.is_deterministic():
            raise ValueError("Автомат должен быть детерминированным для минимизации")

        reachable_dfa = self.remove_unreachable_states()
        print("После удаления недостижимых состояний:")
        print(f"Состояния: {reachable_dfa.states}")

        equivalence_classes = reachable_dfa.build_equivalence_classes()
        print(f"\nФинальные классы эквивалентности: {equivalence_classes}")

        return self._build_minimized_from_equivalence_classes(reachable_dfa, equivalence_classes)

    def _build_minimized_from_equivalence_classes(self, reachable_dfa: 'DFA',
                                                  equivalence_classes: List[Set[str]]) -> 'DFA':
        """Строит минимальный автомат из классов эквивалентности"""
        state_mapping = {}
        new_states = set()

        for i, eq_class in enumerate(equivalence_classes):
            new_state = f"q{i}"
            new_states.add(new_state)
            for old_state in eq_class:
                state_mapping[old_state] = new_state

        new_start_state = state_mapping[reachable_dfa.start_state]

        new_final_states = set()
        for final_state in reachable_dfa.final_states:
            new_final_states.add(state_mapping[final_state])

        new_transitions = {}
        for (old_state, symbol), old_target in reachable_dfa.transitions.items():
            new_state = state_mapping[old_state]
            if isinstance(old_target, set):
                new_targets = {state_mapping[t] for t in old_target}
                if len(new_targets) == 1:
                    new_transitions[(new_state, symbol)] = next(iter(new_targets))
                else:
                    new_transitions[(new_state, symbol)] = new_targets
            else:
                new_target = state_mapping[old_target]
                new_transitions[(new_state, symbol)] = new_target

        return DFA(new_states, self.alphabet, new_transitions, new_start_state, new_final_states)

    def __str__(self) -> str:
        result = "Конечный автомат:\n"
        result += f"Состояния: {sorted(self.states)}\n"
        result += f"Алфавит: {sorted(self.alphabet)}\n"
        result += f"Начальное состояние: {self.start_state}\n"
        result += f"Конечные состояния: {sorted(self.final_states)}\n"
        result += "Переходы:\n"
        for (state, symbol), target in sorted(self.transitions.items()):
            if isinstance(target, set):
                result += f"  δ({state}, {symbol}) = {sorted(target)}\n"
            else:
                result += f"  δ({state}, {symbol}) = {target}\n"
        return result


# ВХОДНОЙ АВТОМАТ - можно менять переходы как нужно
def process_automaton():
    """Обработка одного входного автомата"""

    # ВХОДНЫЕ ДАННЫЕ - МОЖНО ИЗМЕНЯТЬ
    states = {'q0', 'q1', 'q2', 'q3', 'q4', 'q5'}
    alphabet = {'0', '1'}

    # ПЕРЕХОДЫ - можно использовать как одно состояние, так и множество
    transitions = {
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

    # СОЗДАНИЕ И АНАЛИЗ АВТОМАТА
    automaton = DFA(states, alphabet, transitions, start_state, final_states)

    print(automaton)

    is_dfa = automaton.is_deterministic()
    print(f"Тип автомата: {'ДКА' if is_dfa else 'НКА'}")

    # МИНИМИЗАЦИЯ ТОЛЬКО ДЛЯ ДКА
    if is_dfa:
        print("\n------- МИНИМИЗАЦИЯ -------")
        try:
            minimized = automaton.minimize()
            print("Минимизированный автомат:")
            print(minimized)
        except Exception as e:
            print(f"Ошибка при минимизации: {e}")
    else:
        print("\nМинимизация не выполняется: автомат не является ДКА")


if __name__ == "__main__":
    process_automaton()