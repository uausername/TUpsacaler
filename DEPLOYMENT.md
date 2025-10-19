# Руководство по развертыванию

## Быстрый старт

### 1. Создание Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Введите имя для вашего бота (например: "Photo Upscaler Bot")
4. Введите username для бота (например: "photo_upscaler_bot")
5. Скопируйте полученный токен

### 2. Настройка проекта

```bash
# Клонируйте репозиторий
git clone <repository-url>
cd telegram-photo-upscaler-bot

# Создайте виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установите зависимости
pip install -r requirements.txt

# Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env и добавьте токен бота
```

### 3. Запуск

```bash
# Простой запуск
python bot.py

# Или через скрипт запуска
python run.py

# Для тестирования функций
python test_bot.py
```

## Развертывание на сервере

### Использование systemd (Linux)

1. Создайте файл сервиса:

```bash
sudo nano /etc/systemd/system/photo-upscaler-bot.service
```

2. Добавьте содержимое:

```ini
[Unit]
Description=Telegram Photo Upscaler Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/telegram-photo-upscaler-bot
Environment=PATH=/path/to/telegram-photo-upscaler-bot/venv/bin
ExecStart=/path/to/telegram-photo-upscaler-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Запустите сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable photo-upscaler-bot
sudo systemctl start photo-upscaler-bot
sudo systemctl status photo-upscaler-bot
```

### Использование Docker

1. Создайте `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

2. Создайте `docker-compose.yml`:

```yaml
version: '3.8'

services:
  photo-upscaler-bot:
    build: .
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

3. Запустите:

```bash
docker-compose up -d
```

## Мониторинг и логи

### Просмотр логов

```bash
# Логи systemd
sudo journalctl -u photo-upscaler-bot -f

# Логи приложения
tail -f bot.log

# Docker логи
docker-compose logs -f
```

### Мониторинг производительности

Бот автоматически логирует:
- Время обработки изображений
- Ошибки и исключения
- Статистику использования

## Безопасность

### Рекомендации

1. **Никогда не коммитьте `.env` файл**
2. **Используйте отдельного пользователя для бота**
3. **Ограничьте права доступа к файлам**
4. **Регулярно обновляйте зависимости**

### Настройка файрвола

```bash
# Разрешить только исходящие соединения
sudo ufw allow out 443
sudo ufw allow out 80
```

## Масштабирование

### Горизонтальное масштабирование

Для обработки большого количества запросов:

1. Запустите несколько экземпляров бота
2. Используйте балансировщик нагрузки
3. Настройте Redis для кеширования

### Вертикальное масштабирование

1. Увеличьте RAM сервера
2. Используйте GPU для ускорения обработки
3. Оптимизируйте алгоритмы апскейлинга

## Устранение неполадок

### Частые проблемы

1. **Бот не отвечает**
   - Проверьте токен в `.env`
   - Убедитесь, что бот запущен
   - Проверьте логи на ошибки

2. **Ошибки обработки изображений**
   - Проверьте формат изображения
   - Убедитесь в наличии свободного места
   - Проверьте права доступа к файлам

3. **Медленная обработка**
   - Увеличьте RAM
   - Используйте SSD диски
   - Оптимизируйте размер изображений

### Диагностика

```bash
# Проверка статуса
python test_bot.py

# Проверка зависимостей
pip check

# Проверка дискового пространства
df -h

# Проверка памяти
free -h
```

## Обновление

### Обновление кода

```bash
git pull origin main
pip install -r requirements.txt
sudo systemctl restart photo-upscaler-bot
```

### Обновление зависимостей

```bash
pip install --upgrade -r requirements.txt
```

## Резервное копирование

### Важные файлы

- `.env` - конфигурация
- `bot.log` - логи
- База данных (если используется)

### Автоматическое резервное копирование

```bash
# Создайте скрипт резервного копирования
#!/bin/bash
tar -czf backup-$(date +%Y%m%d).tar.gz .env bot.log
```

## Поддержка

При возникновении проблем:

1. Проверьте логи
2. Запустите тесты
3. Создайте issue в репозитории
4. Обратитесь к документации