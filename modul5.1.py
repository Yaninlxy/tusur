from thinkdsp import SinSignal
import thinkplot
import matplotlib.pyplot as plt
import numpy as np

# ============================
# 1. Создание исходного сигнала
# ============================

freqs = [200, 350, 500, 750, 1200]
signals = [SinSignal(freq=f, amp=1) for f in freqs]

mix = sum(signals)
wave = mix.make_wave(duration=5, framerate=44100)

# ============================
# 2. Графики исходного сигнала
# ============================

wave.plot()
plt.title("Исходный сигнал — время")
plt.show()

spectrum = wave.make_spectrum()
spectrum.plot()
plt.title("Исходный сигнал — частоты")
plt.show()

# ============================
# 3. Фильтрация
# ============================

student_index = 1  # <-- ПОСТАВЬТЕ СВОЙ НОМЕР

kind = student_index % 3   # 1 — ФНЧ, 2 — ФВЧ, 0 — полосовой
spec2 = wave.make_spectrum()

if kind == 1:
    cutoff = 400
    for f in spec2.hs.index:
        if abs(f) > cutoff:
            spec2.hs[f] = 0

elif kind == 2:
    cutoff = 400
    for f in spec2.hs.index:
        if abs(f) < cutoff:
            spec2.hs[f] = 0

elif kind == 0:
    low, high = 300, 600
    for f in spec2.hs.index:
        if not (low <= abs(f) <= high):
            spec2.hs[f] = 0

filtered_wave = spec2.make_wave()

# ============================
# 4. Графики после фильтрации
# ============================

filtered_wave.plot()
plt.title("Фильтрованный сигнал — время")
plt.show()

spec2.plot()
plt.title("Фильтрованный сигнал — частоты")
plt.show()
