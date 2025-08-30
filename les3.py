# # Задание 1
# n = input("Введите натуральное число: ").strip()

# last_digit = n[-1]

# count_4 = n.count("4")
# count_last_digit = n.count(last_digit)
# count_even = sum(1 for ch in n if int(ch) % 2 == 0)
# sum_gt5 = sum(int(ch) for ch in n if int(ch) > 5)
# count_0_5 = sum(1 for ch in n if ch in ("0", "5"))

# prod_gt7 = 1
# found = False
# for ch in n:
#     if int(ch) > 7:
#         prod_gt7 *= int(ch)
#         found = True
# prod_gt7 = prod_gt7 if found else "Нет цифр > 7"

# print("количество цифр 4:", count_4)
# print("количество последней цифры:", count_last_digit)
# print("количество чётных цифр:", count_even)
# print("сумма цифр > 5:", sum_gt5)
# print("количество цифр 0 и 5:", count_0_5)
# print("произведение цифр > 7:", prod_gt7)

# # Задание 2
# a = int(input("Введите a (0 ≤ a ≤ 50): "))
# n = int(input("Введите n (1 ≤ n ≤ 100): "))
# a2 = int(input("Введите a для суммы квадратов: "))
# b2 = int(input("Введите b (b ≥ a): "))

# sum_cubes = sum(x ** 3 for x in range(20, 41))
# sum_squares_a50 = sum(x ** 2 for x in range(a, 51))
# sum_squares_1n = sum(x ** 2 for x in range(1, n + 1))
# sum_squares_ab = sum(x ** 2 for x in range(a2, b2 + 1))

# print("a) Сумма кубов от 20 до 40:", sum_cubes)
# print("б) Сумма квадратов от a до 50:", sum_squares_a50)
# print("в) Сумма квадратов от 1 до n:", sum_squares_1n)
# print("г) Сумма квадратов от a до b:", sum_squares_ab)
# # Задание 3
# a = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
# res = [x for x in a if x < 5]
# print("Элементы списка меньше 5:", res)
# # Задание 4
# a = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
# b = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
# res = list(set(a) & set(b))
# print("Общие элементы:", res)
# # Задание 5
# class Soda:
#     def __init__(self, additive=None):
#         self.additive = additive if isinstance(additive, str) else None

#     def show_my_drink(self):
#         if self.additive:
#             print(f"Газировка и {self.additive}")
#         else:
#             print("Обычная газировка")

# add = input("Введите добавку (или оставьте пустым): ").strip()
# drink = Soda(add if add else None)
# drink.show_my_drink()
# # Задание 6
# s = input("Введите строку: ").strip()
# first = s.split()[0]
# print("Первое слово:", first)
# Задание 7
def password_check(password: str) -> bool:
    return len(password) > 6

pw = input("Введите пароль: ").strip()
print("Пароль корректный?", password_check(pw))
