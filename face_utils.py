import face_recognition
import os

def load_known_faces(known_dir="/home/Alexeyp5/telegram-face-bot/target_faces"):
    known_encodings = []
    for file in os.listdir(known_dir):
        path = os.path.join(known_dir, file)
        img = face_recognition.load_image_file(path)
        encs = face_recognition.face_encodings(img)
        if encs:
            known_encodings.append(encs[0])
    return known_encodings

def match_face(photo_path, known_encodings, threshold=0.6):
    img = face_recognition.load_image_file(photo_path)
    unknown_encs = face_recognition.face_encodings(img)
    
    if len(unknown_encs) == 0:
        return False, 0  # Если лица не найдены, возвращаем False и 0

    for enc in unknown_encs:
        results = face_recognition.compare_faces(known_encodings, enc, tolerance=threshold)
        if any(results):
            distances = face_recognition.face_distance(known_encodings, enc)
            similarity = 1 - min(distances)  # Чем меньше расстояние, тем больше сходство
            return True, similarity  # Возвращаем True и процент сходства
    return False, 0  # Если лицо не совпало, возвращаем False и 0
