#!/bin/bash
# Скрипт для быстрой установки бота

echo "🚀 Установка Telegram Photo Upscaler Bot"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Пожалуйста, установите Python 3.8 или выше."
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"
echo ""

# Создание виртуального окружения
echo "📦 Создание виртуального окружения..."
python3 -m venv venv

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env если его нет
if [ ! -f .env ]; then
    echo "📝 Создание файла .env..."
    cp .env.example .env
    echo ""
    echo "⚠️  ВАЖНО: Отредактируйте файл .env и добавьте ваш TELEGRAM_BOT_TOKEN"
    echo "    Получить токен можно у @BotFather в Telegram"
else
    echo "✅ Файл .env уже существует"
fi

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Получите токен бота у @BotFather в Telegram"
echo "2. Отредактируйте файл .env и укажите токен"
echo "3. Активируйте окружение: source venv/bin/activate"
echo "4. Запустите бота: python bot.py"
echo ""
