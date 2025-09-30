import random
import math
import os
from typing import Tuple, List, Optional


# ======= Быстрое возведение в степень по модулю ======= #
def mod_exp(a: int, x: int, p: int) -> int:
    """Быстрое возведение в степень по модулю"""
    y = 1
    s = a % p
    while x > 0:
        if x & 1:
            y = (y * s) % p
        s = (s * s) % p
        x >>= 1
    return y


# ======= Тест Ферма ======= #
def test_ferma(p: int, k: int = 5) -> bool:
    """Тест Ферма на простоту"""
    if p == 2:
        return True
    if p % 2 == 0 or p < 2:
        return False

    for _ in range(k):
        a = random.randint(1, p - 1)
        if mod_exp(a, p - 1, p) != 1:
            return False
    return True


# ======= Расширенный алгоритм Евклида ======= #
def extended_euclid(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида"""
    U = [a, 1, 0]
    V = [b, 0, 1]

    while V[0] != 0:
        q = U[0] // V[0]
        T = [U[0] % V[0], U[1] - q * V[1], U[2] - q * V[2]]
        U, V = V, T

    return U[0], U[1], U[2]


def mod_inverse(a: int, m: int) -> int:
    """Нахождение обратного элемента по модулю"""
    g, x, _ = extended_euclid(a, m)
    if g != 1:
        raise ValueError(f"Обратный элемент не существует для a={a}, m={m}")
    return x % m


def generate_prime(lower: int = 100, upper: int = 1000, k: int = 5) -> int:
    """Генерация простого числа в заданном диапазоне"""
    while True:
        candidate = random.randint(lower, upper)
        if test_ferma(candidate, k):
            return candidate


def generate_large_prime(lower: int = 10 ** 8, upper: int = 10 ** 9, k: int = 10) -> int:
    """Генерация большого простого числа"""
    while True:
        candidate = random.randint(lower, upper)
        if test_ferma(candidate, k):
            return candidate


def prime_factors(n: int) -> set:
    """Разложение числа на простые множители"""
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)
    return factors


def find_primitive_root(p: int) -> int:
    """Поиск примитивного корня по модулю p"""
    if p == 2:
        return 1

    phi = p - 1
    factors = prime_factors(phi)

    for g in range(2, min(p, 10000)):
        if all(mod_exp(g, phi // factor, p) != 1 for factor in factors):
            return g
    return 2


# ======= Функции для RSA ======= #
def generate_coprime(phi: int) -> int:
    """Генерация числа, взаимно простого с phi"""
    while True:
        candidate = random.randint(2, phi - 1)
        if math.gcd(candidate, phi) == 1:
            return candidate


def rsa_generate_keys(mode: int = 1) -> Tuple[Tuple[int, int], Tuple[int, int, int, int]]:
    """Генерация ключей для RSA"""
    print("\n=== Генерация ключей RSA ===")

    if mode == 1:
        # Ручной ввод параметров
        p = int(input("Введите простое число p: "))
        q = int(input("Введите простое число q: "))
        d = int(input("Введите секретный ключ d: "))

        if not test_ferma(p):
            raise ValueError(f"Число p={p} не является простым!")
        if not test_ferma(q):
            raise ValueError(f"Число q={q} не является простым!")

    elif mode == 2:
        # Автоматическая генерация всех параметров
        print("Генерация простых чисел p и q...")
        p = generate_large_prime()
        q = generate_large_prime()
        while q == p:
            q = generate_large_prime()

        print(f"Сгенерированные простые числа:")
        print(f"p = {p}")
        print(f"q = {q}")

        # Генерация d
        phi = (p - 1) * (q - 1)
        d = generate_coprime(phi)
        print(f"d = {d}")

    else:
        raise ValueError("Неверный режим")

    # Вычисление остальных параметров
    n = p * q
    phi = (p - 1) * (q - 1)

    # Вычисление c (обратного к d по модулю phi)
    c = mod_inverse(d, phi)

    print(f"\nВычисленные параметры:")
    print(f"n = p * q = {p} * {q} = {n}")
    print(f"φ(n) = (p-1)*(q-1) = {phi}")
    print(f"c = d^(-1) mod φ(n) = {c}")

    public_key = (n, c)  # Открытый ключ: (n, c)
    private_key = (n, d, p, q)  # Закрытый ключ: (n, d, p, q)

    return public_key, private_key


def calculate_rsa_block_size(n: int) -> int:
    """Вычисление размера блока для RSA шифрования"""
    # Размер блока должен быть меньше n
    block_size_bits = n.bit_length() - 1
    block_size_bytes = max(1, block_size_bits // 8)
    return block_size_bytes


def rsa_encrypt_file(public_key: Tuple[int, int], input_file: str, output_file: str):
    """Шифрование файла с помощью RSA
        выбираем 2 простых числа p и q
        вычисляем n = pq
        вычисляем ф = (p-1)(q-1)
        выбираем d , чтобы нод (d, ф) = 1 и d < ф
        c такое, что cd mod ф = 1
        шифруем e = m^d mod n"""
    n, c = public_key
    block_size = calculate_rsa_block_size(n)

    print(f"Размер блока: {block_size} байт")

    # Чтение исходного файла
    with open(input_file, 'rb') as f:
        data = f.read()

    encrypted_blocks = []

    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]

        # Дополняем блок если нужно
        if len(block) < block_size:
            block = block.ljust(block_size, b'\x00')

        # Преобразуем блок в число
        m = int.from_bytes(block, 'big')

        # Убеждаемся, что m < n
        if m >= n:
            raise ValueError(f"Блок данных слишком большой для модуля n={n}")

        # Шифруем блок: e = m^c mod n
        e = mod_exp(m, c, n)
        encrypted_blocks.append(e)

    # Запись зашифрованного файла
    with open(output_file, 'wb') as f:
        # Записываем метаданные
        f.write(block_size.to_bytes(4, 'big'))
        f.write(len(encrypted_blocks).to_bytes(8, 'big'))

        # Записываем зашифрованные блоки
        for block in encrypted_blocks:
            block_bytes = block.to_bytes((n.bit_length() + 7) // 8, 'big')
            f.write(len(block_bytes).to_bytes(2, 'big'))
            f.write(block_bytes)

    print(f"Файл зашифрован. Размер исходного файла: {len(data)} байт")
    print(f"Количество блоков: {len(encrypted_blocks)}")


def rsa_decrypt_file(private_key: Tuple[int, int, int, int], input_file: str, output_file: str):
    """Дешифрование файла с помощью RSA
        m = e^d mod n"""
    n, d, p, q = private_key

    # Чтение зашифрованного файла
    with open(input_file, 'rb') as f:
        # Читаем метаданные
        block_size = int.from_bytes(f.read(4), 'big')
        num_blocks = int.from_bytes(f.read(8), 'big')

        encrypted_blocks = []
        for _ in range(num_blocks):
            block_len = int.from_bytes(f.read(2), 'big')
            block = int.from_bytes(f.read(block_len), 'big')
            encrypted_blocks.append(block)

    # Дешифрование
    decrypted_data = bytearray()

    for encrypted_block in encrypted_blocks:
        # Дешифруем блок: m = e^d mod n
        m = mod_exp(encrypted_block, d, n)

        # Преобразуем обратно в байты
        decrypted_block = m.to_bytes(block_size, 'big')
        decrypted_data.extend(decrypted_block)

    # Убираем дополняющие нули
    decrypted_data = decrypted_data.rstrip(b'\x00')

    # Запись расшифрованного файла
    with open(output_file, 'wb') as f:
        f.write(decrypted_data)

    print(f"Файл расшифрован. Размер: {len(decrypted_data)} байт")


def rsa_crypto_system():
    """Основная функция для работы с RSA"""
    print("\n=== RSA Шифрование ===")

    print("Выберите действие:")
    print("1 - Шифрование файла")
    print("2 - Дешифрование файла")
    action = int(input("Ваш выбор: "))

    print("\nВыберите способ задания параметров:")
    print("1 - Ввести параметры вручную")
    print("2 - Сгенерировать параметры автоматически")
    mode = int(input("Ваш выбор: "))

    if action == 1:
        # Шифрование
        public_key, private_key = rsa_generate_keys(mode)

        input_file = input("Введите путь к файлу для шифрования: ")
        output_file = input("Введите путь для сохранения зашифрованного файла: ")

        if not os.path.exists(input_file):
            print("Ошибка: исходный файл не существует!")
            return

        print("Шифрование...")
        rsa_encrypt_file(public_key, input_file, output_file)

        print(f"✓ Файл успешно зашифрован и сохранен как {output_file}")
        print(f"Секретный ключ для дешифрования: d = {private_key[1]}")
        print(f"Параметры p и q: p = {private_key[2]}, q = {private_key[3]}")

    elif action == 2:
        # Дешифрование
        if mode == 1:
            n = int(input("Введите модуль n: "))
            d = int(input("Введите секретный ключ d: "))
            p = int(input("Введите простое число p: "))
            q = int(input("Введите простое число q: "))
        else:
            print("Для дешифрования необходимо знать секретный ключ!")
            return

        private_key = (n, d, p, q)

        input_file = input("Введите путь к зашифрованному файлу: ")
        output_file = input("Введите путь для сохранения расшифрованного файла: ")

        if not os.path.exists(input_file):
            print("Ошибка: зашифрованный файл не существует!")
            return

        print("Дешифрование...")
        rsa_decrypt_file(private_key, input_file, output_file)

        print(f"✓ Файл успешно расшифрован и сохранен как {output_file}")

        # Пытаемся прочитать и показать содержимое как текст
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print("\nСодержимое файла (как текст):")
                print(content[:500] + "..." if len(content) > 500 else content)
        except:
            print("\nФайл содержит бинарные данные (не текст)")

    else:
        print("Неверный выбор действия!")


# ======= Схема Диффи-Хеллмана ======= #
def diffie_hellman_key_exchange() -> Optional[int]:
    """Схема Диффи-Хеллмана для обмена ключами"""
    print("\n=== Схема Диффи-Хеллмана ===")

    print("\nВыберите способ задания параметров:")
    print("1 - Ввести все параметры вручную")
    print("2 - Сгенерировать все параметры автоматически")
    print("3 - Ввести p и g, сгенерировать секретные ключи")

    mode = int(input("Ваш выбор: "))

    if mode == 1:
        p = int(input("Введите простое число p: "))
        g = int(input("Введите генератор g: "))
        Xa = int(input("Введите секретный ключ абонента A (Xa): "))
        Xb = int(input("Введите секретный ключ абонента B (Xb): "))

    elif mode == 2:
        print("Генерация простого числа p...")
        p = generate_large_prime()
        print("Поиск генератора g...")
        g = find_primitive_root(p)
        Xa = random.randint(2, p - 2)
        Xb = random.randint(2, p - 2)

        print(f"Сгенерированные параметры:")
        print(f"p = {p}")
        print(f"g = {g}")
        print(f"Xa = {Xa}")
        print(f"Xb = {Xb}")

    elif mode == 3:
        p = int(input("Введите простое число p: "))
        g = int(input("Введите генератор g: "))
        Xa = random.randint(2, p - 2)
        Xb = random.randint(2, p - 2)

        print(f"Сгенерированные секретные ключи:")
        print(f"Xa = {Xa}")
        print(f"Xb = {Xb}")

    else:
        print("Неверный режим")
        return None

    # Вычисление открытых ключей
    Ya = mod_exp(g, Xa, p)
    Yb = mod_exp(g, Xb, p)

    print(f"\nОткрытые ключи:")
    print(f"Ya = g^Xa mod p = {g}^{Xa} mod {p} = {Ya}")
    print(f"Yb = g^Xb mod p = {g}^{Xb} mod {p} = {Yb}")

    # Вычисление общего секретного ключа
    Kab_A = mod_exp(Yb, Xa, p)
    Kab_B = mod_exp(Ya, Xb, p)

    print(f"\nОбщий секретный ключ:")
    print(f"Kab (вычисленный A) = Yb^Xa mod p = {Yb}^{Xa} mod {p} = {Kab_A}")
    print(f"Kab (вычисленный B) = Ya^Xb mod p = {Ya}^{Xb} mod {p} = {Kab_B}")

    if Kab_A == Kab_B:
        print("✓ Ключи совпадают! Обмен успешен.")
        return Kab_A
    else:
        print("✗ Ошибка: ключи не совпадают!")
        return None


# ======= Шифр Эль-Гамаля ======= #
def elgamal_generate_keys(mode: int = 1) -> Tuple[Tuple[int, int, int], Tuple[int, int]]:
    """Генерация ключей для шифра Эль-Гамаля"""
    print("\n=== Генерация ключей Эль-Гамаля ===")

    if mode == 1:
        p = int(input("Введите простое число p: "))
        g = int(input("Введите генератор g: "))
        C1 = int(input("Введите открытый ключ C1: "))
        D1 = random.randint(2, p - 2)

    elif mode == 2:
        print("Генерация простого числа p...")
        p = generate_large_prime()
        print("Поиск генератора g...")
        g = find_primitive_root(p)
        D1 = random.randint(2, p - 2)
        C1 = mod_exp(g, D1, p)

        print(f"Сгенерированные параметры:")
        print(f"p = {p}")
        print(f"g = {g}")
        print(f"C1 = {C1}")
        print(f"D1 = {D1}")

    else:
        raise ValueError("Неверный режим")

    public_key = (p, g, C1)
    private_key = (p, D1)
    return public_key, private_key


def calculate_block_size(p: int) -> int:
    """Вычисление размера блока для шифрования"""
    # Размер блока должен быть меньше p
    block_size_bits = p.bit_length() - 1
    block_size_bytes = max(1, block_size_bits // 8)
    return block_size_bytes


def elgamal_encrypt_file(public_key: Tuple[int, int, int], input_file: str, output_file: str):
    """Шифрование файла с помощью Эль-Гамаля"""
    p, g, C1 = public_key
    block_size = calculate_block_size(p)

    print(f"Размер блока: {block_size} байт")

    # Чтение исходного файла
    with open(input_file, 'rb') as f:
        data = f.read()

    encrypted_blocks = []

    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]

        # Дополняем блок если нужно
        if len(block) < block_size:
            block = block.ljust(block_size, b'\x00')

        # Преобразуем блок в число
        m = int.from_bytes(block, 'big')

        # Убеждаемся, что m < p
        if m >= p:
            m = m % p

        # Шифруем блок
        k = random.randint(2, p - 2)
        a = mod_exp(g, k, p)
        b = (m * mod_exp(C1, k, p)) % p

        encrypted_blocks.append((a, b))

    # Запись зашифрованного файла
    with open(output_file, 'wb') as f:
        # Записываем метаданные
        f.write(block_size.to_bytes(4, 'big'))
        f.write(len(encrypted_blocks).to_bytes(8, 'big'))

        # Записываем зашифрованные блоки
        for a, b in encrypted_blocks:
            a_bytes = a.to_bytes((p.bit_length() + 7) // 8, 'big')
            b_bytes = b.to_bytes((p.bit_length() + 7) // 8, 'big')

            f.write(len(a_bytes).to_bytes(2, 'big'))
            f.write(a_bytes)
            f.write(len(b_bytes).to_bytes(2, 'big'))
            f.write(b_bytes)

    print(f"Файл зашифрован. Размер исходного файла: {len(data)} байт")
    print(f"Количество блоков: {len(encrypted_blocks)}")


def elgamal_decrypt_file(private_key: Tuple[int, int], input_file: str, output_file: str):
    """Дешифрование файла с помощью Эль-Гамаля"""
    p, D1 = private_key

    # Чтение зашифрованного файла
    with open(input_file, 'rb') as f:
        # Читаем метаданные
        block_size = int.from_bytes(f.read(4), 'big')
        num_blocks = int.from_bytes(f.read(8), 'big')

        encrypted_blocks = []
        for _ in range(num_blocks):
            a_len = int.from_bytes(f.read(2), 'big')
            a = int.from_bytes(f.read(a_len), 'big')
            b_len = int.from_bytes(f.read(2), 'big')
            b = int.from_bytes(f.read(b_len), 'big')
            encrypted_blocks.append((a, b))

    # Дешифрование
    decrypted_data = bytearray()

    for a, b in encrypted_blocks:
        # Вычисляем s = a^D1 mod p
        s = mod_exp(a, D1, p)

        # Находим обратный элемент
        s_inv = mod_inverse(s, p)

        # Восстанавливаем сообщение
        m = (b * s_inv) % p

        # Преобразуем обратно в байты
        decrypted_block = m.to_bytes(block_size, 'big')
        decrypted_data.extend(decrypted_block)

    # Убираем дополняющие нули
    decrypted_data = decrypted_data.rstrip(b'\x00')

    # Запись расшифрованного файла
    with open(output_file, 'wb') as f:
        f.write(decrypted_data)

    print(f"Файл расшифрован. Размер: {len(decrypted_data)} байт")


def elgamal_crypto_system():
    """Основная функция для работы с шифром Эль-Гамаля"""
    print("\n=== Шифр Эль-Гамаля ===")

    print("Выберите действие:")
    print("1 - Шифрование файла")
    print("2 - Дешифрование файла")
    action = int(input("Ваш выбор: "))

    print("\nВыберите способ задания параметров:")
    print("1 - Ввести параметры вручную")
    print("2 - Сгенерировать параметры автоматически")
    mode = int(input("Ваш выбор: "))

    if action == 1:
        # Шифрование
        public_key, private_key = elgamal_generate_keys(mode)

        input_file = input("Введите путь к файлу для шифрования: ")
        output_file = input("Введите путь для сохранения зашифрованного файла: ")

        if not os.path.exists(input_file):
            print("Ошибка: исходный файл не существует!")
            return

        print("Шифрование...")
        elgamal_encrypt_file(public_key, input_file, output_file)

        print(f"✓ Файл успешно зашифрован и сохранен как {output_file}")
        print(f"Секретный ключ для дешифрования: D1 = {private_key[1]}")

    elif action == 2:
        # Дешифрование
        if mode == 1:
            p = int(input("Введите простое число p: "))
            D1 = int(input("Введите секретный ключ D1: "))
        else:
            print("Для дешифрования необходимо знать секретный ключ!")
            return

        private_key = (p, D1)

        input_file = input("Введите путь к зашифрованному файлу: ")
        output_file = input("Введите путь для сохранения расшифрованного файла: ")

        if not os.path.exists(input_file):
            print("Ошибка: зашифрованный файл не существует!")
            return

        print("Дешифрование...")
        elgamal_decrypt_file(private_key, input_file, output_file)

        print(f"✓ Файл успешно расшифрован и сохранен как {output_file}")

        # Пытаемся прочитать и показать содержимое как текст
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print("\nСодержимое файла (как текст):")
                print(content[:500] + "..." if len(content) > 500 else content)
        except:
            print("\nФайл содержит бинарные данные (не текст)")

    else:
        print("Неверный выбор действия!")


# ======= Шифр Шамира ======= #
def shamir_generate_keys(mode: int = 1) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Генерация ключей для шифра Шамира"""
    print("\n=== Генерация ключей Шамира ===")

    if mode == 1:
        p = int(input("Введите простое число p: "))
        Ca = int(input("Введите открытый ключ абонента A (Ca): "))
        Cb = int(input("Введите открытый ключ абонента B (Cb): "))

        # Проверяем взаимную простоту
        if math.gcd(Ca, p - 1) != 1:
            raise ValueError("Ca должен быть взаимно прост с p-1")
        if math.gcd(Cb, p - 1) != 1:
            raise ValueError("Cb должен быть взаимно прост с p-1")

        Da = mod_inverse(Ca, p - 1)
        Db = mod_inverse(Cb, p - 1)

    elif mode == 2:
        p = generate_large_prime()

        # Генерация ключей с проверкой взаимной простоты
        while True:
            Ca = random.randint(2, p - 2)
            if math.gcd(Ca, p - 1) == 1:
                break

        while True:
            Cb = random.randint(2, p - 2)
            if math.gcd(Cb, p - 1) == 1:
                break

        Da = mod_inverse(Ca, p - 1)
        Db = mod_inverse(Cb, p - 1)

        print(f"Сгенерированные параметры:")
        print(f"p = {p}")
        print(f"Ca = {Ca}")
        print(f"Cb = {Cb}")
        print(f"Da = {Da}")
        print(f"Db = {Db}")

    else:
        raise ValueError("Неверный режим")

    keys_a = (p, Ca, Da)
    keys_b = (p, Cb, Db)
    return keys_a, keys_b


def shamir_encrypt_file(keys_a: Tuple[int, int, int], keys_b: Tuple[int, int, int],
                        input_file: str, output_file: str):
    """Шифрование файла с помощью шифра Шамира"""
    p, Ca, Da = keys_a
    p, Cb, Db = keys_b
    block_size = calculate_block_size(p)

    print(f"Размер блока: {block_size} байт")

    # Чтение исходного файла
    with open(input_file, 'rb') as f:
        data = f.read()

    encrypted_blocks = []

    for i in range(0, len(data), block_size):
        block = data[i:i + block_size]

        if len(block) < block_size:
            block = block.ljust(block_size, b'\x00')

        m = int.from_bytes(block, 'big')
        if m >= p:
            m = m % p

        # Схема Шамира (3 прохода)
        # 1. A -> B: x1 = m^Ca mod p
        x1 = mod_exp(m, Ca, p)

        # 2. B -> A: x2 = x1^Cb mod p
        x2 = mod_exp(x1, Cb, p)

        # 3. A -> B: x3 = x2^Da mod p
        x3 = mod_exp(x2, Da, p)

        # B вычисляет: m = x3^Db mod p
        encrypted_blocks.append(x3)

    # Запись зашифрованного файла
    with open(output_file, 'wb') as f:
        f.write(block_size.to_bytes(4, 'big'))
        f.write(len(encrypted_blocks).to_bytes(8, 'big'))

        for block in encrypted_blocks:
            block_bytes = block.to_bytes((p.bit_length() + 7) // 8, 'big')
            f.write(len(block_bytes).to_bytes(2, 'big'))
            f.write(block_bytes)

    print(f"Файл зашифрован. Размер исходного файла: {len(data)} байт")
    print(f"Количество блоков: {len(encrypted_blocks)}")


def shamir_decrypt_file(keys_a: Tuple[int, int, int], keys_b: Tuple[int, int, int],
                        input_file: str, output_file: str):
    """Дешифрование файла с помощью шифра Шамира"""
    p, Ca, Da = keys_a
    p, Cb, Db = keys_b

    # Чтение зашифрованного файла
    with open(input_file, 'rb') as f:
        block_size = int.from_bytes(f.read(4), 'big')
        num_blocks = int.from_bytes(f.read(8), 'big')

        encrypted_blocks = []
        for _ in range(num_blocks):
            block_len = int.from_bytes(f.read(2), 'big')
            block = int.from_bytes(f.read(block_len), 'big')
            encrypted_blocks.append(block)

    # Дешифрование
    decrypted_data = bytearray()

    for encrypted_block in encrypted_blocks:
        # B дешифрует: m = encrypted_block^Db mod p
        m = mod_exp(encrypted_block, Db, p)

        decrypted_block = m.to_bytes(block_size, 'big')
        decrypted_data.extend(decrypted_block)

    # Убираем дополняющие нули
    decrypted_data = decrypted_data.rstrip(b'\x00')

    # Запись расшифрованного файла
    with open(output_file, 'wb') as f:
        f.write(decrypted_data)

    print(f"Файл расшифрован. Размер: {len(decrypted_data)} байт")


def shamir_crypto_system():
    """Основная функция для работы с шифром Шамира"""
    print("\n=== Шифр Шамира ===")

    print("Выберите действие:")
    print("1 - Шифрование файла")
    print("2 - Дешифрование файла")
    action = int(input("Ваш выбор: "))

    print("\nВыберите способ задания параметров:")
    print("1 - Ввести параметры вручную")
    print("2 - Сгенерировать параметры автоматически")
    mode = int(input("Ваш выбор: "))

    if action == 1:
        # Шифрование
        keys_a, keys_b = shamir_generate_keys(mode)

        input_file = input("Введите путь к файлу для шифрования: ")
        output_file = input("Введите путь для сохранения зашифрованного файла: ")

        if not os.path.exists(input_file):
            print("Ошибка: исходный файл не существует!")
            return

        print("Шифрование...")
        shamir_encrypt_file(keys_a, keys_b, input_file, output_file)

        print(f"✓ Файл успешно зашифрован и сохранен как {output_file}")
        print(f"Секретные ключи для дешифрования:")
        print(f"Da = {keys_a[2]}")
        print(f"Db = {keys_b[2]}")

    elif action == 2:
        # Дешифрование
        if mode == 1:
            p = int(input("Введите простое число p: "))
            Ca = int(input("Введите открытый ключ абонента A (Ca): "))
            Da = int(input("Введите секретный ключ абонента A (Da): "))
            Cb = int(input("Введите открытый ключ абонента B (Cb): "))
            Db = int(input("Введите секретный ключ абонента B (Db): "))
        else:
            print("Для дешифрования необходимо знать секретные ключи!")
            return

        keys_a = (p, Ca, Da)
        keys_b = (p, Cb, Db)

        input_file = input("Введите путь к зашифрованному файлу: ")
        output_file = input("Введите путь для сохранения расшифрованного файла: ")

        if not os.path.exists(input_file):
            print("Ошибка: зашифрованный файл не существует!")
            return

        print("Дешифрование...")
        shamir_decrypt_file(keys_a, keys_b, input_file, output_file)

        print(f"✓ Файл успешно расшифрован и сохранен как {output_file}")

        # Пытаемся прочитать и показать содержимое как текст
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print("\nСодержимое файла (как текст):")
                print(content[:500] + "..." if len(content) > 500 else content)
        except:
            print("\nФайл содержит бинарные данные (не текст)")

    else:
        print("Неверный выбор действия!")


# ======= Тестирование ======= #
def create_test_file(filename: str = "test_file.txt"):
    """Создание тестового файла"""
    test_content = """Hello, World! Чупапи муняня !@#$%^&*() 1234567890
    ты на пенёк сел
    должен был косарь отдать"""

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(test_content)

    print(f"Создан тестовый файл: {filename}")
    return filename


def test_encryption_systems():
    """Тестирование систем шифрования"""
    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ СИСТЕМ ШИФРОВАНИЯ")
    print("=" * 60)

    # Создаем тестовый файл
    test_file = create_test_file()

    print("\n1. ТЕСТ ШИФРА ЭЛЬ-ГАМАЛЯ")
    print("-" * 40)

    # Генерируем ключи
    public_key, private_key = elgamal_generate_keys(2)

    # Шифруем
    elgamal_encrypt_file(public_key, test_file, "encrypted_elgamal.bin")

    # Дешифруем
    elgamal_decrypt_file(private_key, "encrypted_elgamal.bin", "decrypted_elgamal.txt")

    # Проверяем
    with open(test_file, 'r', encoding='utf-8') as f1, open("decrypted_elgamal.txt", 'r', encoding='utf-8') as f2:
        original = f1.read()
        decrypted = f2.read()

    if original == decrypted:
        print("✓ Шифр Эль-Гамаля: УСПЕХ")
        print(f"Исходный размер: {len(original)} символов")
        print(f"Расшифрованный размер: {len(decrypted)} символов")
    else:
        print("✗ Шифр Эль-Гамаля: ОШИБКА")

    print("\n2. ТЕСТ ШИФРА ШАМИРА")
    print("-" * 40)

    # Генерируем ключи
    keys_a, keys_b = shamir_generate_keys(2)

    # Шифруем
    shamir_encrypt_file(keys_a, keys_b, test_file, "encrypted_shamir.bin")

    # Дешифруем
    shamir_decrypt_file(keys_a, keys_b, "encrypted_shamir.bin", "decrypted_shamir.txt")

    # Проверяем
    with open(test_file, 'r', encoding='utf-8') as f1, open("decrypted_shamir.txt", 'r', encoding='utf-8') as f2:
        original = f1.read()
        decrypted = f2.read()

    if original == decrypted:
        print("✓ Шифр Шамира: УСПЕХ")
        print(f"Исходный размер: {len(original)} символов")
        print(f"Расшифрованный размер: {len(decrypted)} символов")
    else:
        print("✗ Шифр Шамира: ОШИБКА")

    print("\n3. ТЕСТ RSA ШИФРОВАНИЯ")
    print("-" * 40)

    # Генерируем ключи
    public_key, private_key = rsa_generate_keys(2)

    # Шифруем
    rsa_encrypt_file(public_key, test_file, "encrypted_rsa.bin")

    # Дешифруем
    rsa_decrypt_file(private_key, "encrypted_rsa.bin", "decrypted_rsa.txt")

    # Проверяем
    with open(test_file, 'r', encoding='utf-8') as f1, open("decrypted_rsa.txt", 'r', encoding='utf-8') as f2:
        original = f1.read()
        decrypted = f2.read()

    if original == decrypted:
        print("✓ RSA Шифрование: УСПЕХ")
        print(f"Исходный размер: {len(original)} символов")
        print(f"Расшифрованный размер: {len(decrypted)} символов")
    else:
        print("✗ RSA Шифрование: ОШИБКА")

    print("\n" + "=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 60)


# ======= Основная программа ======= #
def main():
    while True:
        print("\n" + "=" * 60)
        print("КРИПТОГРАФИЧЕСКАЯ СИСТЕМА")
        print("=" * 60)
        print("1 - Возведение в степень по модулю")
        print("2 - Тест Ферма (проверка на простоту)")
        print("3 - Расширенный алгоритм Евклида")
        print("4 - Схема Диффи-Хеллмана (общий ключ)")
        print("5 - Шифр Эль-Гамаля (шифрование/дешифрование файлов)")
        print("6 - Шифр Шамира (шифрование/дешифрование файлов)")
        print("7 - RSA (шифрование/дешифрование файлов)")
        print("8 - Тестирование систем шифрования")
        print("0 - Выход")

        try:
            choice = int(input("Ваш выбор: "))
        except ValueError:
            print("Ошибка: введите число от 0 до 8")
            continue

        if choice == 0:
            print("Выход из программы...")
            break
        elif choice == 1:
            a = int(input("Введите a: "))
            x = int(input("Введите показатель степени x: "))
            p = int(input("Введите модуль p: "))
            result = mod_exp(a, x, p)
            print(f"{a}^{x} mod {p} = {result}")
        elif choice == 2:
            n = int(input("Введите число для проверки на простоту: "))
            k = int(input("Введите количество повторов k: "))
            is_prime = test_ferma(n, k)
            print(f"{n} - {'простое' if is_prime else 'составное'}")
        elif choice == 3:
            a = int(input("Введите a: "))
            b = int(input("Введите b: "))
            g, x, y = extended_euclid(a, b)
            print(f"НОД({a}, {b}) = {g}")
            print(f"Коэффициенты Безу: {a}*({x}) + {b}*({y}) = {g}")
        elif choice == 4:
            diffie_hellman_key_exchange()
        elif choice == 5:
            elgamal_crypto_system()
        elif choice == 6:
            shamir_crypto_system()
        elif choice == 7:
            rsa_crypto_system()
        elif choice == 8:
            test_encryption_systems()
        else:
            print("Неверный выбор! Попробуйте снова.")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()