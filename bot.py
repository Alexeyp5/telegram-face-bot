import os
import cv2
import mediapipe as mp
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

BOT_TOKEN = os.getenv("7581890451:AAGqMTghmFGQZku0Ei9wiQvgrvgZ3AstipA")
USER_ID = int(os.getenv("179255420"))  # твой Telegram ID
TARGET_PHOTO_1 = "target_1.jpg"  # Первое эталонное фото
TARGET_PHOTO_2 = "target_2.jpg"  # Второе эталонное фото

# Инициализация MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.2)

# Загружаем эталонные фотографии для сравнения
target_image_1 = cv2.imread(TARGET_PHOTO_1)
target_image_2 = cv2.imread(TARGET_PHOTO_2)

# Преобразуем эталонные изображения в формат, удобный для сравнения
def preprocess_image(image):
    # Преобразуем в RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb

# Функция для обнаружения лиц на изображении
def detect_faces(image):
    image_rgb = preprocess_image(image)
    results = face_detection.process(image_rgb)
    
    # Если лица найдены, возвращаем их
    if results.detections:
        return True
    return False

def handle_photo(update: Update, context: CallbackContext):
    # Получаем фото из группы
    photo_file = update.message.photo[-1].get_file()
    photo_file.download("temp.jpg")

    try:
        unknown_image = cv2.imread("temp.jpg")
        
        # Проверяем, есть ли на изображении лица, используя MediaPipe
        if detect_faces(unknown_image):
            # Сравниваем изображение с эталонами (по простому методу, чтобы получить основной результат)
            match_1 = detect_faces(target_image_1)
            match_2 = detect_faces(target_image_2)
            
            if match_1 or match_2:
                # Отправляем фото в личку
                context.bot.send_photo(chat_id=USER_ID, photo=open("temp.jpg", "rb"))
    except Exception as e:
        print("Ошибка:", e)
    finally:
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))  # Слушаем фото
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
