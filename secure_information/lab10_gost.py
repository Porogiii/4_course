import hashlib
import struct
import random
import math
from typing import Tuple, List, Optional
from crypto_lib import CryptoUtils


class GOSTSignature:

    def __init__(self):
        self.utils = CryptoUtils()

    def generate_common_params(self) -> Tuple[int, int, int]:
        print("Генерация общих параметров ГОСТ Р 34.10-94...")

        print("Генерация простого числа q (16 бит)...")
        q_lower = 2 ** 15
        q_upper = 2 ** 16 - 1
        q = self.utils.generate_prime(q_lower, q_upper)
        print(f"q = {q} (бит: {q.bit_length()})")

        print("Генерация простого числа p (31 бит)...")
        p_lower = 2 ** 30
        p_upper = 2 ** 31 - 1

        while True:
            b_min = p_lower // q
            b_max = p_upper // q
            b = random.randint(b_min, b_max)
            p_candidate = b * q + 1

            if p_lower <= p_candidate <= p_upper and self.utils.test_ferma(p_candidate):
                p = p_candidate
                break

        print(f"p = {p} (бит: {p.bit_length()})")
        print(f"b = {b}")
        print(f"Проверка: p = b*q + 1 = {b}*{q} + 1 = {b * q + 1}")

        print("Генерация числа a...")
        while True:
            g = random.randint(2, p - 2)
            a = self.utils.mod_exp(g, b, p)
            if a > 1:
                check = self.utils.mod_exp(a, q, p)
                if check == 1:
                    break

        print(f"g = {g}")
        print(f"a = g^b mod p = {g}^{b} mod {p} = {a}")
        print(f"Проверка: a^q mod p = {a}^{q} mod {p} = {check}")

        return p, q, a

    def generate_keys(self, p: int, q: int, a: int) -> Tuple[int, int]:

        print("\nГенерация ключевой пары...")

        x = random.randint(1, q - 1)

        y = self.utils.mod_exp(a, x, p)

        print(f"Секретный ключ x = {x}")
        print(f"Открытый ключ y = a^x mod p = {a}^{x} mod {p} = {y}")

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

    def sign(self, data: bytes, p: int, q: int, a: int, x: int) -> Tuple[int, int]:
        print("\nПодписание документа...")

        h = self.compute_hash(data, q)

        while True:
            k = random.randint(1, q - 1)

            r = self.utils.mod_exp(a, k, p) % q
            if r == 0:
                continue

            try:
                k_inv = self.utils.mod_inverse(k, q)
                s = (k * h + x * r) % q

                if s == 0:
                    continue

                break

            except ValueError:
                continue

        print(f"Случайное число k = {k}")
        print(f"r = (a^k mod p) mod q = ({a}^{k} mod {p}) mod {q} = {r}")
        print(f"s = (k*h + x*r) mod q = ({k}*{h} + {x}*{r}) mod {q} = {s}")

        return r, s

    def verify(self, data: bytes, signature: Tuple[int, int], p: int, q: int, a: int, y: int) -> bool:

        print("\nПроверка подписи...")

        r, s = signature

        h = self.compute_hash(data, q)

        if not (0 < r < q and 0 < s < q):
            print("Ошибка: r или s не в диапазоне (0, q)")
            return False

        print(f"Проверка: 0 < r={r} < q={q} - OK")
        print(f"Проверка: 0 < s={s} < q={q} - OK")

        try:
            h_inv = self.utils.mod_inverse(h, q)
            u1 = (s * h_inv) % q
            u2 = (-r * h_inv) % q

            print(f"h^(-1) mod q = {h_inv}")
            print(f"u1 = s * h^(-1) mod q = {s} * {h_inv} mod {q} = {u1}")
            print(f"u2 = -r * h^(-1) mod q = -{r} * {h_inv} mod {q} = {u2}")

            a_u1 = self.utils.mod_exp(a, u1, p)
            y_u2 = self.utils.mod_exp(y, u2, p)
            v = ((a_u1 * y_u2) % p) % q

            print(f"a^u1 mod p = {a}^{u1} mod {p} = {a_u1}")
            print(f"y^u2 mod p = {y}^{u2} mod {p} = {y_u2}")
            print(f"v = (a^u1 * y^u2 mod p) mod q = ({a_u1} * {y_u2} mod {p}) mod {q} = {v}")

            print(f"Проверка: v = {v}, r = {r}")
            if v == r:
                print("✓ Подпись верна!")
                return True
            else:
                print("✗ Подпись неверна!")
                return False

        except ValueError as e:
            print(f"Ошибка при вычислении обратного элемента: {e}")
            return False

    def sign_file(self, input_file: str, p: int, q: int, a: int, x: int,
                  signature_file: Optional[str] = None) -> str:

        print(f"Подписание файла: {input_file}")

        with open(input_file, 'rb') as f:
            data = f.read()

        r, s = self.sign(data, p, q, a, x)

        if signature_file is None:
            signature_file = input_file + '.gost_sig'

        self._save_signature(signature_file, r, s, p.bit_length())

        print(f"Файл успешно подписан. Подпись сохранена в: {signature_file}")
        return signature_file

    def verify_file(self, input_file: str, signature_file: str,
                    p: int, q: int, a: int, y: int) -> bool:

        print(f"Проверка подписи файла: {input_file}")

        with open(input_file, 'rb') as f:
            data = f.read()

        r, s = self._load_signature(signature_file, p.bit_length())

        return self.verify(data, (r, s), p, q, a, y)

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

    def save_common_params(self, p: int, q: int, a: int, filename: str):
        with open(filename, 'w') as f:
            f.write(f"{p}\n{q}\n{a}")

        print(f"Общие параметры сохранены в: {filename}")

    def load_common_params(self, filename: str) -> Tuple[int, int, int]:
        with open(filename, 'r') as f:
            lines = f.readlines()
            p = int(lines[0].strip())
            q = int(lines[1].strip())
            a = int(lines[2].strip())

        print("Общие параметры загружены")
        return p, q, a

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

        print("Ключи загружены")
        return x, y


def main():
    gost = GOSTSignature()

    common_params = None
    keys = None

    while True:
        print("\n" + "=" * 60)
        print("=== Электронная подпись ГОСТ Р 34.10-94 ===")
        print("1. Генерация общих параметров")
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
                print("\n--- Генерация общих параметров ---")
                common_params = gost.generate_common_params()
                p, q, a = common_params
                print("✓ Общие параметры сгенерированы успешно!")

            except Exception as e:
                print(f"✗ Ошибка при генерации параметров: {e}")

        elif choice == '2':
            try:
                print("\n--- Генерация ключей ---")
                if common_params is None:
                    print("Сначала сгенерируйте общие параметры!")
                    continue

                p, q, a = common_params
                keys = gost.generate_keys(p, q, a)
                print("✓ Ключи сгенерированы успешно!")

            except Exception as e:
                print(f"✗ Ошибка при генерации ключей: {e}")

        elif choice == '3':
            try:
                print("\n--- Подписание файла ---")
                if common_params is None or keys is None:
                    print("Сначала сгенерируйте параметры и ключи!")
                    continue

                input_file = input("Путь к файлу для подписи: ").strip()
                p, q, a = common_params
                x, y = keys

                sig_file = input("Файл для сохранения подписи (по умолчанию <filename>.gost_sig): ").strip()
                if not sig_file:
                    sig_file = None

                gost.sign_file(input_file, p, q, a, x, sig_file)

            except Exception as e:
                print(f"✗ Ошибка при подписании файла: {e}")

        elif choice == '4':
            try:
                print("\n--- Проверка подписи ---")
                if common_params is None:
                    print("Сначала сгенерируйте или загрузите общие параметры!")
                    continue

                input_file = input("Путь к файлу для проверки: ").strip()
                sig_file = input("Файл с подписью (по умолчанию <filename>.gost_sig): ").strip()
                if not sig_file:
                    sig_file = input_file + '.gost_sig'

                public_key_file = input("Файл открытого ключа (по умолчанию gost_public.key): ") or "gost_public.key"

                p, q, a = common_params

                with open(public_key_file, 'r') as f:
                    y = int(f.read().strip())

                result = gost.verify_file(input_file, sig_file, p, q, a, y)
                if not result:
                    print("✗ Подпись неверна!")

            except Exception as e:
                print(f"✗ Ошибка при проверке подписи: {e}")

        elif choice == '5':
            try:
                print("\n--- Сохранение параметров и ключей ---")
                if common_params is None or keys is None:
                    print("Сначала сгенерируйте параметры и ключи!")
                    continue

                p, q, a = common_params
                x, y = keys

                params_file = input("Файл для общих параметров (по умолчанию gost_params.txt): ") or "gost_params.txt"
                priv_file = input("Файл для секретного ключа (по умолчанию gost_private.key): ") or "gost_private.key"
                pub_file = input("Файл для открытого ключа (по умолчанию gost_public.key): ") or "gost_public.key"

                gost.save_common_params(p, q, a, params_file)
                gost.save_keys(x, y, priv_file, pub_file)
                print("✓ Все параметры и ключи сохранены!")

            except Exception as e:
                print(f"✗ Ошибка при сохранении: {e}")

        elif choice == '6':
            try:
                print("\n--- Загрузка параметров и ключей ---")
                params_file = input("Файл общих параметров (по умолчанию gost_params.txt): ") or "gost_params.txt"
                priv_file = input("Файл секретного ключа (по умолчанию gost_private.key): ") or "gost_private.key"
                pub_file = input("Файл открытого ключа (по умолчанию gost_public.key): ") or "gost_public.key"

                common_params = gost.load_common_params(params_file)
                keys = gost.load_keys(priv_file, pub_file)
                print("✓ Все параметры и ключи загружены!")

            except Exception as e:
                print(f"✗ Ошибка при загрузке: {e}")

        elif choice == '7':
            print("Выход из программы")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()