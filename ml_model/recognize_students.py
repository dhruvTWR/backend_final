import face_recognition
import pickle
import os
import numpy as np
from datetime import datetime
import csv
import cv2
import uuid

def recognize_students(image_path):
    """
    Recognizes students and saves unrecognized face images.
    Returns:
        recognized_names (list[str]),
        unrecognized_faces (list[dict]) with keys 'image', 'time', 'source_image'
    """
    encodings_file = r"C:\Users\dhruv\Desktop\smart_attendance_combined\ml_model\encodings.pickle"
    if not os.path.exists(encodings_file):
        print("❌ encodings.pickle not found. Run generate_encodings.py first.")
        return [], []

    with open(encodings_file, "rb") as f:
        data = pickle.load(f)

    known_encodings = data["encodings"]
    known_names = data["names"]

    try:
        image = face_recognition.load_image_file(image_path)
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
        return [], []

    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    print(f"📷 Detected {len(face_locations)} face(s) in the image.")
    print(f"🔎 Encodings generated for {len(face_encodings)} face(s).")

    recognized_names = set()
    unrecognized_faces = []

    # Convert to BGR for OpenCV (to save images)
    opencv_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    for i, (top, right, bottom, left) in enumerate(face_locations):
        if i < len(face_encodings):
            face_encoding = face_encodings[i]
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.46)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            name = "Unrecognized"

            if True in matches:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]

            if name != "Unrecognized":
                recognized_names.add(name)
            else:
                # Save cropped unknown face
                face_crop = opencv_image[top:bottom, left:right]
                os.makedirs("unrecognized", exist_ok=True)
                filename = f"unrecognized/{uuid.uuid4().hex}.jpg"
                cv2.imwrite(filename, face_crop)

                unrecognized_faces.append({
                    "image": filename,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "source_image": os.path.basename(image_path)
                })
        else:
            # No encoding for this face → still save it
            face_crop = opencv_image[top:bottom, left:right]
            os.makedirs("unrecognized", exist_ok=True)
            filename = f"unrecognized/{uuid.uuid4().hex}_noencoding.jpg"
            cv2.imwrite(filename, face_crop)

            unrecognized_faces.append({
                "image": filename,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source_image": os.path.basename(image_path)
            })

    return list(recognized_names), unrecognized_faces


def save_attendance(names, image_filename):
    """
    Save recognized attendance to CSV with date and time.
    """
    if not names:
        print("⚠️ No recognized names to save.")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    attendance_folder = "attendance"
    os.makedirs(attendance_folder, exist_ok=True)

    csv_filename = os.path.join(attendance_folder, f"{today}.csv")
    is_new_file = not os.path.exists(csv_filename)

    with open(csv_filename, mode="a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if is_new_file:
            writer.writerow(["Name", "Time", "Image"])

        for name in names:
            writer.writerow([name, timestamp, os.path.basename(image_filename)])

    print(f"✅ Attendance saved to {csv_filename}")


def save_unrecognized_log(unrecognized_faces):
    """
    Save unrecognized face info to a CSV log for admin/teacher review.
    """
    if not unrecognized_faces:
        return

    log_folder = "unrecognized"
    os.makedirs(log_folder, exist_ok=True)

    log_file = os.path.join(log_folder, "unrecognized_log.csv")
    is_new = not os.path.exists(log_file)

    with open(log_file, mode="a", newline="") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["Image", "Time", "Source Photo"])

        for entry in unrecognized_faces:
            writer.writerow([entry["image"], entry["time"], entry["source_image"]])

    print(f"⚠️ Logged {len(unrecognized_faces)} unrecognized face(s) to {log_file}")


if __name__ == '__main__':
    test_image = r"ml_model\uploads\grp_3tb.jpg"

    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
    else:
        print(f"🔍 Recognizing students from: {test_image}")
        recognized, unrecognized = recognize_students(test_image)

        print("\n🎓 Recognized Students:")
        if recognized:
            for name in recognized:
                print(f" - {name}")
        else:
            print("⚠️ No recognized students.")

        if unrecognized:
            print(f"\n❓ Unrecognized faces: {len(unrecognized)} (saved for admin review)")

        save_attendance(recognized, test_image)
        save_unrecognized_log(unrecognized)
