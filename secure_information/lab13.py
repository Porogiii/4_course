import secrets
import hashlib
import sys
import math
from typing import Tuple

PRIME_BITS = 256
RND_BITS = 512

def is_probable_prime(n: int, rounds: int = 16) -> bool:
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            continue
        for _ in range(s - 1):
            x = (x*x) % n
            if x == n-1:
                break
        else:
            return False
    return True

def generate_prime(bits: int) -> int:
    while True:
        p = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(p):
            return p

def egcd_iter(a: int, b: int) -> Tuple[int,int,int]:
    x0, x1 = 1, 0
    y0, y1 = 0, 1
    while b != 0:
        q, a, b = a // b, b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0

def modinv(a: int, m: int) -> int:
    g, x, _ = egcd_iter(a, m)
    if g != 1:
        raise ValueError("Inverse does not exist")
    return x % m


class Server:
    def __init__(self, prime_bits=PRIME_BITS):
        print("[server] Генерация RSA-ключей...")
        self.P = generate_prime(prime_bits)
        self.Q = generate_prime(prime_bits)
        while self.Q == self.P:
            self.Q = generate_prime(prime_bits)
        self.N = self.P * self.Q
        self.phi = (self.P - 1) * (self.Q - 1)

        e = 65537
        if math.gcd(e, self.phi) != 1:
            e = 3
            while math.gcd(e, self.phi) != 1:
                e += 2

        self.e = e
        self.d = modinv(self.e, self.phi)

        self.issued = set()
        self.votes_db = []

        print("[server] Готово.")

    def issue_signed_blind(self, client_id: str, h_bar: int) -> int:
        if client_id in self.issued:
            raise PermissionError("Этому человеку уже выдавали бюллетень!")
        self.issued.add(client_id)
        return pow(h_bar, self.d, self.N)

    def verify_and_accept(self, n: int, s: int) -> bool:
        h = sha3_int(n)
        if pow(s, self.e, self.N) == h:
            vote_info = decode_n(n)
            self.votes_db.append((n, s, vote_info))
            return True
        return False

    def print_public_info(self):
        print("----- Публичные параметры -----")
        print(f"N = {self.N}")
        print(f"e = {self.e}")
        print("--------------------------------")

    def print_votes(self):
        print("\n=== Принятые голоса ===")
        if not self.votes_db:
            print("Пока нет голосов.")
            return
        for i, (_, _, info) in enumerate(self.votes_db, 1):
            print(f"{i}) Голос: {info['vote']} (код {info['vote_code']})")


def sha3_int(n: int) -> int:
    b = n.to_bytes((n.bit_length() + 7) // 8 or 1, 'big')
    h = hashlib.sha3_256(b).digest()
    return int.from_bytes(h, 'big')

def encode_vote(vote_choice: str, extra_info: str = "") -> int:
    mapping = {"Да": 1, "Нет": 0, "Воздержался": 2}
    if vote_choice not in mapping:
        raise ValueError("Неверный вариант.")
    code = mapping[vote_choice] & 0xFF
    h = hashlib.sha3_256(extra_info.encode('utf-8')).digest()
    prefix = int.from_bytes(h[:63], 'big')
    return (prefix << 8) | code

def decode_n(n: int) -> dict:
    v_mask = (1 << 512) - 1
    v = n & v_mask
    rnd = n >> 512
    code = v & 0xFF
    mapping = {1: "Да", 0: "Нет", 2: "Воздержался"}
    return {"vote_code": code, "vote": mapping.get(code, "??")}

def client_vote_flow(server: Server, client_id: str, vote_choice: str):
    print(f"\n[client] Голосование за '{vote_choice}'...")

    rnd = secrets.randbits(RND_BITS)

    v_field = encode_vote(vote_choice, extra_info="Election2025")
    n = (rnd << 512) | v_field

    h = sha3_int(n)

    while True:
        r = secrets.randbelow(server.N - 2) + 2
        if math.gcd(r, server.N) == 1:
            break
    h_bar = (h * pow(r, server.e, server.N)) % server.N

    try:
        s_bar = server.issue_signed_blind(client_id, h_bar)
    except PermissionError as e:
        print("[client]", e)
        return

    s = (s_bar * modinv(r, server.N)) % server.N

    if server.verify_and_accept(n, s):
        print("[client] Голос принят!")
    else:
        print("[client] Голос отклонён.")


def menu(server: Server):
    while True:
        print("\n==== МЕНЮ ГОЛОСОВАНИЯ ====")
        print("1) Проголосовать")
        print("2) Показать принятые голоса")
        print("3) Показать публичные параметры сервера")
        print("4) Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            cid = input("Введите ваш ID (например user123): ").strip()
            print("Варианты:")
            print("  1 — Да")
            print("  2 — Нет")
            print("  3 — Воздержался")
            v = input("Выберите вариант: ").strip()
            mapping = {"1": "Да", "2": "Нет", "3": "Воздержался"}
            if v not in mapping:
                print("Неверный ввод.")
                continue
            client_vote_flow(server, cid, mapping[v])

        elif choice == "2":
            server.print_votes()

        elif choice == "3":
            server.print_public_info()

        elif choice == "4":
            print("Выход.")
            break

        else:
            print("Неизвестный пункт меню.")


def main():
    print("=== Протокол слепой подписи — голосование ===")
    server = Server(prime_bits=PRIME_BITS)
    menu(server)

if __name__ == "__main__":
    main()
