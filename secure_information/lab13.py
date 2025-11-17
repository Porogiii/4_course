import random
import hashlib
import json
from typing import Tuple, Dict, Any


class BlindSignatureSystem:
    """Система слепой подписи для анонимного голосования"""

    def __init__(self, p: int = None, g: int = None, q: int = None):
        """Инициализация системы с параметрами безопасности"""
        if p is None:
            # Используем стандартные параметры для простоты
            self.p = 23  # простое число
            self.g = 5  # генератор
            self.q = 11  # порядок подгруппы
        else:
            self.p = p
            self.g = g
            self.q = q

        # Закрытый ключ сервера
        self.server_private_key = random.randint(1, self.q - 1)
        # Открытый ключ сервера
        self.server_public_key = pow(self.g, self.server_private_key, self.p)

        print(f"Инициализирована система слепой подписи:")
        print(f"p = {self.p}, g = {self.g}, q = {self.q}")
        print(f"Открытый ключ сервера: {self.server_public_key}")
        print(f"Закрытый ключ сервера: {self.server_private_key}\n")


class Client:
    """Клиентская часть системы голосования"""

    def __init__(self, system: BlindSignatureSystem):
        self.system = system
        self.vote_options = {1: "Да", 2: "Нет", 3: "Воздержался"}

    def create_blinded_vote(self, vote_choice: int) -> Tuple[int, int, int]:
        """Создание ослепленного бюллетеня"""
        if vote_choice not in self.vote_options:
            raise ValueError("Неверный выбор голоса")

        # Преобразуем голос в число
        vote_number = vote_choice

        # Генерируем случайное число для ослепления
        k = random.randint(1, self.system.q - 1)

        # Вычисляем ослепленный бюллетень
        blinded_vote = (vote_number * pow(self.system.g, k, self.system.p)) % self.system.p

        print(f"Клиент: Создание ослепленного бюллетеня")
        print(f"Выбор: {self.vote_options[vote_choice]} ({vote_number})")
        print(f"Случайное число k = {k}")
        print(f"Ослепленный бюллетень: {blinded_vote}")

        return blinded_vote, k, vote_number

    def unblind_signature(self, blinded_signature: int, k: int) -> int:
        """Снятие ослепления с подписи"""
        # Вычисляем обратный элемент для k
        k_inv = pow(k, -1, self.system.q)

        # Снимаем ослепление
        signature = (blinded_signature * pow(self.system.server_public_key, -k_inv, self.system.p)) % self.system.p

        print(f"Клиент: Снятие ослепления")
        print(f"Ослепленная подпись: {blinded_signature}")
        print(f"Обратный элемент k: {k_inv}")
        print(f"Итоговая подпись: {signature}")

        return signature

    def create_final_ballot(self, vote_number: int, signature: int) -> Dict[str, Any]:
        """Создание финального бюллетеня"""
        ballot = {
            'vote': vote_number,
            'signature': signature,
            'public_key': self.system.server_public_key
        }

        print(f"Клиент: Финальный бюллетень создан")
        print(f"Голос: {self.vote_options[vote_number]} ({vote_number})")
        print(f"Подпись: {signature}")

        return ballot


class Server:
    """Серверная часть системы голосования"""

    def __init__(self, system: BlindSignatureSystem):
        self.system = system
        self.received_ballots = []
        self.vote_options = {1: "Да", 2: "Нет", 3: "Воздержался"}

    def sign_blinded_vote(self, blinded_vote: int) -> int:
        """Подписание ослепленного бюллетеня"""
        # Сервер подписывает ослепленный бюллетень своим закрытым ключом
        blinded_signature = pow(blinded_vote, self.system.server_private_key, self.system.p)

        print(f"Сервер: Подписание ослепленного бюллетеня")
        print(f"Ослепленный бюллетень: {blinded_vote}")
        print(f"Закрытый ключ: {self.system.server_private_key}")
        print(f"Ослепленная подпись: {blinded_signature}")

        return blinded_signature

    def verify_ballot(self, ballot: Dict[str, Any]) -> bool:
        """Проверка корректности бюллетеня"""
        vote = ballot['vote']
        signature = ballot['signature']
        public_key = ballot['public_key']

        print(f"Сервер: Проверка бюллетеня")
        print(f"Голос: {self.vote_options[vote]} ({vote})")
        print(f"Подпись: {signature}")

        # Проверяем подпись
        left_side = pow(self.system.g, signature, self.system.p)
        right_side = (vote * pow(public_key, signature, self.system.p)) % self.system.p

        is_valid = left_side == right_side

        print(f"Проверка подписи:")
        print(f"Левая часть: {left_side}")
        print(f"Правая часть: {right_side}")
        print(f"Подпись {'валидна' if is_valid else 'невалидна'}")

        if is_valid:
            self.received_ballots.append(ballot)
            print("Бюллетень принят!")
        else:
            print("Бюллетень отклонен!")

        return is_valid

    def show_results(self):
        """Показать результаты голосования"""
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ ГОЛОСОВАНИЯ")
        print("=" * 50)

        vote_counts = {1: 0, 2: 0, 3: 0}

        for ballot in self.received_ballots:
            vote_counts[ballot['vote']] += 1

        for vote_num, count in vote_counts.items():
            print(f"{self.vote_options[vote_num]}: {count} голосов")

        total_votes = len(self.received_ballots)
        print(f"\nВсего голосов: {total_votes}")


def main():
    """Основная функция демонстрации системы"""
    print("СИСТЕМА АНОНИМНОГО ГОЛОСОВАНИЯ СО СЛЕПОЙ ПОДПИСЬЮ")
    print("=" * 60)

    # Инициализация системы
    system = BlindSignatureSystem()
    client = Client(system)
    server = Server(system)

    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ:")
        print("1. Проголосовать")
        print("2. Показать результаты")
        print("3. Выйти")

        choice = input("Выберите действие: ")

        if choice == "1":
            # Процесс голосования
            print("\nВЫБОР ГОЛОСА:")
            print("1 - Да")
            print("2 - Нет")
            print("3 - Воздержался")

            try:
                vote_choice = int(input("Ваш выбор: "))

                if vote_choice not in [1, 2, 3]:
                    print("Неверный выбор!")
                    continue

                print("\n" + "-" * 30)
                print("ЭТАП 1: Клиент создает ослепленный бюллетень")
                print("-" * 30)
                blinded_vote, k, vote_number = client.create_blinded_vote(vote_choice)

                print("\n" + "-" * 30)
                print("ЭТАП 2: Сервер подписывает ослепленный бюллетень")
                print("-" * 30)
                blinded_signature = server.sign_blinded_vote(blinded_vote)

                print("\n" + "-" * 30)
                print("ЭТАП 3: Клиент снимает ослепление")
                print("-" * 30)
                signature = client.unblind_signature(blinded_signature, k)

                print("\n" + "-" * 30)
                print("ЭТАП 4: Клиент формирует финальный бюллетень")
                print("-" * 30)
                ballot = client.create_final_ballot(vote_number, signature)

                print("\n" + "-" * 30)
                print("ЭТАП 5: Сервер проверяет бюллетень")
                print("-" * 30)
                server.verify_ballot(ballot)

            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == "2":
            server.show_results()

        elif choice == "3":
            print("Выход из системы...")
            break

        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    main()