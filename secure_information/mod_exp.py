def mod_exp(a: int, x: int, p: int):
    y = 1
    s = a % p

    while x > 0:
        if x & 1:
            y = (y * s) % p
        s = (s * s) % p
        x >>= 1
    return y

print(mod_exp(157, 31, 721))