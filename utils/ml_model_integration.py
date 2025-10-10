"""
ML Model Integration Utilities
Provides functions that match your original ML model workflow
"""

import face_recognition
import os
import pickle
import numpy as np
from datetime import datetime
import csv
import cv2
import uuid
from pathlib import Path

def generate_encodings_from_folders(student_images_dir='student_images', output_pickle='encodings.pickle'):
    """
    Generate encodings from folder structure (matches your generate_encodings.py)
    
    Folder structure:
    student_images/
        PersonName1/
            image1.jpg
            image2.jpg
        PersonName2/
            image1.jpg
    """
    print("📦 Starting encoding process...")
    
    student_images_dir = Path(student_images_dir)
    
    if not student_images_dir.exists():
        print(f"❌ Error: The directory '{student_images_dir}' does not exist.")
        print(f"   Please create it and add student images.")
        return None
    
    known_face_encodings = []
    known_face_names = []
    
    # Iterate through each person's folder
    for person_name in os.listdir(student_images_dir):
        person_folder = student_images_dir / person_name
        
        if not person_folder.is_dir():
            continue
        
        # Iterate through each image in the person's folder
        for filename in os.listdir(person_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_path = person_folder / filename
                
                try:
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)
                    
                    if face_encodings:
                        # Append the first encoding found
                        known_face_encodings.append(face_encodings[0])
                        known_face_names.append(person_name.strip())
                        print(f"✅ Encoded {filename} for {person_name}")
                    else:
                        print(f"⚠️ No face found in {filename}. Skipping.")
                        
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")
    
    # Save encodings to pickle
    if known_face_encodings:
        data = {
            "encodings": known_face_encodings,
            "names": known_face_names
        }
        
        with open(output_pickle, 'wb') as f:
            pickle.dump(data, f)
        
        student_count = len(set(known_face_names))
        print(f"\n🎉 Encoding complete. Saved to '{output_pickle}'.")
        print(f"Total students encoded: {student_count}")
        print(f"Total images processed: {len(known_face_encodings)}")
        
        return data
    else:
        print("❌ No encodings generated")
        return None

def recognize_students_from_image(image_path, encodings_file='encodings.pickle', tolerance=0.46):
    """
    Recognize students in image (matches your recognize_students.py)
    
    Args:
        image_path: Path to classroom image
        encodings_file: Path to pickle file with encodings
        tolerance: Recognition tolerance (lower = stricter, your default: 0.46)
    
    Returns:
        tuple: (recognized_names, unrecognized_faces)
    """
    if not os.path.exists(encodings_file):
        print("❌ encodings.pickle not found. Run generate_encodings.py first.")
        return [], []
    
    # Load known encodings
    with open(encodings_file, 'rb') as f:
        data = pickle.load(f)
    
    known_encodings = data["encodings"]
    known_names = data["names"]
    
    # Load and process image
    try:
        image = face_recognition.load_image_file(image_path)
    except Exception as e:
        print(f"❌ Failed to load image: {e}")
        return [], []
    
    # Detect faces
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    print(f"📷 Detected {len(face_locations)} face(s) in the image.")
    print(f"🔎 Encodings generated for {len(face_encodings)} face(s).")
    
    recognized_names = set()
    unrecognized_faces = []
    
    # Convert to BGR for OpenCV (to save images)
    opencv_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    # Process each face
    for i, (top, right, bottom, left) in enumerate(face_locations):
        if i < len(face_encodings):
            face_encoding = face_encodings[i]
            
            # Compare with known faces
            matches = face_recognition.compare_faces(
                known_encodings, 
                face_encoding, 
                tolerance=tolerance
            )
            face_distances = face_recognition.face_distance(
                known_encodings, 
                face_encoding
            )
            
            name = "Unrecognized"
            
            # Find best match
            if True in matches:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]
            
            if name != "Unrecognized":
                recognized_names.add(name)
                print(f"✅ Recognized: {name}")
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
                print(f"⚠️ Unrecognized face saved: {filename}")
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
            print(f"⚠️ Face with no encoding saved: {filename}")
    
    return list(recognized_names), unrecognized_faces

def save_attendance_csv(names, image_filename, output_folder='attendance'):
    """
    Save recognized attendance to CSV (matches your save_attendance function)
    
    Args:
        names: List of recognized student names
        image_filename: Source image filename
        output_folder: Folder to save CSV files
    """
    if not names:
        print("⚠️ No recognized names to save.")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    os.makedirs(output_folder, exist_ok=True)
    
    csv_filename = os.path.join(output_folder, f"{today}.csv")
    is_new_file = not os.path.exists(csv_filename)
    
    with open(csv_filename, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        if is_new_file:
            writer.writerow(["Name", "Time", "Image"])
        
        for name in names:
            writer.writerow([name, timestamp, os.path.basename(image_filename)])
    
    print(f"✅ Attendance saved to {csv_filename}")
    return csv_filename

def save_unrecognized_log_csv(unrecognized_faces, log_folder='unrecognized'):
    """
    Save unrecognized face info to CSV log (matches your save_unrecognized_log)
    
    Args:
        unrecognized_faces: List of dicts with image, time, source_image
        log_folder: Folder to save log file
    """
    if not unrecognized_faces:
        return
    
    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, "unrecognized_log.csv")
    is_new = not os.path.exists(log_file)
    
    with open(log_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        
        if is_new:
            writer.writerow(["Image", "Time", "Source Photo"])
        
        for entry in unrecognized_faces:
            writer.writerow([
                entry["image"], 
                entry["time"], 
                entry["source_image"]
            ])
    
    print(f"⚠️ Logged {len(unrecognized_faces)} unrecognized face(s) to {log_file}")
    return log_file

def process_classroom_image(image_path, encodings_file='encodings.pickle', tolerance=0.46):
    """
    Complete workflow: recognize students and save attendance
    Matches your complete workflow from recognize_students.py
    
    Args:
        image_path: Path to classroom image
        encodings_file: Path to pickle file
        tolerance: Recognition tolerance
    
    Returns:
        dict: Results with recognized, unrecognized, attendance_file, log_file
    """
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    print(f"\n🔍 Recognizing students from: {image_path}")
    print("="*60)
    
    # Recognize students
    recognized, unrecognized = recognize_students_from_image(
        image_path, 
        encodings_file, 
        tolerance
    )
    
    # Display results
    print("\n🎓 Recognized Students:")
    if recognized:
        for name in recognized:
            print(f"   - {name}")
    else:
        print("   ⚠️ No recognized students.")
    
    if unrecognized:
        print(f"\n❓ Unrecognized faces: {len(unrecognized)} (saved for admin review)")
    
    # Save attendance
    attendance_file = None
    if recognized:
        attendance_file = save_attendance_csv(recognized, image_path)
    
    # Save unrecognized log
    log_file = None
    if unrecognized:
        log_file = save_unrecognized_log_csv(unrecognized)
    
    print("="*60)
    
    return {
        'recognized': recognized,
        'unrecognized': unrecognized,
        'recognized_count': len(recognized),
        'unrecognized_count': len(unrecognized),
        'attendance_file': attendance_file,
        'unrecognized_log_file': log_file
    }

def batch_process_images(image_folder, encodings_file='encodings.pickle', tolerance=0.46):
    """
    Process multiple classroom images at once
    
    Args:
        image_folder: Folder containing classroom images
        encodings_file: Path to pickle file
        tolerance: Recognition tolerance
    
    Returns:
        list: Results for each image
    """
    image_folder = Path(image_folder)
    
    if not image_folder.exists():
        print(f"❌ Folder not found: {image_folder}")
        return []
    
    results = []
    image_files = [
        f for f in image_folder.iterdir() 
        if f.suffix.lower() in ['.jpg', '.jpeg', '.png']
    ]
    
    print(f"\n📁 Processing {len(image_files)} images from {image_folder}")
    print("="*60)
    
    for idx, image_path in enumerate(image_files, start=1):
        print(f"\n[{idx}/{len(image_files)}] Processing: {image_path.name}")
        result = process_classroom_image(str(image_path), encodings_file, tolerance)
        if result:
            results.append(result)
    
    # Summary
    total_recognized = sum(r['recognized_count'] for r in results)
    total_unrecognized = sum(r['unrecognized_count'] for r in results)
    
    print("\n" + "="*60)
    print("📊 BATCH PROCESSING SUMMARY")
    print("="*60)
    print(f"   Images processed:     {len(results)}")
    print(f"   Total recognized:     {total_recognized}")
    print(f"   Total unrecognized:   {total_unrecognized}")
    print("="*60 + "\n")
    
    return results

def test_ml_model_workflow():
    """
    Test the complete ML model workflow
    Simulates running your generate_encodings.py and recognize_students.py
    """
    print("\n" + "="*60)
    print("🧪 TESTING ML MODEL WORKFLOW")
    print("="*60 + "\n")
    
    # Step 1: Generate encodings
    print("STEP 1: Generating encodings from student_images/")
    print("-"*60)
    data = generate_encodings_from_folders()
    
    if data is None:
        print("\n❌ Failed to generate encodings")
        return
    
    # Step 2: Process test image
    test_images = [
        'uploads/test.jpg',
        'ml_model/uploads/grp_3tb.jpg',
        'test.jpg'
    ]
    
    test_image = None
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if test_image is None:
        print("\n⚠️ No test image found. Place a test image in uploads/")
        return
    
    print(f"\n\nSTEP 2: Processing test image")
    print("-"*60)
    result = process_classroom_image(test_image)
    
    print("\n✅ Workflow test complete!")

# Convenience function for direct usage
def quick_attendance(image_path):
    """
    Quick attendance marking - one function call
    
    Usage:
        from utils.ml_model_integration import quick_attendance
        quick_attendance('classroom.jpg')
    """
    return process_classroom_image(image_path)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'generate':
            # Generate encodings
            folder = sys.argv[2] if len(sys.argv) > 2 else 'student_images'
            generate_encodings_from_folders(folder)
        
        elif command == 'recognize':
            # Recognize from image
            if len(sys.argv) < 3:
                print("Usage: python ml_model_integration.py recognize <image_path>")
            else:
                image_path = sys.argv[2]
                process_classroom_image(image_path)
        
        elif command == 'batch':
            # Batch process
            if len(sys.argv) < 3:
                print("Usage: python ml_model_integration.py batch <image_folder>")
            else:
                folder = sys.argv[2]
                batch_process_images(folder)
        
        elif command == 'test':
            # Test workflow
            test_ml_model_workflow()
        
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python ml_model_integration.py generate [folder]")
            print("  python ml_model_integration.py recognize <image>")
            print("  python ml_model_integration.py batch <folder>")
            print("  python ml_model_integration.py test")
    else:
        print("ML Model Integration Utilities")
        print("\nUsage:")
        print("  python ml_model_integration.py generate [folder]  # Generate encodings")
        print("  python ml_model_integration.py recognize <image>  # Recognize students")
        print("  python ml_model_integration.py batch <folder>     # Batch process")
        print("  python ml_model_integration.py test               # Test workflow")