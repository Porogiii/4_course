import random
import math

def mod_exp(a: int, x: int, p: int):
    y = 1
    s = a % p

    while x > 0:
        if x & 1:
            y = (y * s) % p
        s = (s * s) % p
        x >>= 1
    return y


def test_ferma(p: int, k: int = 5):
    if p == 2:
        return True
    if p % 2 == 0 or p < 2:
        return False

    for _ in range(k):
        a = random.randint(1, p - 1)
        if math.gcd(a, p) != 1 or mod_exp(a, p - 1, p) != 1:
            return False
    return True

def extended_euclid(a: int, b: int):
    U = [a, 1, 0]
    V = [b, 0, 1]

    while V[0] != 0:
        q = U[0] // V[0]
        T = [U[0] % V[0], U[1] - q * V[1], U[2] - q * V[2]]
        U, V = V, T

    return U[0], U[1], U[2]

def get_numbers(mode: int):
    """
    mode = 1 -> ввод с клавиатуры
    mode = 2 -> случайные числа
    mode = 3 -> случайные простые числа (по тесту Ферма)
    """
    if mode == 1:
        a = int(input("Введите a: "))
        b = int(input("Введите b: "))
    elif mode == 2:
        a = random.randint(10, 500)
        b = random.randint(10, 500)
    elif mode == 3:
        def gen_prime():
            while True:
                n = random.randint(50, 500)
                if test_ferma(n, 7):
                    return n

        a = gen_prime()
        b = gen_prime()
    else:
        raise ValueError("Неверный режим")

    if a < b:
        a, b = b, a
    return a, b

if __name__ == "__main__":
    print("Выберите режим:")
    print("1 - Ввод чисел с клавиатуры")
    print("2 - Генерация случайных чисел")
    print("3 - Генерация случайных простых чисел (тест Ферма)")
    mode = int(input("Режим: "))

    a, b = get_numbers(mode)
    print(f"a = {a}, b = {b}")

    g, x, y = extended_euclid(a, b)
    print(f"НОД({a}, {b}) = {g}")
    print(f"{a}*({x}) + {b}*({y}) = {a*x + b*y}")
