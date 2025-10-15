import hashlib
import struct
import random
import math
from typing import Tuple, List, Optional
from crypto_lib import CryptoUtils


class ElGamalSignature:

    def __init__(self):
        self.utils = CryptoUtils()

    def generate_keys(self, key_size: int = 1024) -> Tuple[Tuple[int, int, int], Tuple[int, int]]:
        print("Генерация ключей Эль-Гамаля...")

        lower_bound = 32500
        upper_bound = 65000

        print(f"Поиск простого числа в диапазоне [{lower_bound}, {upper_bound}]...")
        p = self.utils.generate_prime(lower_bound, upper_bound)

        print(f"Найдено простое число p = {p}")

        print("Поиск примитивного корня g...")
        g = self.utils.find_primitive_root(p)
        print(f"Найден примитивный корень g = {g}")

        x = random.randint(2, p - 2)

        y = self.utils.mod_exp(g, x, p)

        public_key = (p, g, y)
        private_key = (p, x)

        print(f"Параметры сгенерированы:")
        print(f"p = {p}")
        print(f"g = {g}")
        print(f"x (секретный) = {x}")
        print(f"y (открытый) = g^x mod p = {g}^{x} mod {p} = {y}")

        print(f"\nПроверка диапазона:")
        print(f"p = {p} (в диапазоне 32500-65000)")
        print(f"Размер p: {p.bit_length()} бит")

        return public_key, private_key

    def compute_hash(self, data: bytes) -> List[int]:

        hash_obj = hashlib.sha256()
        hash_obj.update(data)
        hash_bytes = hash_obj.digest()

        return list(hash_bytes)

    def sign_byte(self, m: int, private_key: Tuple[int, int]) -> Tuple[int, int]:

        p, x = private_key

        while True:
            k = random.randint(2, p - 2)
            if math.gcd(k, p - 1) == 1:
                break

        r = self.utils.mod_exp(self.utils.find_primitive_root(p), k, p)

        try:
            k_inv = self.utils.mod_inverse(k, p - 1)
            s = (k_inv * (m - x * r)) % (p - 1)

            if s < 0:
                s += (p - 1)

        except ValueError as e:
            print(f"Ошибка при вычислении обратного элемента: {e}")
            return self.sign_byte(m, private_key)

        return r, s

    def verify_byte(self, m: int, signature: Tuple[int, int], public_key: Tuple[int, int, int]) -> bool:

        p, g, y = public_key
        r, s = signature

        if r <= 0 or r >= p or s <= 0 or s >= p - 1:
            return False

        try:
            left_part = self.utils.mod_exp(g, m, p)
            right_part_part1 = self.utils.mod_exp(y, r, p)
            right_part_part2 = self.utils.mod_exp(r, s, p)
            right_part = (right_part_part1 * right_part_part2) % p

            return left_part == right_part
        except:
            return False

    def sign_file(self, input_file: str, private_key: Tuple[int, int],
                  signature_file: Optional[str] = None) -> str:

        print(f"Подписание файла: {input_file}")

        try:
            with open(input_file, 'rb') as f:
                data = f.read()

            hash_bytes = self.compute_hash(data)
            hash_hex = ''.join(f'{b:02x}' for b in hash_bytes)
            print(f"Хеш файла (SHA-256): {hash_hex}")
            print(f"Длина хеша: {len(hash_bytes)} байт")

            signatures = []
            print("Подписание байтов хеша...")
            for i, byte_val in enumerate(hash_bytes):
                r, s = self.sign_byte(byte_val, private_key)
                signatures.append((r, s))
                if i < 5:
                    print(f"  Байт {i}: значение={byte_val}, подпись=({r}, {s})")

            if signature_file is None:
                signature_file = input_file + '.sig'

            self._save_signature(signature_file, signatures, private_key[0])

            print(f"Файл успешно подписан. Подпись сохранена в: {signature_file}")
            return signature_file

        except Exception as e:
            print(f"Ошибка при подписании файла: {e}")
            raise

    def verify_file(self, input_file: str, signature_file: str,
                    public_key: Tuple[int, int, int]) -> bool:

        print(f"Проверка подписи файла: {input_file}")

        try:
            with open(input_file, 'rb') as f:
                data = f.read()

            hash_bytes = self.compute_hash(data)
            hash_hex = ''.join(f'{b:02x}' for b in hash_bytes)
            print(f"Хеш файла (SHA-256): {hash_hex}")

            signatures = self._load_signature(signature_file, public_key[0])
            print(f"Загружено подписей: {len(signatures)}")

            all_valid = True
            for i, byte_val in enumerate(hash_bytes):
                if i >= len(signatures):
                    print(f"Ошибка: для байта {i} нет подписи")
                    all_valid = False
                    continue

                is_valid = self.verify_byte(byte_val, signatures[i], public_key)
                if not is_valid:
                    print(f"Ошибка проверки подписи для байта {i}")
                    all_valid = False

            if all_valid:
                print("✓ Подпись верна! Все байты прошли проверку.")
            else:
                print("✗ Подпись неверна!")

            return all_valid

        except Exception as e:
            print(f"Ошибка при проверке подписи: {e}")
            return False

    def _save_signature(self, filename: str, signatures: List[Tuple[int, int]], p: int):
        with open(filename, 'wb') as f:
            f.write(struct.pack('>I', len(signatures)))

            for r, s in signatures:
                byte_size = (p.bit_length() + 7) // 8
                r_bytes = r.to_bytes(byte_size, 'big')
                s_bytes = s.to_bytes(byte_size, 'big')

                f.write(struct.pack('>I', byte_size))
                f.write(r_bytes)
                f.write(s_bytes)

    def _load_signature(self, filename: str, p: int) -> List[Tuple[int, int]]:
        signatures = []

        with open(filename, 'rb') as f:
            num_sigs = struct.unpack('>I', f.read(4))[0]

            for _ in range(num_sigs):
                byte_size = struct.unpack('>I', f.read(4))[0]

                r_bytes = f.read(byte_size)
                s_bytes = f.read(byte_size)

                r = int.from_bytes(r_bytes, 'big')
                s = int.from_bytes(s_bytes, 'big')

                signatures.append((r, s))

        return signatures

    def save_keys(self, public_key: Tuple[int, int, int], private_key: Tuple[int, int],
                  public_key_file: str, private_key_file: str):
        p, g, y = public_key
        p_priv, x = private_key

        with open(public_key_file, 'w') as f:
            f.write(f"{p}\n{g}\n{y}")

        with open(private_key_file, 'w') as f:
            f.write(f"{p_priv}\n{x}")

        print(f"Открытый ключ сохранен в: {public_key_file}")
        print(f"Закрытый ключ сохранен в: {private_key_file}")

    def load_keys(self, public_key_file: str, private_key_file: str) -> Tuple[Tuple[int, int, int], Tuple[int, int]]:

        with open(public_key_file, 'r') as f:
            lines = f.readlines()
            p = int(lines[0].strip())
            g = int(lines[1].strip())
            y = int(lines[2].strip())

        with open(private_key_file, 'r') as f:
            lines = f.readlines()
            p_priv = int(lines[0].strip())
            x = int(lines[1].strip())

        if p != p_priv:
            raise ValueError("Модули p в открытом и закрытом ключах не совпадают")

        public_key = (p, g, y)
        private_key = (p, x)

        print("Ключи успешно загружены")
        return public_key, private_key


def main():

    elgamal = ElGamalSignature()

    while True:
        print("=== Электронная подпись Эль-Гамаля ===")
        print("1. Генерация ключей")
        print("2. Подписание файла")
        print("3. Проверка подписи")
        print("4. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == '1':
            try:
                print("\n--- Генерация ключей ---")
                public_key, private_key = elgamal.generate_keys()

                pub_file = input("Файл для сохранения открытого ключа (по умолчанию public.key): ") or "public.key"
                priv_file = input("Файл для сохранения закрытого ключа (по умолчанию private.key): ") or "private.key"

                elgamal.save_keys(public_key, private_key, pub_file, priv_file)
                print("✓ Генерация ключей завершена успешно!")

            except Exception as e:
                print(f"✗ Ошибка при генерации ключей: {e}")

        elif choice == '2':
            try:
                print("\n--- Подписание файла ---")
                input_file = input("Путь к файлу для подписи: ").strip()
                priv_file = input("Файл закрытого ключа (по умолчанию private.key): ") or "private.key"
                pub_file = input("Файл открытого ключа (по умолчанию public.key): ") or "public.key"

                public_key, private_key = elgamal.load_keys(pub_file, priv_file)

                sig_file = input("Файл для сохранения подписи (по умолчанию <filename>.sig): ").strip()
                if not sig_file:
                    sig_file = None

                elgamal.sign_file(input_file, private_key, sig_file)

            except Exception as e:
                print(f"✗ Ошибка при подписании файла: {e}")

        elif choice == '3':
            try:
                print("\n--- Проверка подписи ---")
                input_file = input("Путь к файлу для проверки: ").strip()
                sig_file = input("Файл с подписью (по умолчанию <filename>.sig): ").strip()
                if not sig_file:
                    sig_file = input_file + '.sig'

                pub_file = input("Файл открытого ключа (по умолчанию public.key): ") or "public.key"

                with open(pub_file, 'r') as f:
                    lines = f.readlines()
                    p = int(lines[0].strip())
                    g = int(lines[1].strip())
                    y = int(lines[2].strip())

                public_key = (p, g, y)

                result = elgamal.verify_file(input_file, sig_file, public_key)
                if not result:
                    print("✗ Подпись неверна!")

            except Exception as e:
                print(f"✗ Ошибка при проверке подписи: {e}")

        elif choice == '4':
            print("Выход из программы")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()