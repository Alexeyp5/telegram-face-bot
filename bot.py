import os
import face_recognition
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv("7581890451:AAGqMTghmFGQZku0Ei9wiQvgrvgZ3AstipA")
USER_ID = int(os.getenv("179255420"))  # твой Telegram ID
TARGET_PHOTO_1 = "target_1.jpg"  # Первое эталонное фото
TARGET_PHOTO_2 = "target_2.jpg"  # Второе эталонное фото

# Загружаем эталонные фотографии и получаем их кодировки
target_image_1 = face_recognition.load_image_file(TARGET_PHOTO_1)
target_encoding_1 = face_recognition.face_encodings(target_image_1)[0]

target_image_2 = face_recognition.load_image_file(TARGET_PHOTO_2)
target_encoding_2 = face_recognition.face_encodings(target_image_2)[0]

def handle_photo(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    photo_file.download("temp.jpg")

    try:
        unknown_image = face_recognition.load_image_file("temp.jpg")
        encodings = face_recognition.face_encodings(unknown_image)

        for encoding in encodings:
            # Сравниваем лицо с двумя эталонными фото
            match_1 = face_recognition.compare_faces([target_encoding_1], encoding, tolerance=0.5)
            match_2 = face_recognition.compare_faces([target_encoding_2], encoding, tolerance=0.5)
            
            # Если есть совпадение с любым из эталонов
            if match_1[0] or match_2[0]:
                context.bot.send_photo(chat_id=USER_ID, photo=open("temp.jpg", "rb"))
                break
    except Exception as e:
        print("Ошибка:", e)
    finally:
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()