#!/usr/bin/env python3
"""
Скрипт для тестирования функций апскейлинга бота
"""

import os
from PIL import Image
import io
from bot import PhotoUpscalerBot

def test_upscaling():
    """Тестируем функцию апскейлинга"""
    print("🧪 Тестирование функции апскейлинга...")
    
    # Создаем тестовое изображение
    test_image = Image.new('RGB', (100, 100), color='red')
    
    # Создаем экземпляр бота (без токена для тестирования)
    class TestBot:
        def __init__(self):
            self.device = "cpu"
            self.upscaler = "enhanced_pil"
    
    bot = TestBot()
    
    # Тестируем апскейлинг
    try:
        upscaled = bot._upscale_image(test_image)
        print(f"✅ Апскейлинг успешен!")
        print(f"   Исходный размер: {test_image.size}")
        print(f"   Новый размер: {upscaled.size}")
        
        # Проверяем, что размер увеличился в 2 раза
        expected_size = (test_image.size[0] * 2, test_image.size[1] * 2)
        if upscaled.size == expected_size:
            print("✅ Размер увеличился корректно")
        else:
            print(f"❌ Неожиданный размер: ожидался {expected_size}, получен {upscaled.size}")
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")

def test_image_formats():
    """Тестируем поддержку различных форматов"""
    print("\n🖼️ Тестирование форматов изображений...")
    
    formats = ['RGB', 'RGBA', 'L', 'P']
    
    for fmt in formats:
        try:
            if fmt == 'P':
                # Для палитрового режима создаем изображение с палитрой
                img = Image.new('P', (50, 50))
                img.putpalette([255, 0, 0, 0, 255, 0, 0, 0, 255] + [0] * 765)
            else:
                img = Image.new(fmt, (50, 50), color='blue')
            
            # Конвертируем в RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            print(f"✅ Формат {fmt} поддерживается")
            
        except Exception as e:
            print(f"❌ Ошибка с форматом {fmt}: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов Telegram Photo Upscaler Bot\n")
    
    test_upscaling()
    test_image_formats()
    
    print("\n✨ Тестирование завершено!")