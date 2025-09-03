import random
from datetime import datetime
import logging

# ================================
# ЭТАП 1: Итератор колоды карт
# ================================
class CardDeck:
    suits = ["Бубей", "Червей", "Крести", "Пик"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Валет", "Дама", "Король", "Туз"]

    def __init__(self):
        self._cards = [f"{value} {suit}" for suit in self.suits for value in self.values]
        random.shuffle(self._cards)
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._cards):
            raise StopIteration
        card = self._cards[self._index]
        self._index += 1
        return card

# ================================
# ЭТАП 2: Собственное исключение
# ================================
class MyCustomError(Exception):
    """Исключение для проверки чисел"""
    pass

def check_number():
    try:
        x = int(input("Введите число меньше 10: "))
        if x >= 10:
            raise MyCustomError("Число слишком большое!")
        print(f"Вы ввели корректное число: {x}")
    except MyCustomError as e:
        print(f"Поймано исключение: {e}")
    except ValueError:
        print("Ошибка: нужно ввести целое число!")

# ================================
# ЭТАП 3: Класс array (как Pascal list)
# ================================
class array:
    def __init__(self):
        self._data = []

    def append(self, value):
        self._data.append(value)

    def remove(self, value):
        self._data.remove(value)

    def insert(self, index, value):
        self._data.insert(index, value)

    def pop(self, index=-1):
        return self._data.pop(index)

    def clear(self):
        self._data.clear()

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def __str__(self):
        return str(self._data)

    # Итератор для for
    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self._data):
            raise StopIteration
        value = self._data[self._index]
        self._index += 1
        return value

# ================================
# ЭТАП 4: Логирование запуска функции
# ================================
def log_current_time():
    logging.basicConfig(
        filename="my_log.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logging.info("Функция запущена")
    print("Дата и время логированы в файл my_log.log")

# ================================
# ЭТАП 5: Параметризованный декоратор logger
# ================================
def logger(log_file):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - Вызов {func.__name__}, args={args}, kwargs={kwargs}, результат={result}\n")
            return result
        return wrapper
    return decorator

@logger("func_log.txt")
def add(a, b):
    return a + b

# ================================
# Тестовый запуск всех этапов
# ================================
if __name__ == "__main__":
    # Этап 1: Колода карт
    print("=== ЭТАП 1: Перебор колоды карт (5 карт) ===")
    deck = CardDeck()
    for i, card in enumerate(deck):
        if i < 5:
            print(card)

    # Этап 2: Собственное исключение
    print("\n=== ЭТАП 2: Проверка собственного исключения ===")
    check_number()

    # Этап 3: Класс array
    print("\n=== ЭТАП 3: Класс array ===")
    arr = array()
    arr.append(10)
    arr.append(20)
    arr.append(30)
    print("Через print:", arr)
    print("Через for:")
    for item in arr:
        print(item)
    arr.insert(1, 15)
    print("После insert:", arr)
    arr.pop()
    print("После pop:", arr)
    arr.clear()
    print("После clear:", arr)

    # Этап 4: Логирование
    print("\n=== ЭТАП 4: Логирование ===")
    log_current_time()

    # Этап 5: Декоратор logger
    print("\n=== ЭТАП 5: Декоратор logger ===")
    add(5, 7)
    add(20, 30)
    print("Вызовы функции add логированы в файл func_log.txt")
