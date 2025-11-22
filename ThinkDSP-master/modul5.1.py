import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter
# --- Параметры сигнала ---
duration = 5.0      # Длительность сигнала (>= 5 секунд)
framerate = 44100   # Частота дискретизации (Гц)
N = int(duration * framerate) # Количество отсчетов
# Время отсчетов
T = 1.0 / framerate
t = np.linspace(0.0, duration, N, endpoint=False)
time_fragment_samples = int(0.01 / T) # 0.01 секунды для временного представления
# Частоты 5 гармоник (Гц)
freq1 = 440
freq2 = 660
freq3 = 880
freq4 = 1200
freq5 = 1500
# Создание 5 гармоник и их микса (Шаг 1)
# y(t) = A1*sin(2*pi*f1*t) + ...
y = (1.0 * np.sin(2. * np.pi * freq1 * t) + 
     0.7 * np.sin(2. * np.pi * freq2 * t) +
     0.5 * np.sin(2. * np.pi * freq3 * t) +
     0.3 * np.sin(2. * np.pi * freq4 * t) +
     0.1 * np.sin(2. * np.pi * freq5 * t))
# Расчет спектра исходного сигнала
yf = fft(y)
xf = fftfreq(N, T)[:N//2]
amplitude_spectrum = 2.0/N * np.abs(yf[0:N//2])
# Функция для создания коэффициентов полосового фильтра Баттерворта
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs # Частота Найквиста
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
# Параметры фильтра для номера 15: Полосовой фильтр
# Цель: Оставить только 2 гармоники (660 Гц и 880 Гц)
low_cutoff = 550.0  # Отсекает 440 Гц
high_cutoff = 1000.0 # Отсекает 1200 Гц и 1500 Гц
order = 5            
# Применение фильтра
b, a = butter_bandpass(low_cutoff, high_cutoff, framerate, order=order)
y_filtered = lfilter(b, a, y)
# Расчет спектра отфильтрованного сигнала
yf_filtered = fft(y_filtered)
amplitude_spectrum_filtered = 2.0/N * np.abs(yf_filtered[0:N//2])
# Создаем общее окно (Figure) с сеткой 2x2 (4 подграфика)
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Сравнение сигнала до и после Полосовой фильтрации (для номера 15)', fontsize=16)
# --- ГРАФИК 1: Временное представление (Исходный сигнал) ---
ax1 = axs[0, 0]
ax1.plot(t[:time_fragment_samples], y[:time_fragment_samples]) 
ax1.set_title('1. Временное представление ИСХОДНОГО сигнала')
ax1.set_xlabel('Время (с)')
ax1.set_ylabel('Амплитуда')
ax1.grid(True)
# --- ГРАФИК 2: Частотное представление (Исходный сигнал) ---
ax2 = axs[0, 1]
ax2.plot(xf, amplitude_spectrum)
ax2.set_xlim(0, 2000)
ax2.set_title('2. Спектр ИСХОДНОГО сигнала (5 гармоник)')
ax2.set_xlabel('Частота (Гц)')
ax2.set_ylabel('Амплитуда')
ax2.grid(True)
# --- ГРАФИК 3: Временное представление (Отфильтрованный сигнал) ---
ax3 = axs[1, 0]
ax3.plot(t[:time_fragment_samples], y_filtered[:time_fragment_samples])
ax3.set_title('3. Временное представление ОТФИЛЬТРОВАННОГО сигнала')
ax3.set_xlabel('Время (с)')
ax3.set_ylabel('Амплитуда')
ax3.grid(True)
# --- ГРАФИК 4: Частотное представление (Отфильтрованный сигнал) ---
ax4 = axs[1, 1]
ax4.plot(xf, amplitude_spectrum_filtered)
ax4.set_xlim(0, 2000)
ax4.set_title('4. Спектр ОТФИЛЬТРОВАННОГО сигнала (2 гармоники)')
# Ожидается только 2 "палки" на 660 и 880 Гц
ax4.set_xlabel('Частота (Гц)')
ax4.set_ylabel('Амплитуда')
ax4.grid(True)
# Оптимизация расположения графиков и вывод
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()