import numpy as np
import matplotlib.pyplot as plt

# === Параметры сигнала ===
Fs = 1000          # частота дискретизации, Гц
T = 1.0            # общая длительность, сек
t = np.arange(0, T, 1/Fs)
N = len(t)

pulse_duration = 0.1       # длительность радиоимпульса, сек
pulse_samples = int(pulse_duration * Fs)

# === Случайное начало импульса ===
start_max = int(pulse_samples / 2)
pulse_start = np.random.randint(1, start_max)  # не равно нулю
pulse_end = pulse_start + pulse_samples

# === Формирование радиоимпульса ===
pulse = np.zeros_like(t)
pulse[pulse_start:pulse_end] = 1.0  # прямоугольный импульс амплитуды 1

# === Формирование гауссовского шума ===
noise_std = 0.3  # стандартное отклонение шума
noise = np.random.normal(0, noise_std, N)

# === Сумма импульса и шума ===
signal_sum = pulse + noise

# === Визуализация сигналов во времени ===
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(t, pulse)
plt.title("Радиоимпульс (без шума)")
plt.xlabel("Время, с")
plt.ylabel("Амплитуда")

plt.subplot(3, 1, 2)
plt.plot(t, noise)
plt.title("Гауссовский шум (без радиоимпульса)")
plt.xlabel("Время, с")
plt.ylabel("Амплитуда")

plt.subplot(3, 1, 3)
plt.plot(t, signal_sum)
plt.title("Сумма радиоимпульса и гауссовского шума")
plt.xlabel("Время, с")
plt.ylabel("Амплитуда")

plt.tight_layout()
plt.show()

# === (Необязательное) Амплитудные спектры ===
# Вычисляем спектры через БПФ
def amplitude_spectrum(x):
    X = np.fft.fft(x)
    freq = np.fft.fftfreq(len(x), 1/Fs)
    return freq[:N//2], np.abs(X[:N//2]) / N

freq, spec_pulse = amplitude_spectrum(pulse)
_, spec_noise = amplitude_spectrum(noise)
_, spec_sum = amplitude_spectrum(signal_sum)

plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(freq, spec_pulse)
plt.title("Амплитудный спектр радиоимпульса")
plt.xlabel("Частота, Гц")
plt.ylabel("|A(f)|")

plt.subplot(3, 1, 2)
plt.plot(freq, spec_noise)
plt.title("Амплитудный спектр гауссовского шума")
plt.xlabel("Частота, Гц")
plt.ylabel("|A(f)|")

plt.subplot(3, 1, 3)
plt.plot(freq, spec_sum)
plt.title("Амплитудный спектр суммы радиоимпульса и шума")
plt.xlabel("Частота, Гц")
plt.ylabel("|A(f)|")

plt.tight_layout()
plt.show()
