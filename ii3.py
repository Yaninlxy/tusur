# Вариант 3 — MLP регрессор
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow.keras import layers, models, Input
import numpy as np

# Пример данных (замени на реальные)
X = np.random.rand(1000, 60)
y = np.random.rand(1000, 1)

# Модель MLP
model = models.Sequential([
    Input(shape=(60,)),
    layers.Dense(128, activation='relu'),
    layers.Dense(64, activation='relu'),
    layers.Dense(32, activation='relu'),
    layers.Dense(1)  # выход без активации (регрессия)
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])
model.summary()

# Обучение
model.fit(X, y, epochs=20, batch_size=32, validation_split=0.2)
