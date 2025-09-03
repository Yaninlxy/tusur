import logging
from datetime import datetime

# ---------------- Задание 1 ----------------
class CardDeck:
    suits = ["Червей", "Бубей", "Треф", "Пик"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Валет", "Дама", "Король", "Туз"]

    def __init__(self):
        self.cards = [f"{v} {s}" for s in self.suits for v in self.values]
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.cards):
            raise StopIteration
        card = self.cards[self.index]
        self.index += 1
        return card


# ---------------- Задание 2 ----------------
class MyCustomError(Exception):
    """Собственное исключение"""
    pass


def test_exception():
    try:
        raise MyCustomError("Это наше собственное исключение!")
    except MyCustomError as e:
        print(f"Обработано исключение: {e}")


# ---------------- Задание 3 ----------------
class array:
    def __init__(self, *args):
        self.data = list(args)

    def append(self, item):
        self.data.append(item)

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __len__(self):
        return len(self.data)

    def __repr__(self):
        return f"array({', '.join(map(str, self.data))})"


# ---------------- Задание 4 ----------------
def log_run():
    logging.basicConfig(filename="program.log", level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Функция log_run() была запущена")
    print("Лог записан в program.log")


# ---------------- Задание 5 ----------------
def logger(filename):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(filename, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} - Вызов {func.__name__} с аргументами {args}, {kwargs}. Результат: {result}\n")
            return result
        return wrapper
    return decorator


@logger("debug.log")
def add(a, b):
    return a + b


# ---------------- Меню ----------------
def menu():
    while True:
        print("\n--- МЕНЮ ---")
        print("1. Итератор колоды карт")
        print("2. Собственное исключение")
        print("3. Класс array (как в Pascal)")
        print("4. Логирование запуска функции")
        print("5. Декоратор logger")
        print("0. Выход")

        choice = input("Выберите пункт меню: ")

        if choice == "1":
            deck = CardDeck()
            print("Карты из колоды:")
            for card in deck:
                print(card)

        elif choice == "2":
            test_exception()

        elif choice == "3":
            arr = array(1, 2, 3)
            print("Создан массив:", arr)
            arr.append(4)
            print("После добавления:", arr)
            arr[1] = 10
            print("После изменения второго элемента:", arr)

        elif choice == "4":
            log_run()

        elif choice == "5":
            print("Вызов функции add(5, 7):", add(5, 7))
            print("Лог записан в debug.log")

        elif choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Неверный ввод, попробуйте снова.")


if __name__ == "__main__":
    menu()
