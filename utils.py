"""
Вспомогательные функции для Telegram Photo Upscaler Bot
"""

import os
import logging
from PIL import Image
import io

def setup_logging(level=logging.INFO):
    """Настройка системы логирования"""
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=level,
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )

def validate_image(image_data: bytes) -> tuple[bool, str]:
    """
    Валидация изображения
    
    Args:
        image_data: Данные изображения в байтах
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Проверяем размер файла (20MB лимит Telegram)
        max_size = 20 * 1024 * 1024  # 20MB
        if len(image_data) > max_size:
            return False, f"Файл слишком большой: {len(image_data) / 1024 / 1024:.1f}MB (максимум 20MB)"
        
        # Пытаемся открыть изображение
        image = Image.open(io.BytesIO(image_data))
        
        # Проверяем формат
        if image.format not in ['JPEG', 'PNG', 'WEBP']:
            return False, f"Неподдерживаемый формат: {image.format}"
        
        # Проверяем размеры
        width, height = image.size
        if width < 10 or height < 10:
            return False, "Изображение слишком маленькое (минимум 10x10 пикселей)"
        
        if width > 4096 or height > 4096:
            return False, "Изображение слишком большое (максимум 4096x4096 пикселей)"
        
        return True, ""
        
    except Exception as e:
        return False, f"Ошибка при валидации изображения: {str(e)}"

def optimize_image_for_processing(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """
    Оптимизация изображения для обработки
    
    Args:
        image: Исходное изображение
        max_size: Максимальный размер по большей стороне
        
    Returns:
        Оптимизированное изображение
    """
    # Конвертируем в RGB если необходимо
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Ограничиваем размер для обработки
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    
    return image

def calculate_processing_time(image_size: tuple) -> int:
    """
    Примерная оценка времени обработки в секундах
    
    Args:
        image_size: Размер изображения (width, height)
        
    Returns:
        Ориентировочное время обработки в секундах
    """
    pixels = image_size[0] * image_size[1]
    
    # Базовое время + время пропорциональное количеству пикселей
    base_time = 5  # 5 секунд базовое время
    pixel_time = pixels / 100000  # ~0.01 секунды на 1000 пикселей
    
    return int(base_time + pixel_time)

def format_file_size(size_bytes: int) -> str:
    """
    Форматирование размера файла в читаемый вид
    
    Args:
        size_bytes: Размер в байтах
        
    Returns:
        Отформатированная строка с размером
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

def get_image_info(image: Image.Image) -> dict:
    """
    Получение информации об изображении
    
    Args:
        image: Изображение PIL
        
    Returns:
        Словарь с информацией об изображении
    """
    return {
        'size': image.size,
        'mode': image.mode,
        'format': image.format,
        'width': image.size[0],
        'height': image.size[1],
        'pixels': image.size[0] * image.size[1],
        'aspect_ratio': round(image.size[0] / image.size[1], 2)
    }