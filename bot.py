import logging
import os
import face_recognition
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from face_utils import load_known_faces, match_face

# === НАСТРОЙКИ ===
BOT_TOKEN = "7581890451:AAGqMTghmFGQZku0Ei9wiQvgrvgZ3AstipA"
OWNER_ID = 179255420
FACE_MATCH_THRESHOLD = 0.60 # Порог чувствительности, только для совпадений более 

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
        matched, similarity = match_face(file_path, known_encodings, threshold=FACE_MATCH_THRESHOLD)
        if matched and similarity > 0.6:  # Проверяем, что совпадение больше 90%
            # Отправляем фото
            await context.bot.send_photo(chat_id=OWNER_ID, photo=open(file_path, "rb"))
            # Отправляем сообщение с процентом совпадения
            similarity_percent = round(similarity * 100, 2)  # Преобразуем в проценты
            await context.bot.send_message(chat_id=OWNER_ID, text=f"Совпадение лица: {similarity_percent}%")
            logger.info(f"Фото отправлено владельцу с совпадением: {similarity_percent}%")
        else:
            logger.info(f"Лицо не совпало или процент ниже TARGET : {similarity*100}%")
    except Exception as e:
        logger.error(f"Ошибка при распознавании: {e}")

    os.remove(file_path)

# === СТАРТ ===
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.GROUPS, handle_photo))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
