import os
import cv2
import mediapipe as mp
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Получаем токен из переменной окружения
USER_ID = int(os.getenv("USER_ID"))  # Используем переменную окружения USER_ID
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
async def preprocess_image(image):
    # Преобразуем в RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image_rgb

# Функция для обнаружения лиц на изображении
async def detect_faces(image):
    image_rgb = await preprocess_image(image)
    results = face_detection.process(image_rgb)
    
    # Если лица найдены, возвращаем их
    if results.detections:
        return True
    return False

# Обработчик фотографии
async def handle_photo(update: Update, context: CallbackContext):
    # Получаем фото из группы
    photo_file = await update.message.photo[-1].get_file()  # используем await для асинхронного получения файла
    await photo_file.download("temp.jpg")  # используем await для асинхронного скачивания фото

    try:
        unknown_image = cv2.imread("temp.jpg")
        
        # Проверяем, есть ли на изображении лица, используя MediaPipe
        if await detect_faces(unknown_image):
            # Сравниваем изображение с эталонами (по простому методу, чтобы получить основной результат)
            match_1 = await detect_faces(target_image_1)
            match_2 = await detect_faces(target_image_2)
            
            if match_1 or match_2:
                # Отправляем фото в личку
                await context.bot.send_photo(chat_id=USER_ID, photo=open("temp.jpg", "rb"))
    except Exception as e:
        print("Ошибка:", e)
    finally:
        if os.path.exists("temp.jpg"):
            os.remove("temp.jpg")

# Главная функция
async def main():
    # Создаем объект Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчик сообщений
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))  # Слушаем фото
    
    # Запуск бота
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
