# Вариант 2 — CNN для классификации кошек и собак
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
from tensorflow.keras import layers, models, Input
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Модель CNN
model = models.Sequential([
    Input(shape=(150,150,3)),
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Conv2D(64, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Conv2D(128, (3,3), activation='relu'),
    layers.MaxPooling2D(2,2),
    layers.Flatten(),
    layers.Dense(512, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

model.summary()

# Подготовка данных (пример)
train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_gen = train_datagen.flow_from_directory(
    '/content/dataset/train',
    target_size=(150,150),
    batch_size=32,
    class_mode='binary',
    subset='training')

val_gen = train_datagen.flow_from_directory(
    '/content/dataset/train',
    target_size=(150,150),
    batch_size=32,
    class_mode='binary',
    subset='validation')

# Обучение
model.fit(train_gen, validation_data=val_gen, epochs=10)
