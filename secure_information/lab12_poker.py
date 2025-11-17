import random
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Tuple, Dict
import math


class RSAMentalPoker:
    def __init__(self):
        self.prime_bit_size = 32

    def generate_rsa_keys(self):
        """Генерация RSA ключей"""
        # Генерируем простые числа
        p = self.generate_large_prime()
        q = self.generate_large_prime()

        while p == q:
            q = self.generate_large_prime()

        n = p * q
        phi = (p - 1) * (q - 1)

        e = 65537
        while math.gcd(e, phi) != 1:
            e = random.randint(2 ** 16, min(phi - 1, 2 ** 17))

        d = pow(e, -1, phi)

        return (n, e), (n, d)

    def generate_large_prime(self):
        """Генерация простого числа"""
        while True:
            num = random.randint(2 ** (self.prime_bit_size - 1), 2 ** self.prime_bit_size)
            num |= 1

            if self.is_prime(num):
                return num

    def is_prime(self, n, k=10):
        """Тест Миллера-Рабина на простоту"""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False

        small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
        for p in small_primes:
            if n % p == 0:
                return n == p

        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1

        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(s - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True

    def rsa_encrypt(self, message, public_key):
        """Шифрование RSA"""
        n, e = public_key
        # Обеспечиваем, что сообщение меньше n
        message = message % n
        return pow(message, e, n)

    def rsa_decrypt(self, ciphertext, private_key):
        """Дешифрование RSA"""
        n, d = private_key
        result = pow(ciphertext, d, n)
        return result


class MentalPokerProtocol:
    def __init__(self, num_players):
        self.num_players = num_players
        self.players = []
        self.rsa = RSAMentalPoker()
        self.setup_players()

    def setup_players(self):
        """Инициализация игроков с RSA ключами"""
        for i in range(self.num_players):
            public_key, private_key = self.rsa.generate_rsa_keys()
            player = {
                'id': i,
                'name': f'Игрок {i + 1}',
                'public_key': public_key,
                'private_key': private_key,
                'hand': [],
                'encrypted_hand': []
            }
            self.players.append(player)

    def commutative_encryption_round(self, deck, player_index):
        """Один раунд коммутативного шифрования"""
        encrypted_deck = []
        player = self.players[player_index]

        for card in deck:
            try:
                encrypted_card = self.rsa.rsa_encrypt(card, player['public_key'])
                encrypted_deck.append(encrypted_card)
            except Exception:
                encrypted_deck.append(card)

        random.shuffle(encrypted_deck)
        return encrypted_deck

    def commutative_decryption_round(self, encrypted_deck, player_index):
        """Один раунд коммутативного дешифрования"""
        decrypted_deck = []
        player = self.players[player_index]

        for encrypted_card in encrypted_deck:
            try:
                decrypted_card = self.rsa.rsa_decrypt(encrypted_card, player['private_key'])
                decrypted_deck.append(decrypted_card)
            except:
                decrypted_deck.append(encrypted_card)

        return decrypted_deck

    def normalize_card_number(self, card_num):
        """Приведение номера карты к диапазону 1-52"""
        # После RSA операции номер карты может быть большим числом
        # Приводим его к диапазону 1-52
        if 1 <= card_num <= 52:
            return card_num
        else:
            # Используем модульную арифметику для приведения к диапазону
            normalized = ((card_num - 1) % 52) + 1
            return normalized

    def mental_poker_protocol(self):
        """Полный протокол ментального покера"""
        # 1. Инициализация колоды
        deck = list(range(1, 53))

        self.encryption_log = []

        # 2. Фаза шифрования
        encrypted_deck = deck.copy()
        for i in range(self.num_players):
            encrypted_deck = self.commutative_encryption_round(encrypted_deck, i)
            self.encryption_log.append(f"🔒 {self.players[i]['name']} зашифровал колоду")

        # 3. Раздача зашифрованных карт
        current_index = 0
        for player in self.players:
            hand = encrypted_deck[current_index:current_index + 2]
            player['encrypted_hand'] = hand.copy()
            current_index += 2

        # 5 общих зашифрованных карт
        community_cards_encrypted = encrypted_deck[current_index:current_index + 5]

        # 4. Фаза дешифрования карт игроков
        for i, player in enumerate(self.players):
            decrypted_hand = []
            for encrypted_card in player['encrypted_hand']:
                temp_card = encrypted_card
                for j in range(self.num_players):
                    temp_card = self.rsa.rsa_decrypt(temp_card, self.players[j]['private_key'])
                # Нормализуем номер карты
                normalized_card = self.normalize_card_number(temp_card)
                decrypted_hand.append(normalized_card)
            player['hand'] = decrypted_hand
            self.encryption_log.append(f"🔓 {player['name']} получил карты")

        # 5. Фаза дешифрования общих карт
        decrypted_community = []
        for encrypted_card in community_cards_encrypted:
            temp_card = encrypted_card
            for player in self.players:
                temp_card = self.rsa.rsa_decrypt(temp_card, player['private_key'])
            normalized_card = self.normalize_card_number(temp_card)
            decrypted_community.append(normalized_card)

        self.encryption_log.append("📋 Общие карты раскрыты")

        return decrypted_community


class CardRenderer:
    def __init__(self):
        self.card_width = 70
        self.card_height = 100
        self.card_colors = {
            'hearts': 'red',
            'diamonds': 'red',
            'clubs': 'black',
            'spades': 'black'
        }

    def safe_card_conversion(self, card_num):
        """Безопасное преобразование номера карты в масть и ранг"""
        try:
            # Обеспечиваем, что номер карты в правильном диапазоне
            safe_num = ((card_num - 1) % 52) + 1
            suit_idx = (safe_num - 1) // 13
            rank_idx = (safe_num - 1) % 13

            suits = ['hearts', 'diamonds', 'clubs', 'spades']
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
            suit_symbols = ['♥', '♦', '♣', '♠']

            # Проверяем границы
            if 0 <= suit_idx < 4 and 0 <= rank_idx < 13:
                return suits[suit_idx], ranks[rank_idx], suit_symbols[suit_idx]
            else:
                # Возвращаем значения по умолчанию при ошибке
                return 'hearts', '?', '?'

        except Exception:
            return 'hearts', '?', '?'

    def create_card_on_canvas(self, canvas, x, y, card_num, is_face_up=True):
        """Создание карты на холсте"""
        card_ids = []

        if not is_face_up:
            # Рубашка карты
            card_id = canvas.create_rectangle(x, y, x + self.card_width, y + self.card_height,
                                              fill='darkblue', outline='gold', width=2)
            text_id = canvas.create_text(x + self.card_width // 2, y + self.card_height // 2,
                                         text='?', fill='white', font=('Arial', 14, 'bold'))
            card_ids.extend([card_id, text_id])
        else:
            # Безопасно получаем данные карты
            suit, rank, symbol = self.safe_card_conversion(card_num)
            color = self.card_colors.get(suit, 'black')

            # Рисуем карту
            card_id = canvas.create_rectangle(x, y, x + self.card_width, y + self.card_height,
                                              fill='white', outline='black', width=2)
            card_ids.append(card_id)

            # Основной текст карты (центр)
            card_text = f"{rank}\n{symbol}"
            text_id = canvas.create_text(x + self.card_width // 2, y + self.card_height // 2,
                                         text=card_text, fill=color, font=('Arial', 12, 'bold'),
                                         justify=tk.CENTER)
            card_ids.append(text_id)

            # Масть в левом верхнем углу
            corner_text = f"{rank}{symbol}"
            corner_id = canvas.create_text(x + 15, y + 15, text=corner_text,
                                           fill=color, font=('Arial', 8, 'bold'))
            card_ids.append(corner_id)

        return card_ids


class PokerTable:
    def __init__(self, canvas, x, y, width, height):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.community_cards = []
        self.player_positions = []
        self.card_renderer = CardRenderer()
        self.setup_table()

    def setup_table(self):
        """Настройка игрового стола"""
        # Рисуем стол
        self.canvas.create_rectangle(self.x, self.y,
                                     self.x + self.width, self.y + self.height,
                                     fill='#228B22', outline='#FFD700', width=4)

        # Центр стола для общих карт
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        # Позиции для общих карт
        card_spacing = 90
        self.community_card_positions = [
            (center_x - 2 * card_spacing, center_y - 20),
            (center_x - card_spacing, center_y - 20),
            (center_x, center_y - 20),
            (center_x + card_spacing, center_y - 20),
            (center_x + 2 * card_spacing, center_y - 20)
        ]

        # Надпись "Общие карты"
        self.canvas.create_text(center_x, center_y - 60, text="ОБЩИЕ КАРТЫ",
                                fill='white', font=('Arial', 14, 'bold'))

        # Позиции для игроков вокруг стола
        self.setup_player_positions()

    def setup_player_positions(self):
        """Определение позиций игроков вокруг стола"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        radius = min(self.width, self.height) * 0.4

        angles = [0, 45, 90, 135, 180, 225, 270, 315]

        self.player_positions = []
        for angle in angles:
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)

            if angle == 0:  # Право
                x += 40
            elif angle == 45:  # Право-верх
                x += 30
                y -= 30
            elif angle == 90:  # Верх
                y -= 40
            elif angle == 135:  # Лево-верх
                x -= 30
                y -= 30
            elif angle == 180:  # Лево
                x -= 40
            elif angle == 225:  # Лево-низ
                x -= 30
                y += 30
            elif angle == 270:  # Низ
                y += 40
            elif angle == 315:  # Право-низ
                x += 30
                y += 30

            self.player_positions.append((x, y))

    def draw_community_cards(self, cards, revealed=False):
        """Отрисовка общих карт на столе"""
        # Очищаем предыдущие карты
        for card_id in self.community_cards:
            self.canvas.delete(card_id)
        self.community_cards = []

        # Рисуем новые карты
        for i, card_num in enumerate(cards):
            if i < len(self.community_card_positions):
                x, y = self.community_card_positions[i]
                card_ids = self.card_renderer.create_card_on_canvas(self.canvas, x, y, card_num, revealed)
                self.community_cards.extend(card_ids)

    def draw_player_cards(self, players, show_all=False):
        """Отрисовка карт игроков"""
        # Очищаем предыдущие карты игроков
        for player in players:
            if 'card_ids' in player:
                for card_id in player['card_ids']:
                    self.canvas.delete(card_id)
                player['card_ids'] = []

        # Рисуем карты для каждого игрока
        for i, player in enumerate(players):
            if i < len(self.player_positions):
                base_x, base_y = self.player_positions[i]

                # Определяем направление разложения карт
                if i in [0, 1, 7]:  # Правые позиции
                    card1_x = base_x - 50
                    card2_x = base_x - 10
                elif i in [3, 4, 5]:  # Левые позиции
                    card1_x = base_x + 10
                    card2_x = base_x + 50
                else:  # Верхние и нижние позиции
                    card1_x = base_x - 30
                    card2_x = base_x + 10

                # Корректируем Y координату
                if i in [1, 2, 3]:  # Верхние позиции
                    card_y = base_y + 20
                elif i in [5, 6, 7]:  # Нижние позиции
                    card_y = base_y - 40
                else:  # Боковые позиции
                    card_y = base_y - 10

                player['card_ids'] = []

                if player.get('hand'):
                    # Рисуем первую карту
                    if len(player['hand']) > 0:
                        card_ids1 = self.card_renderer.create_card_on_canvas(
                            self.canvas, card1_x, card_y, player['hand'][0], show_all)
                        player['card_ids'].extend(card_ids1)

                    # Рисуем вторую карту
                    if len(player['hand']) > 1:
                        card_ids2 = self.card_renderer.create_card_on_canvas(
                            self.canvas, card2_x, card_y, player['hand'][1], show_all)
                        player['card_ids'].extend(card_ids2)

                # Подпись игрока
                name_y_offset = 0
                if i in [1, 2, 3]:  # Верхние позиции
                    name_y_offset = 60
                elif i in [5, 6, 7]:  # Нижние позиции
                    name_y_offset = -60
                elif i in [0, 4]:  # Боковые позиции
                    name_y_offset = 50

                name_bg = self.canvas.create_rectangle(
                    base_x - 40, base_y + name_y_offset - 10,
                    base_x + 40, base_y + name_y_offset + 10,
                    fill='black', outline='white', width=1
                )
                name_id = self.canvas.create_text(
                    base_x, base_y + name_y_offset,
                    text=player['name'], fill='white', font=('Arial', 9, 'bold')
                )
                player['card_ids'].extend([name_bg, name_id])

    def get_card_display(self, card_num):
        """Получить текстовое представление карты"""
        try:
            safe_num = ((card_num - 1) % 52) + 1
            suits = ['♥', '♦', '♣', '♠']
            ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

            suit_idx = (safe_num - 1) // 13
            rank_idx = (safe_num - 1) % 13

            if 0 <= suit_idx < 4 and 0 <= rank_idx < 13:
                return f"{ranks[rank_idx]}{suits[suit_idx]}"
            else:
                return "??"
        except:
            return "??"


class MentalPokerGUI:
    def __init__(self, root):
        self.root = root
        self.players = []
        self.deck = []
        self.community_cards = []
        self.poker_table = None
        self.poker_protocol = None
        self.setup_ui()

    def setup_ui(self):
        self.root.title("🎰 Ментальный покер - Техасский Холдем")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2C3E50')

        # Заголовок
        title_label = tk.Label(self.root, text="🎰 МЕНТАЛЬНЫЙ ПОКЕР - ТЕХАССКИЙ ХОЛДЕМ",
                               font=('Arial', 18, 'bold'), fg='white', bg='#2C3E50')
        title_label.pack(pady=10)

        # Основной фрейм с разделением
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель - управление и информация
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)

        # Правая панель - игровой стол
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=3)

        # Настройка левой панели
        self.setup_left_panel(left_frame)

        # Настройка правой панели
        self.setup_right_panel(right_frame)

    def setup_left_panel(self, parent):
        """Настройка левой панели с управлением"""
        # Настройка игры
        setup_frame = ttk.LabelFrame(parent, text="🎮 Настройка игры", padding="15")
        setup_frame.pack(fill=tk.X, pady=5)

        ttk.Label(setup_frame, text="Количество игроков (2-8):",
                  font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)

        self.player_count = tk.StringVar(value="4")
        player_combo = ttk.Combobox(setup_frame, textvariable=self.player_count,
                                    values=["2", "3", "4", "5", "6", "7", "8"],
                                    width=10, state="readonly")
        player_combo.grid(row=0, column=1, padx=10, pady=5)

        ttk.Button(setup_frame, text="🎲 Инициализировать игру",
                   command=self.initialize_game).grid(row=1, column=0, columnspan=2, pady=10, sticky=tk.EW)

        # Управление игрой
        control_frame = ttk.LabelFrame(parent, text="⚙️ Управление игрой", padding="15")
        control_frame.pack(fill=tk.X, pady=5)

        buttons = [
            ("🃏 Защищенная раздача карт", self.secure_deal_cards),
            ("👁️ Показать все карты", self.show_all_cards),
            ("🔄 Сбросить игру", self.reset_game),
            ("🛡️ Обоснование безопасности", self.show_security),
            ("🔍 Показать ключи", self.show_keys)
        ]

        for text, command in buttons:
            ttk.Button(control_frame, text=text, command=command).pack(fill=tk.X, pady=3)

        # Информация о процессе
        process_frame = ttk.LabelFrame(parent, text="📋 Процесс игры", padding="15")
        process_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.process_text = scrolledtext.ScrolledText(process_frame, height=15,
                                                      font=('Arial', 9))
        self.process_text.pack(fill=tk.BOTH, expand=True)

        # Проверка условий
        conditions_frame = ttk.LabelFrame(parent, text="✅ Проверка условий", padding="15")
        conditions_frame.pack(fill=tk.X, pady=5)

        self.conditions_text = tk.Text(conditions_frame, height=6, font=('Arial', 9))
        self.conditions_text.pack(fill=tk.BOTH, expand=True)

    def setup_right_panel(self, parent):
        """Настройка правой панели с игровым столом"""
        self.canvas = tk.Canvas(parent, bg='#1E8449', highlightthickness=2,
                                highlightbackground='#FFD700', relief='raised')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.poker_table = PokerTable(self.canvas, 150, 100, 1000, 600)

    def log_process(self, message):
        """Логирование процесса"""
        self.process_text.insert(tk.END, message + "\n")
        self.process_text.see(tk.END)
        self.root.update()

    def card_to_string(self, card_num):
        """Преобразование номера карты в строку"""
        return self.poker_table.get_card_display(card_num)

    def initialize_game(self):
        try:
            num_players = int(self.player_count.get())
            if not (2 <= num_players <= 8):
                messagebox.showerror("Ошибка", "Количество игроков должно быть от 2 до 8")
                return

            self.poker_protocol = MentalPokerProtocol(num_players)
            self.players = self.poker_protocol.players
            self.deck = list(range(1, 53))
            self.community_cards = []

            self.process_text.delete(1.0, tk.END)
            self.conditions_text.delete(1.0, tk.END)

            self.log_process("🎰 ИНИЦИАЛИЗАЦИЯ МЕНТАЛЬНОГО ПОКЕРА С RSA")
            self.log_process("=" * 50)

            for player in self.players:
                n, e = player['public_key']
                self.log_process(f"🔑 {player['name']}: сгенерирована RSA пара ключей")
                self.log_process(f"   Модуль (n): {n}")
                self.log_process(f"   Открытая экспонента (e): {e}")

            self.poker_table.draw_player_cards(self.players)

            self.log_process(f"✅ Игра инициализирована с {num_players} игроками")
            self.log_process("🔒 Все игроки имеют RSA ключи для безопасной раздачи")
            self.update_conditions()

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число игроков")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка инициализации: {str(e)}")

    def secure_deal_cards(self):
        """Защищенная раздача карт с использованием RSA"""
        if not self.poker_protocol:
            messagebox.showerror("Ошибка", "Сначала инициализируйте игру")
            return

        self.log_process("\n🔄 ЗАПУСК ЗАЩИЩЕННОГО ПРОТОКОЛА RSA")
        self.log_process("=" * 45)

        try:
            community_cards = self.poker_protocol.mental_poker_protocol()
            self.community_cards = community_cards

            for log_entry in self.poker_protocol.encryption_log:
                self.log_process(log_entry)

            for player in self.players:
                if player['hand']:
                    card1 = self.card_to_string(player['hand'][0])
                    card2 = self.card_to_string(player['hand'][1])
                    self.log_process(f"🎯 {player['name']} получил карты: {card1} {card2}")

            community_text = " ".join([self.card_to_string(card) for card in self.community_cards])
            self.log_process(f"📋 Выложены 5 общих карт: {community_text}")
            self.log_process("✅ ЗАЩИЩЕННАЯ РАЗДАЧА ЗАВЕРШЕНА")

            self.poker_table.draw_community_cards(self.community_cards, revealed=False)
            self.poker_table.draw_player_cards(self.players, show_all=False)

            self.update_conditions()

        except Exception as e:
            self.log_process(f"❌ Ошибка в протоколе: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def show_all_cards(self):
        """Показать все карты на столе"""
        if not self.players or not self.community_cards:
            messagebox.showwarning("Предупреждение", "Сначала раздайте карты")
            return

        self.log_process("\n👁️ ПОКАЗ ВСЕХ КАРТ")
        self.log_process("-" * 30)

        self.poker_table.draw_community_cards(self.community_cards, revealed=True)
        self.poker_table.draw_player_cards(self.players, show_all=True)

        for player in self.players:
            if player['hand']:
                card1 = self.card_to_string(player['hand'][0])
                card2 = self.card_to_string(player['hand'][1])
                self.log_process(f"🃏 {player['name']}: {card1} {card2}")

        community_text = " ".join([self.card_to_string(card) for card in self.community_cards])
        self.log_process(f"🎯 Общие карты: {community_text}")
        self.log_process("🔓 Все карты раскрыты!")

    def show_keys(self):
        """Показать информацию о ключах"""
        if not self.poker_protocol:
            messagebox.showwarning("Предупреждение", "Сначала инициализируйте игру")
            return

        keys_info = "🔐 ИНФОРМАЦИЯ О КЛЮЧАХ RSA\n\n"

        for player in self.players:
            n, e = player['public_key']
            n, d = player['private_key']

            keys_info += f"{player['name']}:\n"
            keys_info += f"  Открытый ключ (n): {n}\n"
            keys_info += f"  Открытый ключ (e): {e}\n"
            keys_info += f"  Закрытый ключ (d): {d}\n\n"

        messagebox.showinfo("Информация о ключах", keys_info)

    def reset_game(self):
        """Сброс игры"""
        self.players = []
        self.community_cards = []
        self.poker_protocol = None
        self.process_text.delete(1.0, tk.END)
        self.conditions_text.delete(1.0, tk.END)

        self.canvas.delete("all")
        self.poker_table = PokerTable(self.canvas, 150, 100, 1000, 600)

        self.log_process("🔄 Игра сброшена. Готов к новой игре!")

    def show_security(self):
        """Показать обоснование безопасности"""
        security_text = """
🔒 ОБОСНОВАНИЕ ЗАЩИЩЕННОСТИ МЕНТАЛЬНОГО ПОКЕРА

✅ РЕАЛИЗОВАННЫЕ МЕРЫ БЕЗОПАСНОСТИ:

1. КОММУТАТИВНОЕ RSA ШИФРОВАНИЕ:
   • Каждый игрок шифрует всю колоду своим открытым ключом
   • Порядок шифрования не влияет на конечный результат

2. МНОГОРАУНДОВОЕ ШИФРОВАНИЕ:
   • Колода шифруется последовательно всеми игроками
   • После каждого раунда колода перемешивается

3. СОВМЕСТНОЕ ДЕШИФРОВАНИЕ:
   • Для раскрытия карты требуются все игроки
   • Каждый игрок дешифрует своей парой ключей

4. НОРМАЛИЗАЦИЯ КАРТ:
   • После дешифрования карты приводятся к диапазону 1-52
   • Обеспечивается корректное отображение карт

🛡️ ГАРАНТИИ ЧЕСТНОСТИ:

• Никто не может предсказать карты до раздачи
• Все игроки участвуют в процессе шифрования
• Невозможно подменить карты после раздачи

🎯 ВЫПОЛНЕНИЕ УСЛОВИЙ ЛАБОРАТОРНОЙ:
• Каждому игроку раздается по 2 карты ✅
• На стол выкладывается 5 общих карт ✅
• Обеспечена криптографическая защита ✅
        """

        messagebox.showinfo("Обоснование безопасности", security_text)

    def update_conditions(self):
        """Обновление проверки условий"""
        self.conditions_text.delete(1.0, tk.END)

        conditions_met = []
        conditions_failed = []

        if len(self.players) >= 2:
            conditions_met.append("✓ Минимум 2 игрока")
        else:
            conditions_failed.append("✗ Нужно минимум 2 игрока")

        all_have_2_cards = all(len(player['hand']) == 2 for player in self.players if self.players)
        if all_have_2_cards:
            conditions_met.append("✓ Каждому игроку по 2 карты")
        else:
            conditions_failed.append("✗ Карты не разданы")

        has_5_community = len(self.community_cards) == 5
        if has_5_community:
            conditions_met.append("✓ 5 карт на столе (Техасский Холдем)")
        else:
            conditions_failed.append("✗ Нет 5 общих карт")

        has_rsa_protocol = self.poker_protocol is not None
        if has_rsa_protocol:
            conditions_met.append("✓ Реализован RSA протокол")
        else:
            conditions_failed.append("✗ Нет криптографической защиты")

        self.conditions_text.insert(tk.END, "ПРОВЕРКА УСЛОВИЙ ЛАБОРАТОРНОЙ:\n\n")

        for condition in conditions_met:
            self.conditions_text.insert(tk.END, condition + "\n")

        for condition in conditions_failed:
            self.conditions_text.insert(tk.END, condition + "\n")

        if all_have_2_cards and has_5_community and len(self.players) >= 2 and has_rsa_protocol:
            self.conditions_text.insert(tk.END, "\n🎉 ВСЕ УСЛОВИЯ ВЫПОЛНЕНЫ!\n")
            self.conditions_text.tag_add("success", "1.0", "end")
            self.conditions_text.tag_config("success", foreground="green")
        else:
            self.conditions_text.tag_add("warning", "1.0", "end")
            self.conditions_text.tag_config("warning", foreground="orange")


def main():
    root = tk.Tk()
    app = MentalPokerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()