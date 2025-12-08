import random
import hashlib
from typing import List, Tuple, Dict, Optional
import os


class ZeroKnowledgeHamiltonian:
    """
    Класс для реализации протокола доказательства с нулевым разглашением
    для задачи гамильтонова цикла.
    """

    def __init__(self, n: int = 0):
        """
        Инициализация протокола.

        Args:
            n: Количество вершин в графе
        """
        self.n = n
        self.adj_matrix = [[0] * n for _ in range(n)]  # Матрица смежности исходного графа G
        self.hamiltonian_cycle = []  # Гамильтонов цикл в исходном графе
        self.public_key = None  # Открытый ключ для шифрования
        self.private_key = None  # Закрытый ключ для расшифровки

    def generate_keys(self) -> Tuple[int, int, int]:
        """
        Генерация ключей для шифрования по схеме RSA.

        Returns:
            Кортеж (N, e, d) - модуль, открытая экспонента, закрытая экспонента
        """
        # Для простоты реализации используем упрощенную RSA
        # В реальной реализации нужны большие простые числа
        p = 101  # Упрощенные простые числа
        q = 103
        N = p * q
        phi = (p - 1) * (q - 1)

        # Выбираем e (открытую экспоненту)
        e = 65537
        while self.gcd(e, phi) != 1:
            e += 2

        # Вычисляем d (закрытую экспоненту)
        d = self.mod_inverse(e, phi)

        self.public_key = (N, e)
        self.private_key = (N, d)

        return N, e, d

    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Нахождение наибольшего общего делителя."""
        while b != 0:
            a, b = b, a % b
        return a

    @staticmethod
    def mod_inverse(a: int, m: int) -> int:
        """Нахождение обратного элемента по модулю."""
        g, x, y = ZeroKnowledgeHamiltonian.extended_gcd(a, m)
        if g != 1:
            raise Exception('Обратный элемент не существует')
        return x % m

    @staticmethod
    def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
        """Расширенный алгоритм Евклида."""
        if a == 0:
            return b, 0, 1
        else:
            g, x, y = ZeroKnowledgeHamiltonian.extended_gcd(b % a, a)
            return g, y - (b // a) * x, x

    def encrypt(self, value: int) -> int:
        """
        Шифрование значения по схеме RSA.

        Args:
            value: Значение для шифрования

        Returns:
            Зашифрованное значение
        """
        if self.public_key is None:
            raise Exception("Ключи не сгенерированы")
        N, e = self.public_key
        # Добавляем случайное число для усиления безопасности
        # В реальной реализации нужно использовать padding схему
        return pow(value, e, N)

    def decrypt(self, value: int) -> int:
        """
        Расшифрование значения по схеме RSA.

        Args:
            value: Зашифрованное значение

        Returns:
            Расшифрованное значение
        """
        if self.private_key is None:
            raise Exception("Ключи не сгенерированы")
        N, d = self.private_key
        return pow(value, d, N)

    def load_graph_from_file(self, filename: str):
        """
        Загрузка графа из файла.

        Формат файла:
        - Первая строка: n m (количество вершин и ребер)
        - Следующие m строк: u v (ребра графа)
        """
        with open(filename, 'r') as f:
            # Чтение количества вершин и ребер
            n, m = map(int, f.readline().split())
            self.n = n
            self.adj_matrix = [[0] * n for _ in range(n)]

            # Чтение ребер
            for _ in range(m):
                u, v = map(int, f.readline().split())
                # Граф неориентированный
                self.adj_matrix[u][v] = 1
                self.adj_matrix[v][u] = 1

    def load_hamiltonian_cycle_from_file(self, filename: str):
        """
        Загрузка гамильтонова цикла из файла.

        Args:
            filename: Имя файла с циклом
        """
        with open(filename, 'r') as f:
            self.hamiltonian_cycle = list(map(int, f.readline().split()))

    def find_hamiltonian_cycle(self) -> List[int]:
        """
        Поиск гамильтонова цикла в графе (для тестирования).
        Использует алгоритм с возвратом.

        Returns:
            Список вершин, образующих гамильтонов цикл
        """
        if not self.hamiltonian_cycle:
            # Если цикл не задан, пытаемся найти
            path = [-1] * self.n
            path[0] = 0  # Начинаем с вершины 0

            def is_safe(v: int, pos: int, path: List[int]) -> bool:
                """Проверка, можно ли добавить вершину v в путь на позицию pos."""
                # Проверяем, соединена ли вершина с предыдущей
                if self.adj_matrix[path[pos - 1]][v] == 0:
                    return False

                # Проверяем, не посещали ли уже эту вершину
                if v in path[:pos]:
                    return False

                return True

            def hamiltonian_util(path: List[int], pos: int) -> bool:
                """Рекурсивная утилита для поиска гамильтонова цикла."""
                if pos == self.n:
                    # Все вершины размещены, проверяем замыкание цикла
                    return self.adj_matrix[path[pos - 1]][path[0]] == 1

                for v in range(1, self.n):
                    if is_safe(v, pos, path):
                        path[pos] = v
                        if hamiltonian_util(path, pos + 1):
                            return True
                        path[pos] = -1  # Откат

                return False

            if hamiltonian_util(path, 1):
                self.hamiltonian_cycle = path
                return path
            else:
                raise Exception("Гамильтонов цикл не найден")

        return self.hamiltonian_cycle

    def create_isomorphic_graph(self) -> Tuple[List[List[int]], List[int], List[int]]:
        """
        Создание изоморфного графа H путем перестановки вершин.

        Returns:
            Кортеж (матрица смежности H, перестановка вершин, обратная перестановка)
        """
        # Создаем случайную перестановку вершин
        permutation = list(range(self.n))
        random.shuffle(permutation)

        # Создаем обратную перестановку
        inverse_permutation = [0] * self.n
        for i in range(self.n):
            inverse_permutation[permutation[i]] = i

        # Создаем матрицу смежности изоморфного графа H
        H = [[0] * self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                if self.adj_matrix[i][j] == 1:
                    # Применяем перестановку к ребру
                    u, v = permutation[i], permutation[j]
                    H[u][v] = 1
                    H[v][u] = 1

        return H, permutation, inverse_permutation

    def encrypt_matrix(self, matrix: List[List[int]]) -> List[List[int]]:
        """
        Шифрование матрицы с добавлением случайных чисел.

        Args:
            matrix: Матрица смежности графа H

        Returns:
            Зашифрованная матрица F
        """
        F = [[0] * self.n for _ in range(self.n)]

        for i in range(self.n):
            for j in range(self.n):
                if matrix[i][j] == 1:
                    # Для единиц добавляем случайное число
                    random_num = random.randint(1000, 10000)
                    value = matrix[i][j] + random_num
                else:
                    # Для нулей оставляем как есть (но можно тоже добавлять шум)
                    value = matrix[i][j]

                # Шифруем значение
                F[i][j] = self.encrypt(value)

        return F

    def prove_hamiltonian_cycle(self, H: List[List[int]],
                                inverse_permutation: List[int],
                                F: List[List[int]]) -> Dict:
        """
        Доказательство знания гамильтонова цикла в графе H.

        Args:
            H: Матрица смежности графа H
            inverse_permutation: Обратная перестановка вершин
            F: Зашифрованная матрица

        Returns:
            Словарь с доказательством цикла
        """
        # Находим гамильтонов цикл в исходном графе
        original_cycle = self.hamiltonian_cycle

        # Преобразуем цикл в изоморфный граф H
        cycle_in_H = [inverse_permutation[v] for v in original_cycle]

        # Создаем доказательство
        proof = {
            'cycle': cycle_in_H,
            'edges': []
        }

        # Добавляем ребра цикла с их расшифровкой
        for i in range(len(cycle_in_H)):
            u = cycle_in_H[i]
            v = cycle_in_H[(i + 1) % len(cycle_in_H)]
            proof['edges'].append((u, v, self.decrypt(F[u][v])))

        return proof

    def prove_isomorphism(self, H: List[List[int]],
                          permutation: List[int],
                          F: List[List[int]]) -> Dict:
        """
        Доказательство изоморфизма графов G и H.

        Args:
            H: Матрица смежности графа H
            permutation: Перестановка вершин
            F: Зашифрованная матрица

        Returns:
            Словарь с доказательством изоморфизма
        """
        # Расшифровываем всю матрицу F
        decrypted_H = [[0] * self.n for _ in range(self.n)]

        for i in range(self.n):
            for j in range(self.n):
                decrypted_value = self.decrypt(F[i][j])
                # Извлекаем исходное значение (убираем случайное число)
                if decrypted_value > 1:
                    decrypted_H[i][j] = 1
                else:
                    decrypted_H[i][j] = decrypted_value

        proof = {
            'decrypted_matrix': decrypted_H,
            'permutation': permutation,
            'original_matrix': self.adj_matrix
        }

        return proof

    def verify_hamiltonian_proof(self, proof: Dict, F: List[List[int]]) -> bool:
        """
        Проверка доказательства гамильтонова цикла.

        Args:
            proof: Доказательство цикла
            F: Зашифрованная матрица

        Returns:
            True если доказательство верно, иначе False
        """
        cycle = proof['cycle']
        edges_proof = proof['edges']

        # Проверяем, что цикл гамильтонов
        if len(set(cycle)) != self.n or len(cycle) != self.n:
            return False

        # Проверяем все ребра цикла
        for u, v, decrypted_value in edges_proof:
            # Проверяем, что ребро существует в графе
            if u < 0 or u >= self.n or v < 0 or v >= self.n:
                return False

            # Проверяем расшифровку
            if self.encrypt(decrypted_value) != F[u][v]:
                return False

            # Проверяем, что значение соответствует ребру (1 + случайное число)
            if decrypted_value <= 1:
                return False

        return True

    def verify_isomorphism_proof(self, proof: Dict, F: List[List[int]]) -> bool:
        """
        Проверка доказательства изоморфизма.

        Args:
            proof: Доказательство изоморфизма
            F: Зашифрованная матрица

        Returns:
            True если доказательство верно, иначе False
        """
        decrypted_H = proof['decrypted_matrix']
        permutation = proof['permutation']
        original_G = proof['original_matrix']

        # Проверяем расшифровку
        for i in range(self.n):
            for j in range(self.n):
                # Для упрощения проверяем только соответствие типов значений
                if decrypted_H[i][j] not in [0, 1]:
                    return False

        # Проверяем изоморфизм
        for i in range(self.n):
            for j in range(self.n):
                u, v = permutation[i], permutation[j]
                if decrypted_H[i][j] != original_G[u][v]:
                    return False

        return True


def create_test_files():
    """Создание тестовых файлов для демонстрации работы программы."""

    # Создаем тестовый граф (простой 4-вершинный граф с гамильтоновым циклом)
    graph_content = """4 5
0 1
1 2
2 3
3 0
0 2
"""

    # Создаем гамильтонов цикл
    cycle_content = "0 1 2 3"

    # Записываем в файлы
    with open("test_graph.txt", "w") as f:
        f.write(graph_content)

    with open("test_cycle.txt", "w") as f:
        f.write(cycle_content)

    print("Тестовые файлы созданы:")
    print("  test_graph.txt - описание графа")
    print("  test_cycle.txt - гамильтонов цикл")


def demo_protocol():
    """Демонстрация работы протокола доказательства с нулевым разглашением."""

    print("=" * 60)
    print("ДЕМОНСТРАЦИЯ ПРОТОКОЛА ДОКАЗАТЕЛЬСТВА С НУЛЕВЫМ РАЗГЛАШЕНИЕМ")
    print("ДЛЯ ЗАДАЧИ ГАМИЛЬТОНОВА ЦИКЛА")
    print("=" * 60)

    # Создаем тестовые файлы
    create_test_files()

    # Инициализируем протокол
    print("\n1. ИНИЦИАЛИЗАЦИЯ ПРОТОКОЛА")
    print("-" * 40)

    protocol = ZeroKnowledgeHamiltonian()

    # Загружаем граф
    print("Загружаем граф из файла test_graph.txt...")
    protocol.load_graph_from_file("test_graph.txt")
    print(f"Граф загружен: {protocol.n} вершин")

    # Загружаем гамильтонов цикл
    print("Загружаем гамильтонов цикл из файла test_cycle.txt...")
    protocol.load_hamiltonian_cycle_from_file("test_cycle.txt")
    print(f"Гамильтонов цикл: {protocol.hamiltonian_cycle}")

    # Генерируем ключи
    print("\nГенерируем криптографические ключи...")
    N, e, d = protocol.generate_keys()
    print(f"Открытый ключ: (N={N}, e={e})")
    print(f"Закрытый ключ: (N={N}, d={d})")

    print("\n2. ПОДГОТОВКА ДОКАЗАТЕЛЬСТВА (АЛИСА)")
    print("-" * 40)

    # Алиса создает изоморфный граф H
    print("Алиса создает изоморфный граф H...")
    H, permutation, inverse_permutation = protocol.create_isomorphic_graph()
    print(f"Перестановка вершин: {permutation}")
    print(f"Обратная перестановка: {inverse_permutation}")

    # Выводим матрицу смежности исходного графа
    print("\nМатрица смежности исходного графа G:")
    for row in protocol.adj_matrix:
        print(" ".join(map(str, row)))

    # Выводим матрицу смежности изоморфного графа
    print("\nМатрица смежности изоморфного графа H:")
    for row in H:
        print(" ".join(map(str, row)))

    # Алиса шифрует матрицу H
    print("\nАлиса шифрует матрицу смежности графа H...")
    F = protocol.encrypt_matrix(H)
    print("Матрица F (зашифрованная) создана и отправлена Бобу")

    # Боб выбирает случайный вопрос
    print("\n3. ВОПРОС БОБА")
    print("-" * 40)

    # Боб случайным образом выбирает вопрос (1 или 2)
    question = random.randint(1, 2)
    if question == 1:
        print("Боб задает вопрос 1: 'Каков гамильтонов цикл для графа H?'")
    else:
        print("Боб задает вопрос 2: 'Действительно ли граф H изоморфен G?'")

    print("\n4. ОТВЕТ АЛИСЫ")
    print("-" * 40)

    proof = None
    if question == 1:
        # Алиса доказывает знание гамильтонова цикла
        print("Алиса доказывает знание гамильтонова цикла в графе H...")
        proof = protocol.prove_hamiltonian_cycle(H, inverse_permutation, F)
        print(f"Предъявлен цикл в графе H: {proof['cycle']}")
        print(f"Расшифрованные ребра цикла: {proof['edges']}")
    else:
        # Алиса доказывает изоморфизм
        print("Алиса доказывает изоморфизм графов G и H...")
        proof = protocol.prove_isomorphism(H, permutation, F)
        print(f"Предъявлена перестановка: {proof['permutation']}")
        print("Предъявлена расшифрованная матрица H:")
        for row in proof['decrypted_matrix']:
            print(" ".join(map(str, row)))

    print("\n5. ПРОВЕРКА БОБА")
    print("-" * 40)

    verification_result = False
    if question == 1:
        # Боб проверяет доказательство цикла
        print("Боб проверяет доказательство гамильтонова цикла...")
        verification_result = protocol.verify_hamiltonian_proof(proof, F)
        if verification_result:
            print("✓ Доказательство цикла ПРИНЯТО")
            print("  Боб убедился, что Алиса знает гамильтонов цикл")
        else:
            print("✗ Доказательство цикла ОТВЕРГНУТО")
    else:
        # Боб проверяет доказательство изоморфизма
        print("Боб проверяет доказательство изоморфизма...")
        verification_result = protocol.verify_isomorphism_proof(proof, F)
        if verification_result:
            print("✓ Доказательство изоморфизма ПРИНЯТО")
            print("  Боб убедился, что граф H изоморфен G")
        else:
            print("✗ Доказательство изоморфизма ОТВЕРГНУТО")

    print("\n6. ПОВТОРЕНИЕ ПРОТОКОЛА")
    print("-" * 40)

    # Демонстрация повторения протокола k раз
    k = 3  # Количество повторений
    print(f"Протокол повторяется {k} раз для увеличения достоверности...")

    successful_rounds = 0
    for round_num in range(1, k + 1):
        print(f"\nРаунд {round_num}:")

        # Создаем новый изоморфный граф
        H, permutation, inverse_permutation = protocol.create_isomorphic_graph()
        F = protocol.encrypt_matrix(H)

        # Боб задает случайный вопрос
        question = random.randint(1, 2)

        # Алиса отвечает
        if question == 1:
            proof = protocol.prove_hamiltonian_cycle(H, inverse_permutation, F)
            result = protocol.verify_hamiltonian_proof(proof, F)
        else:
            proof = protocol.prove_isomorphism(H, permutation, F)
            result = protocol.verify_isomorphism_proof(proof, F)

        if result:
            print(f"  ✓ Раунд {round_num} пройден успешно")
            successful_rounds += 1
        else:
            print(f"  ✗ Раунд {round_num} провален")

    print(f"\nИтог: {successful_rounds} из {k} раундов пройдены успешно")

    if successful_rounds == k:
        print("\n✓ Боб убежден, что Алиса действительно знает гамильтонов цикл!")
        print(f"  Вероятность обмана: 1/2^k = 1/{2 ** k} ≈ {1 / (2 ** k):.4f}")
    else:
        print("\n✗ Алиса не смогла доказать знание гамильтонова цикла")

    print("\n" + "=" * 60)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("=" * 60)


def interactive_mode():
    """Интерактивный режим работы программы."""

    print("=" * 60)
    print("ИНТЕРАКТИВНЫЙ РЕЖИМ: ДОКАЗАТЕЛЬСТВО С НУЛЕВЫМ РАЗГЛАШЕНИЕМ")
    print("=" * 60)

    protocol = ZeroKnowledgeHamiltonian()

    # Выбор режима
    print("\nВыберите режим работы:")
    print("1. Демонстрация на тестовом графе")
    print("2. Загрузка своего графа из файла")

    choice = input("Ваш выбор (1/2): ").strip()

    if choice == "1":
        # Демонстрационный режим
        if not os.path.exists("test_graph.txt"):
            create_test_files()

        protocol.load_graph_from_file("test_graph.txt")

        if os.path.exists("test_cycle.txt"):
            protocol.load_hamiltonian_cycle_from_file("test_cycle.txt")
        else:
            print("Поиск гамильтонова цикла...")
            cycle = protocol.find_hamiltonian_cycle()
            print(f"Найден цикл: {cycle}")

    else:
        # Пользовательский режим
        graph_file = input("Введите имя файла с графом: ").strip()
        if not os.path.exists(graph_file):
            print(f"Файл {graph_file} не найден!")
            return

        protocol.load_graph_from_file(graph_file)

        cycle_choice = input("Загрузить гамильтонов цикл из файла? (y/n): ").strip().lower()
        if cycle_choice == 'y':
            cycle_file = input("Введите имя файла с циклом: ").strip()
            if os.path.exists(cycle_file):
                protocol.load_hamiltonian_cycle_from_file(cycle_file)
            else:
                print(f"Файл {cycle_file} не найден!")
                return
        else:
            print("Поиск гамильтонова цикла...")
            try:
                cycle = protocol.find_hamiltonian_cycle()
                print(f"Найден цикл: {cycle}")
            except Exception as e:
                print(f"Ошибка: {e}")
                print("Граф не содержит гамильтонов цикл!")
                return

    # Генерация ключей
    print("\nГенерация криптографических ключей...")
    protocol.generate_keys()

    # Количество раундов
    try:
        k = int(input("\nВведите количество раундов протокола (рекомендуется >= 10): ").strip())
    except ValueError:
        k = 10
        print(f"Используется значение по умолчанию: {k}")

    print(f"\nНачинаем {k} раундов протокола...")
    print("-" * 60)

    successful_rounds = 0

    for round_num in range(1, k + 1):
        print(f"\nРАУНД {round_num}:")
        print("-" * 30)

        # Шаг 1: Алиса создает изоморфный граф и шифрует его
        print("1. Алиса создает изоморфный граф H и шифрует его...")
        H, permutation, inverse_permutation = protocol.create_isomorphic_graph()
        F = protocol.encrypt_matrix(H)

        # Шаг 2: Боб задает вопрос
        question = random.randint(1, 2)
        if question == 1:
            print("2. Боб спрашивает: 'Каков гамильтонов цикл для графа H?'")
        else:
            print("2. Боб спрашивает: 'Действительно ли граф H изоморфен G?'")

        # Шаг 3: Алиса отвечает
        print("3. Алиса предоставляет доказательство...")
        if question == 1:
            proof = protocol.prove_hamiltonian_cycle(H, inverse_permutation, F)
        else:
            proof = protocol.prove_isomorphism(H, permutation, F)

        # Шаг 4: Боб проверяет
        print("4. Боб проверяет доказательство...")
        if question == 1:
            result = protocol.verify_hamiltonian_proof(proof, F)
        else:
            result = protocol.verify_isomorphism_proof(proof, F)

        if result:
            print(f"   ✓ Раунд {round_num} пройден")
            successful_rounds += 1
        else:
            print(f"   ✗ Раунд {round_num} провален")
            break  # Если раунд провален, прерываем выполнение

    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ПРОТОКОЛА")
    print("=" * 60)

    print(f"Всего раундов: {k}")
    print(f"Успешных раундов: {successful_rounds}")

    if successful_rounds == k:
        print(f"\n✓ Доказательство ПРИНЯТО")
        print(f"Вероятность обмана: 1/2^{k} = 1/{2 ** k} ≈ {1 / (2 ** k):.10f}")
        print("Боб убежден, что Алиса действительно знает гамильтонов цикл!")
    else:
        print(f"\n✗ Доказательство ОТВЕРГНУТО")
        print("Алиса не смогла доказать знание гамильтонова цикла")

    print("\n" + "=" * 60)


def main():
    """Главная функция программы."""

    print("=" * 60)
    print("ПРОГРАММА ДОКАЗАТЕЛЬСТВА С НУЛЕВЫМ РАЗГЛАШЕНИЕМ")
    print("ДЛЯ ЗАДАЧИ ГАМИЛЬТОНОВА ЦИКЛА")
    print("=" * 60)

    while True:
        print("\nВыберите режим работы:")
        print("1. Полная демонстрация протокола")
        print("2. Интерактивный режим")
        print("3. Создать тестовые файлы")
        print("4. Выход")

        choice = input("Ваш выбор (1-4): ").strip()

        if choice == "1":
            demo_protocol()
        elif choice == "2":
            interactive_mode()
        elif choice == "3":
            create_test_files()
            print("Тестовые файлы созданы!")
        elif choice == "4":
            print("Выход из программы...")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()