import face_recognition
import os
import pickle
from pathlib import Path

def main():
    print("📦 Starting encoding process...")

    # Get the directory where this script is located
    script_dir = Path(__file__).resolve().parent
    
    # Define paths relative to the script's parent directory (ml_model/)
    # This makes the script runnable from anywhere
    model_root_dir = script_dir.parent
    known_faces_dir = model_root_dir / "student_images"
    output_pickle_path = model_root_dir / "encodings.pickle"

    if not known_faces_dir.exists():
        print(f"❌ Error: The directory '{known_faces_dir}' does not exist. Please create it and add student images.")
        return

    known_face_encodings = []
    known_face_names = []

    # Iterate through each person's folder in student_images/
    for person_name in os.listdir(known_faces_dir):
        person_folder = known_faces_dir / person_name
        if not person_folder.is_dir():
            continue

        # Iterate through each image in the person's folder
        for filename in os.listdir(person_folder):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = person_folder / filename
                image = face_recognition.load_image_file(image_path)
                
                # Find face encodings in the image
                # face_locations = face_recognition.face_locations(image, model="cnn")

                # # Then, it generates the encodings for the locations it found
                # face_encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)
                
                face_encodings = face_recognition.face_encodings(image)

                if face_encodings:
                    # Append the first encoding found and the person's name
                    known_face_encodings.append(face_encodings[0])
                    known_face_names.append(person_name.strip())
                    print(f"✅ Encoded {filename} for {person_name}")
                else:
                    print(f"⚠️ No face found in {filename}. Skipping.")

    # Save the encodings data to the pickle file
    data = {"encodings": known_face_encodings, "names": known_face_names}
    with open(output_pickle_path, "wb") as f:
        pickle.dump(data, f)

    student_count = len(set(known_face_names))
    print(f"\n🎉 Encoding complete. Saved to '{output_pickle_path}'.")
    print(f"Total students encoded: {student_count}")

if __name__ == "__main__":
    main()