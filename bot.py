import os
import cv2
import mediapipe as mp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))
TARGET_PHOTO_1 = "target_1.jpg"
TARGET_PHOTO_2 = "target_2.jpg"

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.2)

target_image_1 = cv2.imread(TARGET_PHOTO_1)
target_image_2 = cv2.imread(TARGET_PHOTO_2)

async def preprocess_image(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

async def detect_faces(image):
    image_rgb = await preprocess_image(image)
    results = face_detection.process(image_rgb)
    return bool(results.detections)

async def handle_photo(update: Update, context: CallbackContext):
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("temp.jpg")

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

async def run_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Бот запущен")
    await application.run_polling()

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(run_bot())
        loop.run_forever()
    except RuntimeError as e:
        print("Ошибка запуска event loop:", e)
