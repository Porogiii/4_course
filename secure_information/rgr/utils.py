# utils.py - дополнительные утилиты

def create_custom_graph():
    """
    Создание пользовательского графа через консольный ввод
    """
    print("Создание пользовательского графа")

    n = int(input("Количество вершин: "))
    m = int(input("Количество ребер: "))

    edges = []
    print("Введите ребра (по одному на строку, формат: u v):")
    for _ in range(m):
        u, v = map(int, input().split())
        edges.append((u, v))

    filename = input("Имя файла для сохранения: ")

    with open(filename, 'w') as f:
        f.write(f"{n} {m}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")

    print(f"Граф сохранен в {filename}")


def create_custom_cycle():
    """
    Создание пользовательского цикла через консольный ввод
    """
    print("Создание гамильтонова цикла")

    n = int(input("Количество вершин в графе: "))

    print(f"Введите последовательность из {n + 1} вершин (первая и последняя должны совпадать):")
    cycle = list(map(int, input().split()))

    if len(cycle) != n + 1 or cycle[0] != cycle[-1]:
        print("Ошибка: цикл должен начинаться и заканчиваться в одной вершине")
        return

    filename = input("Имя файла для сохранения: ")

    with open(filename, 'w') as f:
        f.write(" ".join(map(str, cycle)) + "\n")

    print(f"Цикл сохранен в {filename}")