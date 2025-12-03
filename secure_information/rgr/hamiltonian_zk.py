import random
import hashlib
import json
from typing import List, Tuple, Set, Dict


class HamiltonianCycleZK:
    """
    Класс для реализации протокола доказательства с нулевым разглашением
    для задачи о гамильтоновом цикле
    """

    def __init__(self, graph_file: str, cycle_file: str = None):
        """
        Инициализация графа из файла

        Args:
            graph_file: файл с описанием графа
            cycle_file: файл с гамильтоновым циклом (опционально)
        """
        self.n = 0  # количество вершин
        self.m = 0  # количество ребер
        self.adjacency_list = {}  # список смежности
        self.vertices = set()  # множество вершин
        self.hamiltonian_cycle = []  # гамильтонов цикл

        if graph_file:
            self.load_graph(graph_file)

        if cycle_file:
            self.load_hamiltonian_cycle(cycle_file)

    def load_graph(self, filename: str):
        """
        Загрузка графа из файла

        Формат файла:
        - первая строка: n m (количество вершин и ребер)
        - последующие m строк: пары вершин (ребра)
        """
        try:
            with open(filename, 'r') as f:
                # Читаем первую строку
                first_line = f.readline().strip()
                self.n, self.m = map(int, first_line.split())

                # Инициализируем список смежности
                self.adjacency_list = {i: set() for i in range(1, self.n + 1)}
                self.vertices = set(range(1, self.n + 1))

                # Читаем ребра
                for _ in range(self.m):
                    line = f.readline().strip()
                    if line:
                        u, v = map(int, line.split())
                        self.adjacency_list[u].add(v)
                        self.adjacency_list[v].add(u)

            print(f"Граф загружен: {self.n} вершин, {self.m} ребер")

        except Exception as e:
            print(f"Ошибка при загрузке графа: {e}")

    def load_hamiltonian_cycle(self, filename: str):
        """
        Загрузка гамильтонова цикла из файла

        Формат: последовательность вершин, образующих цикл
        """
        try:
            with open(filename, 'r') as f:
                self.hamiltonian_cycle = list(map(int, f.readline().strip().split()))

            # Проверяем корректность цикла
            if self.verify_hamiltonian_cycle(self.hamiltonian_cycle):
                print("Гамильтонов цикл загружен и проверен")
            else:
                print("Предупреждение: загруженный цикл не является корректным гамильтоновым циклом")

        except Exception as e:
            print(f"Ошибка при загрузке цикла: {e}")

    def verify_hamiltonian_cycle(self, cycle: List[int]) -> bool:
        """
        Проверка, является ли данный цикл гамильтоновым

        Args:
            cycle: список вершин, образующих цикл

        Returns:
            True если цикл гамильтонов, иначе False
        """
        if len(cycle) != self.n + 1:
            print(f"Ошибка: длина цикла {len(cycle)} != {self.n + 1}")
            return False

        if cycle[0] != cycle[-1]:
            print(f"Ошибка: первая вершина {cycle[0]} != последней вершине {cycle[-1]}")
            return False

        visited = set()
        for i in range(len(cycle) - 1):
            u, v = cycle[i], cycle[i + 1]

            # Проверяем существование ребра
            if v not in self.adjacency_list[u]:
                print(f"Ошибка: ребро ({u}, {v}) не существует в графе")
                return False

            # Проверяем, что все вершины уникальны (кроме первой и последней)
            if i < len(cycle) - 1:
                if u in visited:
                    print(f"Ошибка: вершина {u} повторяется")
                    return False
                visited.add(u)

        if len(visited) != self.n:
            print(f"Ошибка: посещено {len(visited)} вершин из {self.n}")
            return False

        return True

    def generate_random_permutation(self) -> Dict[int, int]:
        """
        Генерация случайной перестановки вершин

        Returns:
            Словарь, отображающий исходные вершины в переставленные
        """
        vertices = list(self.vertices)
        shuffled = vertices.copy()
        random.shuffle(shuffled)
        return {original: permuted for original, permuted in zip(vertices, shuffled)}

    def permute_graph(self, permutation: Dict[int, int]) -> Dict[int, List[int]]:
        """
        Применение перестановки к графу

        Args:
            permutation: перестановка вершин

        Returns:
            Переставленный граф в виде списка смежности (со списками вместо множеств)
        """
        permuted_graph = {}

        for u in self.vertices:
            permuted_u = permutation[u]
            # Используем список вместо множества для JSON сериализации
            permuted_graph[permuted_u] = sorted([permutation[v] for v in self.adjacency_list[u]])

        return permuted_graph

    def permute_cycle(self, cycle: List[int], permutation: Dict[int, int]) -> List[int]:
        """
        Применение перестановки к гамильтонову циклу

        Args:
            cycle: исходный цикл
            permutation: перестановка вершин

        Returns:
            Переставленный цикл
        """
        return [permutation[v] for v in cycle]

    def commit(self, data: any) -> str:
        """
        Создание коммита (обязательства) для данных

        Args:
            data: данные для коммита

        Returns:
            Хеш-значение коммита
        """
        # Преобразуем данные в строку для хеширования
        if isinstance(data, dict):
            # Для словаря сортируем ключи и значения
            sorted_data = {str(k): sorted(v) if isinstance(v, list) else v for k, v in data.items()}
            data_str = json.dumps(sorted_data, sort_keys=True)
        else:
            data_str = json.dumps(data, sort_keys=True)

        return hashlib.sha256(data_str.encode()).hexdigest()

    def prover_round(self) -> Tuple[str, List[int], Dict[int, int]]:
        """
        Один раунд доказательства (сторона доказывающего)

        Returns:
            Кортеж (коммит, переставленный_цикл, перестановка)
        """
        # Генерируем случайную перестановку
        permutation = self.generate_random_permutation()

        # Переставляем граф и цикл
        permuted_graph = self.permute_graph(permutation)
        permuted_cycle = self.permute_cycle(self.hamiltonian_cycle, permutation)

        # Создаем коммит для переставленного графа
        commit_hash = self.commit(permuted_graph)

        return commit_hash, permuted_cycle, permutation

    def verifier_challenge(self) -> int:
        """
        Генерация вызова верификатора (0 или 1)

        Returns:
            Случайный вызов: 0 или 1
        """
        return random.randint(0, 1)

    def prover_response(self, challenge: int, permuted_cycle: List[int],
                        permutation: Dict[int, int]) -> any:
        """
        Ответ доказывающего на вызов верификатора

        Args:
            challenge: вызов верификатора (0 или 1)
            permuted_cycle: переставленный цикл
            permutation: перестановка вершин

        Returns:
            Ответ в зависимости от вызова
        """
        if challenge == 0:
            # Показать перестановку
            return permutation
        else:
            # Показать гамильтонов цикл в переставленном графе
            return permuted_cycle

    def verifier_verify(self, challenge: int, response: any,
                        commit_hash: str, permuted_graph: Dict[int, List[int]] = None) -> bool:
        """
        Проверка ответа верификатором

        Args:
            challenge: вызов (0 или 1)
            response: ответ доказывающего
            commit_hash: коммит от доказывающего
            permuted_graph: переставленный граф (для challenge=0)

        Returns:
            True если проверка пройдена, иначе False
        """
        if challenge == 0:
            # Проверяем, что перестановка корректно применяется к графу
            if permuted_graph is None:
                return False

            # Восстанавливаем граф из перестановки
            reconstructed_graph = self.permute_graph(response)

            # Проверяем совпадение с коммитом
            reconstructed_commit = self.commit(reconstructed_graph)

            if reconstructed_commit == commit_hash:
                print("✓ Перестановка верифицирована успешно")
                return True
            else:
                print("✗ Ошибка верификации перестановки")
                return False

        else:
            # Проверяем, что цикл является гамильтоновым в переставленном графе
            cycle = response

            # Создаем временный граф для проверки
            temp_graph = HamiltonianCycleZK(None, None)
            temp_graph.n = self.n
            temp_graph.m = self.m
            temp_graph.vertices = set(permuted_graph.keys())

            # Преобразуем обратно в формат со множествами для проверки
            temp_graph.adjacency_list = {}
            for vertex, neighbors in permuted_graph.items():
                temp_graph.adjacency_list[vertex] = set(neighbors)

            if temp_graph.verify_hamiltonian_cycle(cycle):
                print("✓ Гамильтонов цикл верифицирован успешно")
                return True
            else:
                print("✗ Ошибка верификации гамильтонова цикла")
                return False

    def run_protocol(self, rounds: int = 10) -> bool:
        """
        Запуск полного протокола доказательства

        Args:
            rounds: количество раундов

        Returns:
            True если все раунды пройдены успешно, иначе False
        """
        print(f"\n=== Запуск протокола доказательства с нулевым разглашением ===")
        print(f"Количество раундов: {rounds}")

        if not self.hamiltonian_cycle:
            print("Ошибка: гамильтонов цикл не задан")
            return False

        # Сохраняем переставленный граф для использования в проверке
        saved_permuted_graphs = []

        for round_num in range(1, rounds + 1):
            print(f"\n--- Раунд {round_num} ---")

            # Фаза 1: Доказывающий создает коммит
            commit_hash, permuted_cycle, permutation = self.prover_round()
            print(f"Доказывающий: создан коммит")

            # Сохраняем переставленный граф для последующей проверки
            permuted_graph = self.permute_graph(permutation)
            saved_permuted_graphs.append(permuted_graph)

            # Фаза 2: Верификатор делает вызов
            challenge = self.verifier_challenge()
            challenge_text = "показать перестановку" if challenge == 0 else "показать гамильтонов цикл"
            print(f"Верификатор: вызов = {challenge} ({challenge_text})")

            # Фаза 3: Доказывающий отвечает
            response = self.prover_response(challenge, permuted_cycle, permutation)
            print(f"Доказывающий: отправлен ответ")

            # Фаза 4: Верификатор проверяет
            verified = self.verifier_verify(
                challenge, response, commit_hash, saved_permuted_graphs[-1]
            )

            if verified:
                print(f"✓ Раунд {round_num} пройден успешно")
            else:
                print(f"✗ Раунд {round_num} провален")
                return False

        print(f"\n=== Все {rounds} раундов пройдены успешно! ===")
        print("Верификатор убежден, что доказывающий знает гамильтонов цикл")
        return True


def generate_sample_graph(filename: str, n: int = 6):
    """
    Генерация примера графа с гамильтоновым циклом

    Args:
        filename: имя файла для сохранения
        n: количество вершин
    """
    # Создаем цикл (гамильтонов)
    edges = []
    for i in range(1, n):
        edges.append((i, i + 1))
    edges.append((n, 1))  # Замыкаем цикл

    # Добавляем несколько случайных ребер для сложности
    extra_edges = 0
    max_extra = n // 2
    attempts = 0
    while extra_edges < max_extra and attempts < 100:
        u = random.randint(1, n)
        v = random.randint(1, n)
        if u != v and (u, v) not in edges and (v, u) not in edges:
            edges.append((u, v))
            extra_edges += 1
        attempts += 1

    # Записываем в файл
    with open(filename, 'w') as f:
        f.write(f"{n} {len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")

    print(f"Пример графа сохранен в {filename} (вершин: {n}, ребер: {len(edges)})")


def generate_sample_cycle(filename: str, n: int = 6):
    """
    Генерация примера гамильтонова цикла

    Args:
        filename: имя файла для сохранения
        n: количество вершин
    """
    # Простой цикл: 1-2-3-...-n-1
    cycle = list(range(1, n + 1))
    cycle.append(1)  # Замыкаем цикл

    with open(filename, 'w') as f:
        f.write(" ".join(map(str, cycle)) + "\n")

    print(f"Пример цикла сохранен в {filename}")


def main():
    """
    Основная функция демонстрации работы протокола
    """
    print("Демонстрация протокола доказательства с нулевым разглашением")
    print("для задачи о гамильтоновом цикле")
    print("=" * 60)

    # Генерируем примеры файлов
    graph_file = "graph.txt"
    cycle_file = "cycle.txt"

    generate_sample_graph(graph_file, 6)
    generate_sample_cycle(cycle_file, 6)

    # Инициализируем протокол
    zk_protocol = HamiltonianCycleZK(graph_file, cycle_file)

    # Запускаем протокол
    success = zk_protocol.run_protocol(rounds=5)

    if success:
        print("\n🎉 Протокол завершен успешно!")
        print("Доказывающий убедил верификатора в знании гамильтонова цикла,")
        print("не раскрыв при этом сам цикл.")
    else:
        print("\n❌ Протокол провален!")
        print("Верификатор не убежден в знании доказывающим гамильтонова цикла.")


if __name__ == "__main__":
    main()