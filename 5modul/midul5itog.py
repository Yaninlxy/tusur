# ==============================================================================
# ЗАДАНИЕ НА КОНТРОЛЬ: ПРАКТИКА 2 (Модуляция, Шум, Фильтрация)
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter
import sys
import os

# --- Параметры ---
FILENAME = 'att.wav' # Используем предоставленный файл att.wav
CARRIER_FREQ = 15000 # Частота несущей для модуляции (Гц)
FILTER_ORDER = 5     # Порядок фильтра Баттерворта
FILE_LOADED = False

# --------------------------------------------------------------------------------
# ШАГ 1: Загрузка и анализ оригинального сигнала (att.wav)
# --------------------------------------------------------------------------------
try:
    # Загрузка файла
    framerate, data = wavfile.read(FILENAME)
    FILE_LOADED = True
except FileNotFoundError:
    print(f"ОШИБКА: Файл {FILENAME} не найден.")
    sys.exit("Выполнение остановлено.")
except ValueError:
    print("ОШИБКА: Не удалось прочитать WAV-файл. Проверьте его формат.")
    sys.exit("Выполнение остановлено.")

# Если аудио стерео (2 канала), берем только один канал
if data.ndim > 1:
    audio_data = data[:, 0]
else:
    audio_data = data

N = len(audio_data)
T = 1.0 / framerate
t = np.linspace(0.0, N * T, N, endpoint=False)
xf = fftfreq(N, T)[:N//2]

def get_spectrum(signal_data, N, T):
    """Вычисляет и возвращает амплитудный спектр."""
    yf = fft(signal_data)
    amplitude_spectrum = 2.0 / N * np.abs(yf[0:N//2])
    return amplitude_spectrum

# Исходный спектр (Шаг 2. Построить временное и частотное представление сигнала)
amplitude_spectrum_original = get_spectrum(audio_data, N, T)

# --------------------------------------------------------------------------------
# ШАГ 2: Укорочение спектра, Модуляция и Демодуляция (без шума)
# --------------------------------------------------------------------------------

# Функция для создания коэффициентов полосового фильтра Баттерворта
def butter_bandpass(lowcut, highcut, fs, order=FILTER_ORDER):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

# 2.1. Укорочение спектра до полосы телефонного сигнала (300 Гц - 3400 Гц) [cite: 4]
b_band, a_band = butter_bandpass(300, 3400, framerate, order=FILTER_ORDER)
y_reduced = lfilter(b_band, a_band, audio_data)

# 2.2. Амплитудная модуляция (AM) [cite: 5]
carrier = np.cos(2. * np.pi * CARRIER_FREQ * t)
modulated_signal = y_reduced * carrier

# 2.3. Демодуляция (синхронная демодуляция) [cite: 8]
demodulated_signal = modulated_signal * carrier

# Фильтрация ФНЧ (для выделения сигнала после демодуляции) [cite: 10]
b_low, a_low = butter(FILTER_ORDER, 4000 / (framerate * 0.5), btype='lowpass')
demodulated_signal_filtered = lfilter(b_low, a_low, demodulated_signal)

amplitude_spectrum_demod = get_spectrum(demodulated_signal_filtered, N, T)

# --------------------------------------------------------------------------------
# ШАГ 3: Добавление белого шума и повторение процесса (Шаги 2-6) [cite: 152, 153]
# --------------------------------------------------------------------------------
noise_level = 0.1 # Уровень шума
noise = noise_level * np.random.normal(0, 1, N)
audio_data_noisy = audio_data + noise

# Повторение: Укорочение спектра зашумленного сигнала
y_reduced_noisy = lfilter(b_band, a_band, audio_data_noisy)

# Повторение: Модуляция
modulated_signal_noisy = y_reduced_noisy * carrier

# Повторение: Демодуляция
demodulated_signal_noisy = modulated_signal_noisy * carrier

# Повторение: Фильтрация (для выделения демодулированного сигнала)
demodulated_signal_filtered_noisy = lfilter(b_low, a_low, demodulated_signal_noisy)

amplitude_spectrum_demod_noisy = get_spectrum(demodulated_signal_filtered_noisy, N, T)


# --------------------------------------------------------------------------------
# ШАГ 4: Построение графиков и выгрузка
# --------------------------------------------------------------------------------

# 4.1. Выгрузка получившегося файла [cite: 12]
output_filename = 'demodulated_filtered_noisy_output.wav'
# Масштабируем до 16-битного формата для записи в wav
wavfile.write(output_filename, framerate, np.int16(demodulated_signal_filtered_noisy / np.max(np.abs(demodulated_signal_filtered_noisy)) * 32767))
print(f"Файл '{output_filename}' успешно создан и готов к выгрузке/прослушиванию.")

# 4.2. Построение графиков (2x2)

fig, axs = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Задание на контроль (Практика 2): Модуляция, Шум и Фильтрация', fontsize=16)

# График A: Спектр Оригинала [cite: 3]
axs[0, 0].plot(xf, amplitude_spectrum_original)
axs[0, 0].set_title('A. Спектр ИСХОДНОГО файла (att.wav)')
axs[0, 0].set_xlabel('Частота (Гц)')
axs[0, 0].set_ylabel('Амплитуда')
axs[0, 0].set_xlim(0, framerate/2)
axs[0, 0].grid(True)
# 
# График B: Спектр Демодулированного и Отфильтрованного (БЕЗ ШУМА) [cite: 9, 11]
axs[0, 1].plot(xf, amplitude_spectrum_demod)
axs[0, 1].set_title('B. Спектр ДЕМОДУЛИРОВАННОГО сигнала (Укороченный спектр, чистый)')
axs[0, 1].set_xlabel('Частота (Гц)')
axs[0, 1].set_ylabel('Амплитуда')
axs[0, 1].set_xlim(0, 5000) 
axs[0, 1].grid(True)
# 
# График C: Временное представление (Демодулированный + Шум)
time_fragment_samples_demod = int(0.02 / T) 
axs[1, 0].plot(t[:time_fragment_samples_demod], demodulated_signal_filtered_noisy[:time_fragment_samples_demod])
axs[1, 0].set_title('C. Временное представление ДЕМОДУЛИРОВАННОГО сигнала с ШУМОМ')
axs[1, 0].set_xlabel('Время (с)')
axs[1, 0].set_ylabel('Амплитуда')
axs[1, 0].grid(True)

# График D: Спектр Демодулированного и Отфильтрованного (С ШУМОМ) [cite: 11, 150]
axs[1, 1].plot(xf, amplitude_spectrum_demod_noisy)
axs[1, 1].set_title('D. Спектр ДЕМОДУЛИРОВАННОГО сигнала с ШУМОМ (после фильтрации)')
axs[1, 1].set_xlabel('Частота (Гц)')
axs[1, 1].set_ylabel('Амплитуда')
axs[1, 1].set_xlim(0, 5000)
axs[1, 1].grid(True)
# 
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()