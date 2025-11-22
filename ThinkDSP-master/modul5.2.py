# ==============================================================================
# ЗАДАНИЕ НА КОНТРОЛЬ: ПРАКТИКА 2 (Модуляция, Шум, Фильтрация)
# Код предназначен для запуска в VS Code
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter
import os
import sys

# --- Параметры ---
# !!! Убедитесь, что этот файл находится в той же папке, что и скрипт .py !!!
FILENAME = 'original_music.wav' 
CARRIER_FREQ = 15000 # Частота несущей для модуляции (Гц)
FILTER_ORDER = 5     # Порядок фильтра Баттерворта
FILE_LOADED = False

# --------------------------------------------------------------------------------
# ШАГ 1: Загрузка и анализ оригинального сигнала
# --------------------------------------------------------------------------------
try:
    framerate, data = wavfile.read(FILENAME)
    FILE_LOADED = True
except FileNotFoundError:
    print(f"ОШИБКА: Файл {FILENAME} не найден.")
    print(f"Пожалуйста, убедитесь, что файл лежит в текущем рабочем каталоге: {os.getcwd()}")
except ValueError:
    print("ОШИБКА: Не удалось прочитать WAV-файл. Проверьте формат файла.")

if not FILE_LOADED:
    # Если файл не загружен, выходим
    sys.exit("Выполнение остановлено из-за ошибки чтения файла.")


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

# Исходный спектр
amplitude_spectrum_original = get_spectrum(audio_data, N, T)


# --------------------------------------------------------------------------------
# ШАГ 2: Модуляция, Демодуляция с укороченным спектром
# --------------------------------------------------------------------------------

# 2.1. Укорочение спектра до полосы телефонного сигнала (300 Гц - 3400 Гц)

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

b_band, a_band = butter_bandpass(300, 3400, framerate, order=FILTER_ORDER)
y_reduced = lfilter(b_band, a_band, audio_data)


# 2.2. Амплитудная модуляция (AM)
carrier = np.cos(2. * np.pi * CARRIER_FREQ * t)
modulated_signal = y_reduced * carrier


# 2.3. Демодуляция (синхронная демодуляция)
demodulated_signal = modulated_signal * carrier

# Фильтрация ФНЧ для выделения исходного сигнала
b_low, a_low = butter(FILTER_ORDER, 4000 / (framerate * 0.5), btype='lowpass')
demodulated_signal_filtered = lfilter(b_low, a_low, demodulated_signal)

amplitude_spectrum_demod = get_spectrum(demodulated_signal_filtered, N, T)

# --------------------------------------------------------------------------------
# ШАГ 3: Добавление белого шума и повторение процесса
# --------------------------------------------------------------------------------
noise_level = 0.1 
noise = noise_level * np.random.normal(0, 1, N)
audio_data_noisy = audio_data + noise

# Повторение для зашумленного сигнала
y_reduced_noisy = lfilter(b_band, a_band, audio_data_noisy)
modulated_signal_noisy = y_reduced_noisy * carrier
demodulated_signal_noisy = modulated_signal_noisy * carrier
demodulated_signal_filtered_noisy = lfilter(b_low, a_low, demodulated_signal_noisy)

amplitude_spectrum_demod_noisy = get_spectrum(demodulated_signal_filtered_noisy, N, T)


# --------------------------------------------------------------------------------
# ШАГ 4: Построение графиков и выгрузка
# --------------------------------------------------------------------------------

# 4.1. Выгрузка получившегося файла (будет сохранен в той же папке, что и скрипт)
output_filename = 'demodulated_filtered_noisy_output.wav'
wavfile.write(output_filename, framerate, np.int16(demodulated_signal_filtered_noisy))
print(f"\nФайл '{output_filename}' успешно создан в папке проекта.")

# 4.2. Построение графиков (2x2)

fig, axs = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Задание 2: Сравнение исходного и демодулированного зашумленного сигнала', fontsize=16)

# График A: Спектр Оригинала
axs[0, 0].plot(xf, amplitude_spectrum_original)
axs[0, 0].set_title('A. Спектр ИСХОДНОГО музыкального файла')
axs[0, 0].set_xlabel('Частота (Гц)')
axs[0, 0].set_ylabel('Амплитуда')
axs[0, 0].set_xlim(0, framerate/2)
axs[0, 0].grid(True)
# 

# График B: Спектр Демодулированного и Отфильтрованного (БЕЗ ШУМА)
axs[0, 1].plot(xf, amplitude_spectrum_demod)
axs[0, 1].set_title('B. Спектр ДЕМОДУЛИРОВАННОГО сигнала (Укороченный спектр)')
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

# График D: Спектр Демодулированного и Отфильтрованного (С ШУМОМ)
axs[1, 1].plot(xf, amplitude_spectrum_demod_noisy)
axs[1, 1].set_title('D. Спектр ДЕМОДУЛИРОВАННОГО сигнала с ШУМОМ (после фильтрации)')
axs[1, 1].set_xlabel('Частота (Гц)')
axs[1, 1].set_ylabel('Амплитуда')
axs[1, 1].set_xlim(0, 5000)
axs[1, 1].grid(True)
# 

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()