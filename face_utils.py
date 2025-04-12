import face_recognition
import os

def load_known_faces(known_dir="target_faces"):
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
    for enc in unknown_encs:
        results = face_recognition.compare_faces(known_encodings, enc, tolerance=threshold)
        if any(results):
            return True
    return False
