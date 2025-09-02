import sys, os
sys.path.append(os.path.dirname(__file__))

from fibonacci import call_fib

if __name__ == "__main__":
    n = int(input("Введите номер числа Фибоначчи: "))
    call_fib(n)
