import hashlib
import struct
import random
import math
from typing import Tuple, List, Optional
from crypto_lib import CryptoUtils


class FIPS186Signature:

    def __init__(self):
        self.utils = CryptoUtils()

    def generate_domain_parameters(self, L: int = 1024, N: int = 160) -> Tuple[int, int, int]:
        print(f"Генерация доменных параметров DSA (L={L}, N={N})...")

        if L == 1024 and N == 160:
            print("Используются упрощенные размеры для лабораторной работы:")
            L, N = 31, 16

        print(f"Генерация простого числа q ({N} бит)...")
        q_lower = 2 ** (N - 1)
        q_upper = 2 ** N - 1
        q = self.utils.generate_prime(q_lower, q_upper)
        print(f"q = {q} (бит: {q.bit_length()})")

        print(f"Генерация простого числа p ({L} бит)...")
        p_lower = 2 ** (L - 1)
        p_upper = 2 ** L - 1

        while True:
            k_min = p_lower // q
            k_max = p_upper // q
            k = random.randint(k_min, k_max)
            p_candidate = k * q + 1

            if p_lower <= p_candidate <= p_upper and self.utils.test_ferma(p_candidate):
                p = p_candidate
                break

        print(f"p = {p} (бит: {p.bit_length()})")
        print(f"k = {k}")
        print(f"Проверка: p = k*q + 1 = {k}*{q} + 1 = {k * q + 1}")
        print(f"Проверка: (p-1) % q = {(p - 1) % q}")

        print("Генерация генератора g...")
        while True:
            h = random.randint(2, p - 2)
            g = self.utils.mod_exp(h, (p - 1) // q, p)
            if g > 1:
                break

        print(f"h = {h}")
        print(f"g = h^((p-1)/q) mod p = {h}^({(p - 1) // q}) mod {p} = {g}")

        check = self.utils.mod_exp(g, q, p)
        print(f"Проверка: g^q mod p = {g}^{q} mod {p} = {check}")

        return p, q, g

    def generate_keys(self, p: int, q: int, g: int) -> Tuple[int, int]:

        print("\nГенерация ключевой пары DSA...")

        x = random.randint(1, q - 1)

        y = self.utils.mod_exp(g, x, p)

        print(f"Секретный ключ x = {x}")
        print(f"Открытый ключ y = g^x mod p = {g}^{x} mod {p} = {y}")

        return x, y

    def compute_hash(self, data: bytes, q: int) -> int:

        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        hash_bytes = hash_obj.digest()

        h = int.from_bytes(hash_bytes, 'big')

        h = h % (q - 1) + 1

        hash_hex = hash_obj.hexdigest()
        print(f"Хеш документа (SHA-256): {hash_hex}")
        print(f"h = {h} (0 < h < q)")

        return h

    def sign(self, data: bytes, p: int, q: int, g: int, x: int) -> Tuple[int, int]:
        print("\nПодписание документа по DSA...")

        h = self.compute_hash(data, q)

        while True:
            k = random.randint(1, q - 1)
            r = self.utils.mod_exp(g, k, p) % q
            if r == 0:
                continue

            try:
                k_inv = self.utils.mod_inverse(k, q)
                s = (k_inv * (h + x * r)) % q

                if s == 0:
                    continue

                break

            except ValueError:
                continue

        print(f"Эфемерный ключ k = {k}")
        print(f"r = (g^k mod p) mod q = ({g}^{k} mod {p}) mod {q} = {r}")
        print(f"s = k^(-1) * (h + x*r) mod q = {k_inv} * ({h} + {x}*{r}) mod {q} = {s}")

        return r, s

    def verify(self, data: bytes, signature: Tuple[int, int], p: int, q: int, g: int, y: int) -> bool:

        print("\nПроверка подписи DSA...")

        r, s = signature

        if not (0 < r < q and 0 < s < q):
            print("Ошибка: r или s не в диапазоне (0, q)")
            return False

        print(f"Проверка: 0 < r={r} < q={q} - OK")
        print(f"Проверка: 0 < s={s} < q={q} - OK")

        h = self.compute_hash(data, q)

        try:
            w = self.utils.mod_inverse(s, q)
            print(f"w = s^(-1) mod q = {s}^(-1) mod {q} = {w}")

            u1 = (h * w) % q
            u2 = (r * w) % q

            print(f"u1 = h * w mod q = {h} * {w} mod {q} = {u1}")
            print(f"u2 = r * w mod q = {r} * {w} mod {q} = {u2}")

            g_u1 = self.utils.mod_exp(g, u1, p)
            y_u2 = self.utils.mod_exp(y, u2, p)
            v = ((g_u1 * y_u2) % p) % q

            print(f"g^u1 mod p = {g}^{u1} mod {p} = {g_u1}")
            print(f"y^u2 mod p = {y}^{u2} mod {p} = {y_u2}")
            print(f"v = (g^u1 * y^u2 mod p) mod q = ({g_u1} * {y_u2} mod {p}) mod {q} = {v}")

            print(f"Проверка: v = {v}, r = {r}")
            if v == r:
                print("✓ Подпись DSA верна!")
                return True
            else:
                print("✗ Подпись DSA неверна!")
                return False

        except ValueError as e:
            print(f"Ошибка при вычислении обратного элемента: {e}")
            return False

    def sign_file(self, input_file: str, p: int, q: int, g: int, x: int,
                  signature_file: Optional[str] = None) -> str:

        print(f"Подписание файла: {input_file}")

        with open(input_file, 'rb') as f:
            data = f.read()

        r, s = self.sign(data, p, q, g, x)

        if signature_file is None:
            signature_file = input_file + '.dsa_sig'

        self._save_signature(signature_file, r, s, p.bit_length())

        print(f"Файл успешно подписан. Подпись сохранена в: {signature_file}")
        return signature_file

    def verify_file(self, input_file: str, signature_file: str,
                    p: int, q: int, g: int, y: int) -> bool:

        print(f"Проверка подписи DSA файла: {input_file}")

        # Чтение файла
        with open(input_file, 'rb') as f:
            data = f.read()

        r, s = self._load_signature(signature_file, p.bit_length())

        return self.verify(data, (r, s), p, q, g, y)

    def _save_signature(self, filename: str, r: int, s: int, bit_length: int):

        with open(filename, 'wb') as f:
            byte_size = (bit_length + 7) // 8

            r_bytes = r.to_bytes(byte_size, 'big')
            s_bytes = s.to_bytes(byte_size, 'big')

            f.write(struct.pack('>I', byte_size))
            f.write(r_bytes)
            f.write(s_bytes)

    def _load_signature(self, filename: str, bit_length: int) -> Tuple[int, int]:
        with open(filename, 'rb') as f:
            byte_size = struct.unpack('>I', f.read(4))[0]

            r_bytes = f.read(byte_size)
            s_bytes = f.read(byte_size)

            r = int.from_bytes(r_bytes, 'big')
            s = int.from_bytes(s_bytes, 'big')

        return r, s

    def save_domain_params(self, p: int, q: int, g: int, filename: str):
        with open(filename, 'w') as f:
            f.write(f"{p}\n{q}\n{g}")

        print(f"Доменные параметры сохранены в: {filename}")

    def load_domain_params(self, filename: str) -> Tuple[int, int, int]:
        with open(filename, 'r') as f:
            lines = f.readlines()
            p = int(lines[0].strip())
            q = int(lines[1].strip())
            g = int(lines[2].strip())

        print("Доменные параметры загружены")
        return p, q, g

    def save_keys(self, x: int, y: int, private_key_file: str, public_key_file: str):

        with open(private_key_file, 'w') as f:
            f.write(f"{x}")

        with open(public_key_file, 'w') as f:
            f.write(f"{y}")

        print(f"Секретный ключ сохранен в: {private_key_file}")
        print(f"Открытый ключ сохранен в: {public_key_file}")

    def load_keys(self, private_key_file: str, public_key_file: str) -> Tuple[int, int]:
        with open(private_key_file, 'r') as f:
            x = int(f.read().strip())

        with open(public_key_file, 'r') as f:
            y = int(f.read().strip())

        print("Ключи DSA загружены")
        return x, y


def main():
    dsa = FIPS186Signature()

    domain_params = None
    keys = None

    while True:
        print("\n" + "=" * 60)
        print("=== Электронная подпись FIPS 186 (DSA) ===")
        print("1. Генерация доменных параметров")
        print("2. Генерация ключей")
        print("3. Подписание файла")
        print("4. Проверка подписи")
        print("5. Сохранение параметров и ключей")
        print("6. Загрузка параметров и ключей")
        print("7. Выход")
        print("=" * 60)

        choice = input("Выберите действие: ").strip()

        if choice == '1':
            try:
                print("\n--- Генерация доменных параметров DSA ---")
                L = input("Длина p в битах (по умолчанию 1024): ").strip()
                N = input("Длина q в битах (по умолчанию 160): ").strip()

                L = int(L) if L else 1024
                N = int(N) if N else 160

                domain_params = dsa.generate_domain_parameters(L, N)
                print("✓ Доменные параметры сгенерированы успешно!")

            except Exception as e:
                print(f"✗ Ошибка при генерации параметров: {e}")

        elif choice == '2':
            try:
                print("\n--- Генерация ключей DSA ---")
                if domain_params is None:
                    print("Сначала сгенерируйте доменные параметры!")
                    continue

                p, q, g = domain_params
                keys = dsa.generate_keys(p, q, g)
                print("✓ Ключи DSA сгенерированы успешно!")

            except Exception as e:
                print(f"✗ Ошибка при генерации ключей: {e}")

        elif choice == '3':
            try:
                print("\n--- Подписание файла DSA ---")
                if domain_params is None or keys is None:
                    print("Сначала сгенерируйте параметры и ключи!")
                    continue

                input_file = input("Путь к файлу для подписи: ").strip()
                p, q, g = domain_params
                x, y = keys

                sig_file = input("Файл для сохранения подписи (по умолчанию <filename>.dsa_sig): ").strip()
                if not sig_file:
                    sig_file = None

                dsa.sign_file(input_file, p, q, g, x, sig_file)

            except Exception as e:
                print(f"✗ Ошибка при подписании файла: {e}")

        elif choice == '4':
            try:
                print("\n--- Проверка подписи DSA ---")
                if domain_params is None:
                    print("Сначала сгенерируйте или загрузите доменные параметры!")
                    continue

                input_file = input("Путь к файлу для проверки: ").strip()
                sig_file = input("Файл с подписью (по умолчанию <filename>.dsa_sig): ").strip()
                if not sig_file:
                    sig_file = input_file + '.dsa_sig'

                public_key_file = input("Файл открытого ключа (по умолчанию dsa_public.key): ") or "dsa_public.key"

                p, q, g = domain_params

                with open(public_key_file, 'r') as f:
                    y = int(f.read().strip())

                result = dsa.verify_file(input_file, sig_file, p, q, g, y)
                if not result:
                    print("✗ Подпись DSA неверна!")

            except Exception as e:
                print(f"✗ Ошибка при проверке подписи: {e}")

        elif choice == '5':
            try:
                print("\n--- Сохранение параметров и ключей DSA ---")
                if domain_params is None or keys is None:
                    print("Сначала сгенерируйте параметры и ключи!")
                    continue

                p, q, g = domain_params
                x, y = keys

                params_file = input("Файл для доменных параметров (по умолчанию dsa_params.txt): ") or "dsa_params.txt"
                priv_file = input("Файл для секретного ключа (по умолчанию dsa_private.key): ") or "dsa_private.key"
                pub_file = input("Файл для открытого ключа (по умолчанию dsa_public.key): ") or "dsa_public.key"

                dsa.save_domain_params(p, q, g, params_file)
                dsa.save_keys(x, y, priv_file, pub_file)
                print("✓ Все параметры и ключи DSA сохранены!")

            except Exception as e:
                print(f"✗ Ошибка при сохранении: {e}")

        elif choice == '6':
            try:
                print("\n--- Загрузка параметров и ключей DSA ---")
                params_file = input("Файл доменных параметров (по умолчанию dsa_params.txt): ") or "dsa_params.txt"
                priv_file = input("Файл секретного ключа (по умолчанию dsa_private.key): ") or "dsa_private.key"
                pub_file = input("Файл открытого ключа (по умолчанию dsa_public.key): ") or "dsa_public.key"

                domain_params = dsa.load_domain_params(params_file)
                keys = dsa.load_keys(priv_file, pub_file)
                print("✓ Все параметры и ключи DSA загружены!")

            except Exception as e:
                print(f"✗ Ошибка при загрузке: {e}")

        elif choice == '7':
            print("Выход из программы")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()