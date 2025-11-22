import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------
# 🔧 Параметры сигнала и шума
# ---------------------------------------------
A = 1.0          # Амплитуда сигнала, В
fc = 30e3       # Частота несущей, Гц
Fd = 10 * fc     # Частота дискретизации, Гц (теорема Котельникова с запасом)
dt = 1 / Fd      # Период дискретизации
ti = 2e-3        # Длительность импульса, с
t = np.arange(-ti, ti, dt)  # Временная шкала
fi0 = 0          # Начальная фаза
noise_power = 0.05  # Мощность шума

# ---------------------------------------------
# 🔹 Выбор типа огибающей
# ---------------------------------------------
# Возможные варианты: 'gaussian', 'triangular', 'rectangular'
pulse_type = "gaussian"  # 👈 можно поменять

# ---------------------------------------------
# Формирование огибающей в зависимости от типа
# ---------------------------------------------
if pulse_type == "gaussian":
    sigma = ti / 6
    envelope = np.exp(-t**2 / (2 * sigma**2))

elif pulse_type == "triangular":
    envelope = 1 - np.abs(t) / (ti / 2)
    envelope[envelope < 0] = 0  # обрезаем отрицательные значения

elif pulse_type == "rectangular":
    envelope = np.where(np.abs(t) <= ti / 2, 1, 0)

else:
    raise ValueError("Неверный тип сигнала. Используйте: 'gaussian', 'triangular' или 'rectangular'.")

# ---------------------------------------------
# 🔸 Формирование заполненного радиоимпульса
# ---------------------------------------------
signal = A * envelope * np.cos(2 * np.pi * fc * t + fi0)

# ---------------------------------------------
# 🔸 Добавляем гауссовский шум
# ---------------------------------------------
noise = np.sqrt(noise_power) * np.random.randn(len(t))
signal_with_noise = signal + noise

# ---------------------------------------------
# 🔸 Согласованный фильтр
# ---------------------------------------------
h = np.flip(signal)
filtered = np.convolve(signal_with_noise, h, mode='same') * dt

# ---------------------------------------------
# 📊 Построение временных графиков
# ---------------------------------------------
plt.figure(figsize=(10, 8))

# 1️⃣ Чистый сигнал
plt.subplot(3, 1, 1)
plt.plot(t * 1e3, signal, color='b')
plt.title(f'Заполненный радиоимпульс ({pulse_type})')
plt.ylabel('Амплитуда, В')
plt.grid(True)

# 2️⃣ Шум
plt.subplot(3, 1, 2)
plt.plot(t * 1e3, noise, color='gray')
plt.title('Гауссовский шум')
plt.ylabel('Амплитуда, В')
plt.grid(True)

# 3️⃣ Сумма и отклик фильтра
plt.subplot(3, 1, 3)
plt.plot(t * 1e3, signal_with_noise, color='k', linewidth=0.7, label='Сигнал + шум')
plt.plot(t * 1e3, filtered / np.max(np.abs(filtered)), color='r', linewidth=1.2, label='Отклик фильтра')
plt.title('Суммарный сигнал и отклик согласованного фильтра')
plt.xlabel('Время, мс')
plt.ylabel('Амплитуда, В')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# ---------------------------------------------
# ⚙️ Расчёт амплитудных спектров
# ---------------------------------------------
def amplitude_spectrum(x, Fd):
    N = len(x)
    spectrum = np.fft.fftshift(np.fft.fft(x))
    freq = np.fft.fftshift(np.fft.fftfreq(N, 1 / Fd))
    amplitude = np.abs(spectrum) / N
    return freq, amplitude

freq, amp_signal = amplitude_spectrum(signal, Fd)
_, amp_noise = amplitude_spectrum(noise, Fd)
_, amp_sum = amplitude_spectrum(signal_with_noise, Fd)

# ---------------------------------------------
# 📈 Графики амплитудных спектров
# ---------------------------------------------
plt.figure(figsize=(10, 8))

plt.subplot(3, 1, 1)
plt.plot(freq / 1e3, amp_signal, color='b')
plt.title(f'Амплитудный спектр: радиоимпульс ({pulse_type})')
plt.ylabel('|S(f)|')
plt.grid(True)

plt.subplot(3, 1, 2)
plt.plot(freq / 1e3, amp_noise, color='gray')
plt.title('Амплитудный спектр: гауссовский шум')
plt.ylabel('|N(f)|')
plt.grid(True)

plt.subplot(3, 1, 3)
plt.plot(freq / 1e3, amp_sum, color='r')
plt.title('Амплитудный спектр: сумма (сигнал + шум)')
plt.xlabel('Частота, кГц')
plt.ylabel('|S+N(f)|')
plt.grid(True)

plt.tight_layout()
plt.show()
