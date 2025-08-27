#!/usr/bin/env python3
"""
Решения тестовых задач по основам программирования на Python
Файл содержит интерактивное меню для демонстрации решений задач 1-5.
Запуск:
    python python_basics_tasks.py

(Можно запускать в локальной установке Python или в Google Colab — в Colab
замените вводы на жестко заданные значения или используйте интерактивные ячейки.)
"""

from typing import Any


def task1_is_even():
    s = input("Задача 1. Введите целое число: ").strip()
    try:
        n = int(s)
    except ValueError:
        print("Ошибка: введено не целое число.")
        return
    print("чётное" if n % 2 == 0 else "нечётное")


def task2_middle_of_three():
    print("Задача 2. Введите три числа (через пробел или по очереди):")
    parts = input().strip().split()
    nums = []
    if len(parts) >= 3:
        parts = parts[:3]
    while len(parts) < 3:
        parts.append(input(f"Введите число {len(parts)+1}: ").strip())
    try:
        nums = [float(x) for x in parts]
    except ValueError:
        print("Ошибка: введены нечисловые значения.")
        return
    # Найти среднее (медиану) из трёх
    a, b, c = nums
    middle = sorted([a, b, c])[1]
    # Если хотите вывести в том же типе, как вводили (int при целых):
    if all(x.is_integer() for x in nums):
        middle = int(middle)
    print("Среднее (медиана) из трёх чисел:", middle)


def task3_collections_demo():
    print("Задача 3. Демонстрация коллекций")
    # Пример наполнения
    lst = [1, 2, 3, 4, 5]
    tpl = ("яблоко", "банан", "вишня")
    st = {1.5, 2.75, 3.0}
    dct = {1: "один", 2: "два", 3: "три"}

    print("Список целых чисел:", lst)
    print("Кортеж строк:", tpl)
    print("Множество чисел с плавающей точкой:", st)
    print("Словарь (числа -> строки):", dct)

    # Слияние списка и множества: можно объединить как множество (union)
    merged_as_set = set(lst) | st
    print("Результат слияния списка и множества (как множество):", merged_as_set)

    # Преобразование списка во множество
    list_to_set = set(lst)
    print("Преобразование списка во множество:", list_to_set)


def func_varargs(*args):
    """Пример функции, принимающей произвольное количество позиционных аргументов"""
    print("Внутри func_varargs. Получено args:", args)
    return args


def func_varkwargs(**kwargs):
    """Пример функции, принимающей произвольное количество именованных аргументов"""
    print("Внутри func_varkwargs. Получено kwargs:", kwargs)
    return kwargs


def task4_args_kwargs_demo():
    print("Задача 4. Упаковка и распаковка, *args и **kwargs")
    print("Пример вызова func_varargs(1, 2, 3):")
    func_varargs(1, 2, 3)

    print("Пример вызова func_varkwargs(a=1, b=2):")
    func_varkwargs(a=1, b=2)

    print("Демонстрация упаковки/распаковки:")
    seq = [10, 20, 30]
    d = {"x": 100, "y": 200}
    print("seq =", seq)
    print("d =", d)
    print("Распаковка seq в func_varargs(*seq):")
    func_varargs(*seq)
    print("Распаковка d в func_varkwargs(**d):")
    func_varkwargs(**d)


def bytes_kb_conversion():
    print("Задача 5. Перевод килобайт <-> байты")
    print("Выберите операцию:")
    print("1) Килобайты -> Байты")
    print("2) Байты -> Килобайты")
    choice = input("Номер операции (1 или 2): ").strip()
    if choice not in ("1", "2"):
        print("Неверный выбор.")
        return
    val_s = input("Введите число: ").strip()
    try:
        val = float(val_s)
    except ValueError:
        print("Ошибка: введено не число.")
        return
    # Используем определение 1 KB = 1024 bytes
    factor = 1024
    if choice == "1":
        bytes_val = val * factor
        # Если исходное было целым и результат тоже целый — привести к int
        if val.is_integer():
            bytes_val = int(bytes_val)
        print(f"{val} KB = {bytes_val} bytes")
    else:
        kb_val = val / factor
        # Круглим до 6 знаков для читаемости
        print(f"{val} bytes = {round(kb_val, 6)} KB")


def main():
    while True:
        print("\nВыберите задачу (1-5) или 0 для выхода:")
        print("1 — чётное/нечётное")
        print("2 — среднее из трёх чисел")
        print("3 — коллекции (список, кортеж, множество, словарь)")
        print("4 — *args, **kwargs и упаковка/распаковка")
        print("5 — перевод KB <-> bytes")
        print("0 — выход")
        cmd = input("Ваш выбор: ").strip()
        if cmd == "0":
            print("Выход. Спасибо!")
            break
        elif cmd == "1":
            task1_is_even()
        elif cmd == "2":
            task2_middle_of_three()
        elif cmd == "3":
            task3_collections_demo()
        elif cmd == "4":
            task4_args_kwargs_demo()
        elif cmd == "5":
            bytes_kb_conversion()
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == '__main__':
    main()
