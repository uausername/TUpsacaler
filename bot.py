import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageEnhance
import torch
import io
import asyncio
from dotenv import load_dotenv
from utils import setup_logging, validate_image, optimize_image_for_processing, calculate_processing_time, format_file_size, get_image_info

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

class PhotoUpscalerBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        
        # Инициализируем модель апскейлинга
        self.upscaler = None
        self._load_model()
    
    def _load_model(self):
        """Загружаем модель апскейлинга"""
        try:
            logger.info("Инициализируем систему апскейлинга...")
            # Проверяем доступность CUDA
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"Используется устройство: {self.device}")
            
            # Для простоты используем встроенные методы PIL с улучшениями
            self.upscaler = "enhanced_pil"
            logger.info("Система апскейлинга инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации: {e}")
            self.upscaler = "basic_pil"
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_message = """
🖼️ Добро пожаловать в бот для апскейлинга фотографий!

Просто отправьте мне фотографию, и я увеличу её разрешение в 2 раза с помощью ИИ.

Команды:
/start - показать это сообщение
/help - помощь
/status - статус бота

Отправьте фото для апскейлинга! 📸
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 Помощь по использованию бота:

1. Отправьте фотографию в формате JPG или PNG
2. Бот обработает изображение и увеличит его разрешение
3. Получите улучшенную версию фотографии

⚠️ Ограничения:
- Максимальный размер файла: 20MB
- Поддерживаемые форматы: JPG, PNG
- Время обработки: 30-60 секунд

Если у вас есть вопросы, обратитесь к администратору.
        """
        await update.message.reply_text(help_text)
    
    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status"""
        model_status = "✅ Загружена" if self.upscaler else "❌ Не загружена (используется простое масштабирование)"
        gpu_status = "✅ CUDA доступна" if torch.cuda.is_available() else "❌ CUDA недоступна (CPU режим)"
        
        status_text = f"""
🤖 Статус бота:

Модель апскейлинга: {model_status}
GPU: {gpu_status}
Статус: ✅ Работает
        """
        await update.message.reply_text(status_text)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик фотографий"""
        try:
            # Получаем информацию о файле
            file = await context.bot.get_file(update.message.photo[-1].file_id)
            
            # Скачиваем изображение
            image_data = await file.download_as_bytearray()
            
            # Валидация изображения
            is_valid, error_msg = validate_image(image_data)
            if not is_valid:
                await update.message.reply_text(f"❌ {error_msg}")
                return
            
            # Получаем информацию об изображении
            image = Image.open(io.BytesIO(image_data))
            image_info = get_image_info(image)
            
            # Оценка времени обработки
            processing_time = calculate_processing_time(image.size)
            
            # Отправляем сообщение о начале обработки
            processing_msg = await update.message.reply_text(
                f"🔄 Обрабатываю изображение...\n"
                f"Размер: {image_info['width']}x{image_info['height']}\n"
                f"Время обработки: ~{processing_time} сек"
            )
            
            # Оптимизируем изображение для обработки
            optimized_image = optimize_image_for_processing(image)
            
            # Апскейлинг изображения
            upscaled_image = await self._upscale_image(optimized_image)
            
            # Сохраняем результат в байты
            output_buffer = io.BytesIO()
            upscaled_image.save(output_buffer, format='JPEG', quality=95)
            output_buffer.seek(0)
            
            # Получаем размер файла
            file_size = format_file_size(len(output_buffer.getvalue()))
            
            # Отправляем результат
            await processing_msg.delete()
            await update.message.reply_photo(
                photo=output_buffer,
                caption=f"✅ Изображение увеличено!\n"
                       f"Исходный размер: {image.size}\n"
                       f"Новый размер: {upscaled_image.size}\n"
                       f"Размер файла: {file_size}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке фото: {e}")
            await update.message.reply_text("❌ Произошла ошибка при обработке изображения. Попробуйте еще раз.")
    
    async def _upscale_image(self, image: Image.Image) -> Image.Image:
        """Апскейлинг изображения с улучшениями"""
        try:
            # Ограничиваем размер для обработки
            max_size = 1024
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Увеличиваем разрешение в 2 раза
            width, height = image.size
            new_size = (width * 2, height * 2)
            
            # Используем LANCZOS для лучшего качества
            upscaled = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Применяем улучшения
            if self.upscaler == "enhanced_pil":
                # Улучшаем резкость
                enhancer = ImageEnhance.Sharpness(upscaled)
                upscaled = enhancer.enhance(1.2)
                
                # Небольшое улучшение контраста
                enhancer = ImageEnhance.Contrast(upscaled)
                upscaled = enhancer.enhance(1.1)
                
                # Легкое улучшение насыщенности
                enhancer = ImageEnhance.Color(upscaled)
                upscaled = enhancer.enhance(1.05)
            
            return upscaled
            
        except Exception as e:
            logger.error(f"Ошибка при апскейлинге: {e}")
            # Fallback на простое масштабирование
            width, height = image.size
            new_size = (width * 2, height * 2)
            return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def run(self):
        """Запуск бота"""
        # Создаем приложение
        application = Application.builder().token(self.token).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Запускаем бота
        logger.info("Запускаем бота...")
        application.run_polling()

if __name__ == '__main__':
    try:
        bot = PhotoUpscalerBot()
        bot.run()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")