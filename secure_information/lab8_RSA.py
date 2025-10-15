import hashlib
import struct
import math
from typing import Tuple, List
from crypto_lib import CryptoUtils


class RSASignature:

    def __init__(self):
        self.utils = CryptoUtils()

    def generate_keys(self, bit_length: int = 1024):
        print("\n=== Генерация ключей для RSA подписи ===")

        # простые чисел
        lower_bound = 2 ** (bit_length // 2 - 1)
        upper_bound = 2 ** (bit_length // 2)

        print("Генерация простых чисел p и q...")
        p = self.utils.generate_large_prime(lower_bound, upper_bound)
        q = self.utils.generate_large_prime(lower_bound, upper_bound)

        while q == p:
            q = self.utils.generate_large_prime(lower_bound, upper_bound)

        n = p * q
        phi = (p - 1) * (q - 1)

        e = 65537
        if math.gcd(e, phi) != 1:
            e = self.utils.generate_coprime(phi)

        d = self.utils.mod_inverse(e, phi)

        print(f"Сгенерированные параметры:")
        print(f"p = {p}")
        print(f"q = {q}")
        print(f"n = p * q = {n}")
        print(f"φ(n) = (p-1)*(q-1) = {phi}")
        print(f"e (открытая экспонента) = {e}")
        print(f"d (секретная экспонента) = {d}")

        public_key = (n, e)
        private_key = (n, d)

        return public_key, private_key

    def calculate_hash(self, data: bytes, hash_algorithm: str = 'sha256') -> bytes:
        """хеш данных"""
        if hash_algorithm.lower() == 'sha256':
            return hashlib.sha256(data).digest()
        elif hash_algorithm.lower() == 'sha512':
            return hashlib.sha512(data).digest()
        elif hash_algorithm.lower() == 'sha384':
            return hashlib.sha384(data).digest()
        elif hash_algorithm.lower() == 'sha1':
            return hashlib.sha1(data).digest()
        elif hash_algorithm.lower() == 'md5':
            return hashlib.md5(data).digest()
        else:
            raise ValueError(f"Неподдерживаемый алгоритм хеширования: {hash_algorithm}")

    def sign_hash_byte_by_byte(self, hash_bytes: bytes, private_key: Tuple[int, int]) -> List[int]:
        """подпись хеша побайтово"""
        n, d = private_key
        signature = []

        for byte in hash_bytes:
            signed_byte = self.utils.mod_exp(byte, d, n)
            signature.append(signed_byte)

        return signature

    def verify_hash_byte_by_byte(self, hash_bytes: bytes, signature: List[int],
                                 public_key: Tuple[int, int]) -> bool:
        """Проверка хеша побайтово"""
        n, e = public_key

        if len(hash_bytes) != len(signature):
            return False

        for i, byte in enumerate(hash_bytes):
            recovered_byte = self.utils.mod_exp(signature[i], e, n) % 256

            if recovered_byte != byte:
                return False

        return True

    def sign_file(self, input_file: str, private_key: Tuple[int, int],
                  signature_file: str = None, hash_algorithm: str = 'sha256') -> str:
        """создание подписи"""
        print(f"\n=== Создание подписи для файла {input_file} ===")

        with open(input_file, 'rb') as f:
            data = f.read()

        print(f"Размер файла: {len(data)} байт")

        file_hash = self.calculate_hash(data, hash_algorithm)
        print(f"Хеш ({hash_algorithm}): {file_hash.hex()}")

        signature = self.sign_hash_byte_by_byte(file_hash, private_key)
        print(f"Создана подпись длиной {len(signature)} элементов")

        if signature_file is None:
            signature_file = input_file + '.sig'

        self.save_signature(signature_file, signature, hash_algorithm)
        print(f"Подпись сохранена в файл: {signature_file}")

        return signature_file

    def verify_file(self, input_file: str, signature_file: str,
                    public_key: Tuple[int, int]) -> bool:
        print(f"\n=== Проверка подписи для файла {input_file} ===")

        with open(input_file, 'rb') as f:
            data = f.read()

        print(f"Размер файла: {len(data)} байт")

        signature, hash_algorithm = self.load_signature(signature_file)
        print(f"Загружена подпись длиной {len(signature)} элементов")
        print(f"Алгоритм хеширования: {hash_algorithm}")

        file_hash = self.calculate_hash(data, hash_algorithm)
        print(f"Хеш ({hash_algorithm}): {file_hash.hex()}")

        is_valid = self.verify_hash_byte_by_byte(file_hash, signature, public_key)

        if is_valid:
            print("✓ Подпись ВЕРНА!")
        else:
            print("✗ Подпись НЕВЕРНА!")

        return is_valid

    def save_signature(self, signature_file: str, signature: List[int],
                       hash_algorithm: str):
        with open(signature_file, 'wb') as f:
            alg_bytes = hash_algorithm.ljust(32).encode('utf-8')[:32]
            f.write(alg_bytes)

            f.write(struct.pack('>I', len(signature)))

            for sig_element in signature:
                byte_length = (sig_element.bit_length() + 7) // 8
                if byte_length == 0:
                    byte_length = 1

                sig_bytes = sig_element.to_bytes(byte_length, 'big')
                f.write(struct.pack('>I', len(sig_bytes)))
                f.write(sig_bytes)

    def load_signature(self, signature_file: str) -> Tuple[List[int], str]:
        with open(signature_file, 'rb') as f:
            alg_bytes = f.read(32)
            hash_algorithm = alg_bytes.decode('utf-8').strip()

            num_elements = struct.unpack('>I', f.read(4))[0]

            signature = []
            for _ in range(num_elements):
                elem_length = struct.unpack('>I', f.read(4))[0]

                elem_bytes = f.read(elem_length)
                sig_element = int.from_bytes(elem_bytes, 'big')
                signature.append(sig_element)

        return signature, hash_algorithm

    def save_public_key(self, public_key: Tuple[int, int], key_file: str):
        n, e = public_key
        with open(key_file, 'w') as f:
            f.write(f"{n}\n{e}\n")
        print(f"Открытый ключ сохранен в: {key_file}")

    def save_private_key(self, private_key: Tuple[int, int], key_file: str):
        n, d = private_key
        with open(key_file, 'w') as f:
            f.write(f"{n}\n{d}\n")
        print(f"Закрытый ключ сохранен в: {key_file}")

    def load_public_key(self, key_file: str) -> Tuple[int, int]:
        with open(key_file, 'r') as f:
            n = int(f.readline().strip())
            e = int(f.readline().strip())
        print(f"Открытый ключ загружен из: {key_file}")
        return (n, e)

    def load_private_key(self, key_file: str) -> Tuple[int, int]:
        with open(key_file, 'r') as f:
            n = int(f.readline().strip())
            d = int(f.readline().strip())
        print(f"Закрытый ключ загружен из: {key_file}")
        return (n, d)


def main():
    rsa_sig = RSASignature()

    while True:
        print("\n" + "=" * 50)
        print("        СИСТЕМА ЭЛЕКТРОННОЙ ПОДПИСИ RSA")
        print("=" * 50)
        print("1. Генерация ключей")
        print("2. Создание подписи для файла")
        print("3. Проверка подписи файла")
        # print("4. Сохранение ключей в файлы")
        # print("5. Загрузка ключей из файлов")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == '1':
            # Генерация ключей
            try:
                bit_length = int(input("Длина ключа в битах (по умолчанию 1024): ") or "1024")
                public_key, private_key = rsa_sig.generate_keys(bit_length)
                print("✓ Ключи успешно сгенерированы!")
            except Exception as e:
                print(f"✗ Ошибка при генерации ключей: {e}")

        elif choice == '2':
            # Создание подписи
            try:
                if 'private_key' not in locals():
                    print("Сначала сгенерируйте ключи!")
                    continue

                input_file = input("Введите путь к файлу для подписи: ")
                hash_alg = input(
                    "Алгоритм хеширования (sha256/sha512/sha384/sha1/md5, по умолчанию sha256): ") or "sha256"
                sig_file = input("Введите путь для файла подписи (Enter для автоматического): ") or None

                signature_file = rsa_sig.sign_file(input_file, private_key, sig_file, hash_alg)
                print(f"✓ Файл успешно подписан! Подпись сохранена в: {signature_file}")

            except Exception as e:
                print(f"✗ Ошибка при создании подписи: {e}")

        elif choice == '3':
            # Проверка подписи
            try:
                if 'public_key' not in locals():
                    print("Сначала загрузите открытый ключ!")
                    continue

                input_file = input("Введите путь к файлу для проверки: ")
                sig_file = input("Введите путь к файлу подписи: ")

                is_valid = rsa_sig.verify_file(input_file, sig_file, public_key)

            except Exception as e:
                print(f"✗ Ошибка при проверке подписи: {e}")

        elif choice == '4':
            # Сохранение ключей
            try:
                if 'public_key' not in locals() or 'private_key' not in locals():
                    print("Сначала сгенерируйте ключи!")
                    continue

                pub_file = input("Введите путь для сохранения открытого ключа: ") or "public_key.pub"
                priv_file = input("Введите путь для сохранения закрытого ключа: ") or "private_key.prv"

                rsa_sig.save_public_key(public_key, pub_file)
                rsa_sig.save_private_key(private_key, priv_file)
                print("✓ Ключи успешно сохранены!")

            except Exception as e:
                print(f"✗ Ошибка при сохранении ключей: {e}")

        elif choice == '5':
            # Загрузка ключей
            try:
                key_type = input("Загрузить открытый или закрытый ключ? (pub/priv): ").strip().lower()

                if key_type == 'pub':
                    key_file = input("Введите путь к файлу открытого ключа: ")
                    public_key = rsa_sig.load_public_key(key_file)
                    print("✓ Открытый ключ загружен!")

                elif key_type == 'priv':
                    key_file = input("Введите путь к файлу закрытого ключа: ")
                    private_key = rsa_sig.load_private_key(key_file)
                    print("✓ Закрытый ключ загружен!")

                else:
                    print("Неверный тип ключа!")

            except Exception as e:
                print(f"✗ Ошибка при загрузке ключей: {e}")

        elif choice == '0':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()