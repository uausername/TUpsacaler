import asyncio
import io
import logging
import os
import tempfile
from typing import Optional

from PIL import Image
import torch
from super_image import EdsrModel, ImageLoader
from telegram import Update, constants
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


MODEL_ID_DEFAULT = "eugenesiow/edsr-base"
SCALE_DEFAULT = 4

MODEL_ID = os.environ.get("UPSCALE_MODEL_ID", MODEL_ID_DEFAULT)
UPSCALE_SCALE = int(os.environ.get("UPSCALE_SCALE", str(SCALE_DEFAULT)))
PREFERRED_DEVICE = os.environ.get("TORCH_DEVICE", "cpu")  # "cpu" or "cuda"

_model: Optional[EdsrModel] = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Пришлите фото, я увеличу его качеством x{} через {}.".format(
            UPSCALE_SCALE, MODEL_ID
        )
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Отправьте фото, и я верну увеличенную версию.\n"
        "Переменные окружения:\n"
        "- TELEGRAM_BOT_TOKEN — токен бота\n"
        "- UPSCALE_MODEL_ID — модель HuggingFace (по умолчанию: {})\n"
        "- UPSCALE_SCALE — коэффициент x (по умолчанию: {})\n"
        "- TORCH_DEVICE — cpu или cuda (по умолчанию: cpu)".format(
            MODEL_ID_DEFAULT, SCALE_DEFAULT
        )
    )


def _get_model() -> EdsrModel:
    global _model
    if _model is None:
        logging.info("Загрузка модели %s (x%s)", MODEL_ID, UPSCALE_SCALE)
        model = EdsrModel.from_pretrained(MODEL_ID, scale=UPSCALE_SCALE)
        model.eval()
        if PREFERRED_DEVICE == "cuda" and torch.cuda.is_available():
            model = model.to("cuda")
            logging.info("Модель переведена на CUDA")
        else:
            model = model.to("cpu")
        _model = model
    return _model


def _upscale_image_bytes(input_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(input_bytes)).convert("RGB")

    model = _get_model()
    inputs = ImageLoader.load_image(image)

    with torch.inference_mode():
        preds = model(inputs)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        ImageLoader.save_image(preds, tmp_path)
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.photo:
        return

    # Сообщим о загрузке
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=constants.ChatAction.UPLOAD_PHOTO
    )

    # Берём фото с максимальным разрешением
    largest_photo = update.message.photo[-1]
    file = await context.bot.get_file(largest_photo.file_id)

    buffer = io.BytesIO()
    await file.download_to_memory(out=buffer)
    input_bytes = buffer.getvalue()

    loop = asyncio.get_running_loop()
    try:
        upscaled_bytes = await loop.run_in_executor(
            None, _upscale_image_bytes, input_bytes
        )
    except Exception as exc:  # noqa: BLE001
        logging.exception("Ошибка апскейла: %s", exc)
        await update.message.reply_text(
            "Не удалось увеличить изображение. Попробуйте позже или другое фото."
        )
        return

    caption = f"x{UPSCALE_SCALE} через {MODEL_ID}"
    await update.message.reply_photo(photo=upscaled_bytes, caption=caption)


def _build_application(token: str) -> Application:
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    return application


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "Не задан TELEGRAM_BOT_TOKEN. Экспортируйте переменную окружения и запустите снова."
        )

    app = _build_application(token)
    app.run_polling()


if __name__ == "__main__":
    main()
