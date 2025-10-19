#!/bin/bash

# Скрипт установки Telegram Photo Upscaler Bot

echo "🤖 Установка Telegram Photo Upscaler Bot"
echo "========================================"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python 3.8+ и попробуйте снова."
    exit 1
fi

echo "✅ Python3 найден"

# Создаем виртуальное окружение
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активируем виртуальное окружение
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Обновляем pip
echo "⬆️ Обновление pip..."
pip install --upgrade pip

# Устанавливаем зависимости
echo "📚 Установка зависимостей..."
pip install -r requirements.txt

# Создаем .env файл если его нет
if [ ! -f .env ]; then
    echo "⚙️ Создание файла конфигурации..."
    cp .env.example .env
    echo "📝 Отредактируйте файл .env и добавьте токен вашего бота"
fi

# Создаем директорию для логов
mkdir -p logs

# Делаем скрипты исполняемыми
chmod +x run.py
chmod +x test_bot.py

echo ""
echo "✅ Установка завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте .env файл и добавьте токен бота"
echo "2. Запустите бота: python run.py"
echo "3. Или протестируйте: python test_bot.py"
echo ""
echo "Удачного использования! 🚀"