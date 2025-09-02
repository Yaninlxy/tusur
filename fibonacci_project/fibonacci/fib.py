def fibonacci(n: int) -> int:
    if n <= 0:
        raise ValueError("n должно быть положительным числом")
    elif n == 1 or n == 2:
        return 1
    a, b = 1, 1
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b
