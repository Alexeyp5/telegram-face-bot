import os
import cv2
import mediapipe as mp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

# Получаем переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))
TARGET_PHOTO_1 = "target_1.jpg"
TARGET_PHOTO_2 = "target_2.jpg"

# Инициализация MediaPipe
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.2)

# Загружаем эталонные изображения
target_image_1 = cv2.imread(TARGET_PHOTO_1)
target_image_2 = cv2.imread(TARGET_PHOTO_2)

# Преобразование изображения
async def preprocess_image(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb

# Обнаружение лиц
async def detect_faces(image):
    image_rgb = await preprocess_image(image)
    results = face_detection.process(image_rgb)
    return bool(results.detections)

# Обработчик фото
async def handle_photo(update: Update, context: CallbackContext):
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download("temp.jpg")

    try:
        unknown_image = cv2.imread("temp.jpg")
        if await detect_faces(unknown_image):
            match_1 = await detect_faces(target_image_1)
            match_2 = await detect_faces(target_image_2)
            if match_1 or match_2:
                await context.bot.send_photo(chat_id=USER_ID, photo=open("temp.jpg", "rb"))
    except Exception as e:
        print("Ошибка:", e)
    finally:
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")

# Запуск бота (ручной режим для Render)
async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.wait_until_closed()
    await application.stop()
    await application.shutdown()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(run_bot())
    except RuntimeError as e:
        print(f"Ошибка запуска бота: {e}")
