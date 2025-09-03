import tkinter as tk
from tkinter import messagebox


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Калькулятор")
        self.geometry("300x400")
        self.resizable(False, False)

        self.expression = ""

        # Поле ввода
        self.entry = tk.Entry(self, font=("Arial", 18), bd=10, relief="sunken", justify="right")
        self.entry.grid(row=0, column=0, columnspan=4, sticky="nsew")

        # Кнопки
        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
            ("C", 5, 0, 4)  # кнопка очистки на всю строку
        ]

        for btn in buttons:
            if len(btn) == 3:
                text, row, col = btn
                colspan = 1
            else:
                text, row, col, colspan = btn

            action = (lambda x=text: self.on_button_click(x))
            tk.Button(self, text=text, font=("Arial", 16), command=action)\
                .grid(row=row, column=col, columnspan=colspan, sticky="nsew", padx=3, pady=3)

        # Настройка сетки
        for i in range(6):
            self.rowconfigure(i, weight=1)
        for j in range(4):
            self.columnconfigure(j, weight=1)

    def on_button_click(self, char):
        if char == "=":
            try:
                result = str(eval(self.expression))
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, result)
                self.expression = result
            except Exception:
                messagebox.showerror("Ошибка", "Неверное выражение")
                self.expression = ""
                self.entry.delete(0, tk.END)
        elif char == "C":
            self.expression = ""
            self.entry.delete(0, tk.END)
        else:
            self.expression += str(char)
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, self.expression)


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
