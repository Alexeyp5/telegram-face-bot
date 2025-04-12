import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from face_utils import load_known_faces, match_face

# === НАСТРОЙКИ ===
BOT_TOKEN = "7581890451:AAGqMTghmFGQZku0Ei9wiQvgrvgZ3AstipA"
OWNER_ID = 179255420
FACE_MATCH_THRESHOLD = 0.6  # Порог чувствительности — можно изменить от 0.4 до 0.6+

# === ЛОГИ ===
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# === ЗАГРУЗКА ЭТАЛОННЫХ ЛИЦ ===
known_encodings = load_known_faces()

# === ОБРАБОТКА ФОТО ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    # Скачиваем фото
    photo_file = await update.message.photo[-1].get_file()
    file_path = f"temp_{update.message.message_id}.jpg"
    await photo_file.download_to_drive(file_path)

    # Распознавание лиц
    try:
        if match_face(file_path, known_encodings, threshold=FACE_MATCH_THRESHOLD):
            await context.bot.send_photo(chat_id=OWNER_ID, photo=open(file_path, "rb"))
            logger.info(f"Фото отправлено владельцу: {file_path}")
        else:
            logger.info(f"Лицо не совпало: {file_path}")
    except Exception as e:
        logger.error(f"Ошибка при распознавании: {e}")

    os.remove(file_path)

# === СТАРТ ===
async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.GROUPS, handle_photo))
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
