#!/usr/bin/env python3
"""
Скрипт для предварительной загрузки модели Real-ESRGAN
Это ускорит первый запуск бота
"""

import torch
from RealESRGAN import RealESRGAN

print("🤖 Загрузка модели Real-ESRGAN...")
print("📊 Это может занять несколько минут при первом запуске...\n")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🖥️  Используется устройство: {device}")

if torch.cuda.is_available():
    print(f"✅ GPU обнаружен: {torch.cuda.get_device_name(0)}")
    print(f"💾 Доступная память GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} ГБ")
else:
    print("⚠️  GPU не обнаружен, будет использоваться CPU (медленнее)")

print("\n📥 Загрузка весов модели...")
model = RealESRGAN(device, scale=4)
model.load_weights('weights/RealESRGAN_x4.pth', download=True)

print("\n✅ Модель успешно загружена!")
print("🚀 Теперь вы можете запустить бота: python bot.py")
