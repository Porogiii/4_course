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

def test_ferma(p: int, k: int):
    if p == 2:
        return True
    if p % 2 == 0 or p < 2:
        return False

    for _ in range(k):
        a = random.randint(1, p - 1)
        if mod_exp(a, p - 1, p) != 1:
            return False
    return True

print(test_ferma(45, 15))
print(test_ferma(18, 5))
