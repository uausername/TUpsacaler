#!/usr/bin/env python3
"""
Скрипт для запуска Telegram Photo Upscaler Bot
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Проверяем наличие необходимых файлов и зависимостей"""
    print("🔍 Проверка требований...")
    
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("   Скопируйте .env.example в .env и добавьте токен бота")
        return False
    
    # Проверяем наличие токена
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        print("❌ TELEGRAM_BOT_TOKEN не найден в .env файле!")
        return False
    
    print("✅ Все требования выполнены")
    return True

def main():
    """Основная функция запуска"""
    print("🤖 Telegram Photo Upscaler Bot")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Не удалось запустить бота. Проверьте настройки.")
        sys.exit(1)
    
    try:
        print("🚀 Запускаем бота...")
        from bot import PhotoUpscalerBot
        bot = PhotoUpscalerBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()