import os
import cv2
import mediapipe as mp
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))
TARGET_PHOTO_1 = "target_1.jpg"
TARGET_PHOTO_2 = "target_2.jpg"

mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.2)

target_image_1 = cv2.imread(TARGET_PHOTO_1)
target_image_2 = cv2.imread(TARGET_PHOTO_2)

def preprocess_image(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def detect_faces(image):
    image_rgb = preprocess_image(image)
    results = face_detection.process(image_rgb)
    return bool(results.detections)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("temp.jpg")

    try:
        unknown_image = cv2.imread("temp.jpg")
        if detect_faces(unknown_image):
            if detect_faces(target_image_1) or detect_faces(target_image_2):
                with open("temp.jpg", "rb") as photo:
                    await context.bot.send_photo(chat_id=USER_ID, photo=photo)
    except Exception as e:
        print("Ошибка:", e)
    finally:
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.run_polling()

if __name__ == "__main__":
    main()
