#!/usr/bin/env python3
"""
Telegram бот для апскейлинга изображений
Использует модель Real-ESRGAN для улучшения качества фотографий
"""

import os
import logging
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import torch
from PIL import Image
from RealESRGAN import RealESRGAN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация модели
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
logger.info(f"Используется устройство: {device}")

# Загружаем модель Real-ESRGAN
model = RealESRGAN(device, scale=4)
model.load_weights('weights/RealESRGAN_x4.pth', download=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_message = (
        "👋 Привет! Я бот для улучшения качества фотографий!\n\n"
        "📸 Отправь мне любое изображение, и я увеличу его разрешение в 4 раза, "
        "сохранив при этом детали и улучшив качество.\n\n"
        "🤖 Я использую технологию Real-ESRGAN - продвинутый алгоритм апскейлинга.\n\n"
        "Команды:\n"
        "/start - Показать это сообщение\n"
        "/help - Справка\n\n"
        "Просто отправь мне фото! 🖼️"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = (
        "ℹ️ Как использовать бота:\n\n"
        "1. Отправьте мне любое изображение (как фото или файл)\n"
        "2. Подождите, пока я обработаю его (это может занять 10-60 секунд)\n"
        "3. Получите улучшенное изображение с увеличенным разрешением!\n\n"
        "⚠️ Ограничения:\n"
        "- Максимальный размер файла: 20 МБ\n"
        "- Поддерживаемые форматы: JPG, PNG, WEBP\n"
        "- Изображение будет увеличено в 4 раза\n\n"
        "💡 Совет: Для лучшего результата используйте изображения хорошего качества."
    )
    await update.message.reply_text(help_text)


async def process_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка полученного изображения"""
    try:
        # Отправляем сообщение о начале обработки
        processing_msg = await update.message.reply_text(
            "⏳ Обрабатываю изображение... Это может занять некоторое время."
        )
        
        # Получаем файл изображения
        if update.message.photo:
            # Если отправлено как фото, берем наибольшее разрешение
            photo_file = await update.message.photo[-1].get_file()
        elif update.message.document:
            # Если отправлено как документ
            photo_file = await update.message.document.get_file()
        else:
            await update.message.reply_text("❌ Пожалуйста, отправьте изображение!")
            return
        
        # Скачиваем изображение
        logger.info(f"Скачивание изображения от пользователя {update.effective_user.id}")
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Открываем изображение
        input_image = Image.open(BytesIO(photo_bytes)).convert('RGB')
        logger.info(f"Исходный размер: {input_image.size}")
        
        # Проверяем размер изображения
        max_dimension = 2000
        if max(input_image.size) > max_dimension:
            await processing_msg.edit_text(
                f"⚠️ Изображение слишком большое! Максимальный размер: {max_dimension}x{max_dimension} пикселей.\n"
                "Пожалуйста, отправьте изображение меньшего размера."
            )
            return
        
        # Применяем апскейлинг
        logger.info("Применение апскейлинга...")
        await processing_msg.edit_text("🔄 Применяю апскейлинг... Почти готово!")
        
        upscaled_image = model.predict(input_image)
        logger.info(f"Новый размер: {upscaled_image.size}")
        
        # Сохраняем результат в буфер
        output_buffer = BytesIO()
        upscaled_image.save(output_buffer, format='PNG', quality=95)
        output_buffer.seek(0)
        
        # Отправляем результат
        await processing_msg.edit_text("✅ Готово! Отправляю результат...")
        
        caption = (
            f"✨ Изображение улучшено!\n"
            f"📊 Исходный размер: {input_image.size[0]}x{input_image.size[1]}\n"
            f"📈 Новый размер: {upscaled_image.size[0]}x{upscaled_image.size[1]}\n"
            f"🔢 Увеличение: x4"
        )
        
        await update.message.reply_document(
            document=output_buffer,
            filename=f"upscaled_{update.effective_user.id}.png",
            caption=caption
        )
        
        # Удаляем сообщение о процессе
        await processing_msg.delete()
        
        logger.info(f"Успешно обработано изображение для пользователя {update.effective_user.id}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке изображения: {e}", exc_info=True)
        error_message = (
            "❌ Произошла ошибка при обработке изображения.\n"
            "Пожалуйста, попробуйте:\n"
            "- Отправить изображение меньшего размера\n"
            "- Использовать другой формат (JPG, PNG)\n"
            "- Попробовать позже"
        )
        await update.message.reply_text(error_message)


async def handle_unsupported(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка неподдерживаемых типов сообщений"""
    await update.message.reply_text(
        "❌ Я могу обрабатывать только изображения.\n"
        "Пожалуйста, отправьте фото или изображение как файл."
    )


def main():
    """Запуск бота"""
    # Получаем токен из переменной окружения
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        print("❌ Ошибка: Укажите TELEGRAM_BOT_TOKEN в файле .env")
        return
    
    # Создаем приложение
    application = Application.builder().token(token).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, process_image))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_unsupported))
    
    # Запускаем бота
    logger.info("🤖 Бот запущен и готов к работе!")
    print("✅ Бот успешно запущен! Нажмите Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
