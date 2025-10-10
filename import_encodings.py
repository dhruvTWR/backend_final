#!/usr/bin/env python3
"""
Import Existing Face Encodings to New Database
Works with updated schema: branches, year, section, etc.
"""

import pickle
import os
from pathlib import Path
from models.student import Student

def get_branch_selection():
    """Show branch menu and get selection"""
    print("\nSelect Branch:")
    print("1. CSE - Computer Science Engineering")
    print("2. ECE - Electronics and Communication")
    print("3. ME - Mechanical Engineering")
    print("4. CE - Civil Engineering")
    
    branch_map = {
        '1': (1, 'CSE'),
        '2': (2, 'ECE'),
        '3': (3, 'ME'),
        '4': (4, 'CE')
    }
    
    choice = input("Enter choice (1-4): ").strip()
    return branch_map.get(choice, (1, 'CSE'))

def get_year_selection():
    """Get year selection"""
    while True:
        year = input("\nEnter year (1-4): ").strip()
        if year in ['1', '2', '3', '4']:
            return int(year)
        print("Invalid year. Please enter 1, 2, 3, or 4")

def get_section_selection():
    """Get section selection"""
    section = input("\nEnter section (A, B, C, etc.): ").strip().upper()
    return section if section else 'A'

def import_from_folders_interactive(student_images_dir='student_images'):
    """
    Import from folder structure with interactive branch/year/section selection
    """
    print("\n" + "="*60)
    print("IMPORTING FROM FOLDER STRUCTURE")
    print("="*60 + "\n")
    
    student_images_dir = Path(student_images_dir)
    
    if not student_images_dir.exists():
        print(f"Directory not found: {student_images_dir}")
        return False
    
    # Get class information
    branch_id, branch_name = get_branch_selection()
    year = get_year_selection()
    section = get_section_selection()
    
    print(f"\nImporting students for:")
    print(f"Branch: {branch_name}")
    print(f"Year: {year}")
    print(f"Section: {section}\n")
    
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Import cancelled")
        return False
    
    try:
        from services.face_recognition_service import FaceRecognitionService
        
        student_model = Student()
        face_service = FaceRecognitionService()
        
        print("\nDatabase connection established")
        print(f"Processing folder: {student_images_dir}\n")
        
        imported = 0
        skipped = 0
        errors = 0
        
        # Get existing students to avoid duplicates
        existing_students = student_model.get_students_by_class(branch_id, year, section)
        existing_roll_numbers = {s['roll_number'] for s in existing_students}
        
        # Process each person's folder
        for person_name in sorted(os.listdir(student_images_dir)):
            person_folder = student_images_dir / person_name
            
            if not person_folder.is_dir():
                continue
            
            # Extract roll number from folder name if present
            # Format: RollNumber_Name or just Name
            parts = person_name.split('_')
            if len(parts) >= 2 and parts[0].isdigit():
                roll_number = parts[0]
                name = '_'.join(parts[1:])
            else:
                # Generate roll number
                roll_number = f"{year}{section}{imported+1:03d}"
                name = person_name
            
            # Check if already exists
            if roll_number in existing_roll_numbers:
                print(f"Skipped: {name} (roll {roll_number} already exists)")
                skipped += 1
                continue
            
            # Process images in folder
            person_encodings = []
            person_images = []
            
            for filename in os.listdir(person_folder):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = person_folder / filename
                    
                    try:
                        encoding = face_service.generate_encoding(str(image_path))
                        
                        if encoding is not None:
                            person_encodings.append(encoding)
                            person_images.append(str(image_path))
                            print(f"   Encoded {filename} for {name}")
                        else:
                            print(f"   No face in {filename}")
                            
                    except Exception as e:
                        print(f"   Error processing {filename}: {e}")
                        errors += 1
            
            # Save student with first encoding
            if person_encodings:
                try:
                    email = f"{roll_number}@student.example.com"
                    
                    student_id = student_model.add_student(
                        roll_number=roll_number,
                        name=name,
                        email=email,
                        branch_id=branch_id,
                        year=year,
                        section=section,
                        face_encoding=person_encodings[0],
                        photo_path=person_images[0]
                    )
                    
                    print(f"Added: {name} (Roll: {roll_number}, ID: {student_id})")
                    imported += 1
                    
                except Exception as e:
                    print(f"Error saving {name}: {e}")
                    errors += 1
            else:
                print(f"No valid encodings for {name}")
                skipped += 1
        
        print_summary(imported, skipped, errors)
        return imported > 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def import_from_pickle_interactive(pickle_file='encodings.pickle'):
    """Import from pickle file with interactive selection"""
    print("\n" + "="*60)
    print("IMPORTING FROM PICKLE FILE")
    print("="*60 + "\n")
    
    try:
        with open(pickle_file, 'rb') as f:
            data = pickle.load(f)
        
        print(f"Loaded pickle file: {pickle_file}")
        print(f"Structure: {list(data.keys())}")
        
        if 'encodings' not in data or 'names' not in data:
            print("Invalid pickle format. Expected 'encodings' and 'names' keys.")
            return False
        
        encodings = data['encodings']
        names = data['names']
        
        if len(encodings) != len(names):
            print(f"Mismatch: {len(encodings)} encodings but {len(names)} names")
            return False
        
        print(f"Found {len(encodings)} student encodings\n")
        
        # Get class information
        branch_id, branch_name = get_branch_selection()
        year = get_year_selection()
        section = get_section_selection()
        
        print(f"\nImporting students for:")
        print(f"Branch: {branch_name}, Year: {year}, Section: {section}\n")
        
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Import cancelled")
            return False
        
        student_model = Student()
        
        # Get existing students
        existing_students = student_model.get_students_by_class(branch_id, year, section)
        existing_names = {s['name'] for s in existing_students}
        
        imported = 0
        skipped = 0
        errors = 0
        
        for idx, (encoding, name) in enumerate(zip(encodings, names), start=1):
            try:
                if name in existing_names:
                    print(f"[{idx}/{len(encodings)}] Skipped: {name} (already exists)")
                    skipped += 1
                    continue
                
                # Generate roll number
                roll_number = f"{year}{section}{imported+1:03d}"
                email = f"{roll_number}@student.example.com"
                
                # Find image
                image_path = find_student_image_in_folder(name)
                if not image_path:
                    image_path = f"student_images/{name}/default.jpg"
                
                student_id = student_model.add_student(
                    roll_number=roll_number,
                    name=name,
                    email=email,
                    branch_id=branch_id,
                    year=year,
                    section=section,
                    face_encoding=encoding,
                    photo_path=image_path
                )
                
                print(f"[{idx}/{len(encodings)}] Imported: {name} (ID: {student_id})")
                imported += 1
                
            except Exception as e:
                print(f"[{idx}/{len(encodings)}] Error importing {name}: {e}")
                errors += 1
        
        print_summary(imported, skipped, errors)
        return imported > 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def find_student_image_in_folder(student_name, base_folder='student_images'):
    """Find first image in student's folder"""
    base_folder = Path(base_folder)
    student_folder = base_folder / student_name
    
    if not student_folder.exists():
        return None
    
    for file in student_folder.iterdir():
        if file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            return str(file)
    
    return None

def print_summary(imported, skipped, errors):
    """Print import summary"""
    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    print(f"   Successfully imported: {imported}")
    print(f"   Skipped (duplicates):  {skipped}")
    print(f"   Errors:               {errors}")
    print("="*60 + "\n")
    
    if imported > 0:
        print("Import completed successfully!")

def verify_import():
    """Verify imported data"""
    try:
        student_model = Student()
        
        print("\n" + "="*60)
        print("VERIFICATION - Students in Database")
        print("="*60 + "\n")
        
        # Group by class
        print("Select class to verify:")
        branch_id, _ = get_branch_selection()
        year = get_year_selection()
        section = get_section_selection()
        
        students = student_model.get_students_by_class(branch_id, year, section)
        
        if not students:
            print(f"\nNo students found for Year {year} Section {section}")
            return
        
        print(f"\nTotal Students: {len(students)}\n")
        
        for idx, student in enumerate(students, start=1):
            photo_status = "✓" if os.path.exists(student.get('photo_path', '')) else "✗"
            print(f"{idx}. [{photo_status}] {student['name']} ({student['roll_number']})")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\nVerification error: {e}\n")

def interactive_menu():
    """Interactive import menu"""
    print("\n" + "="*60)
    print("SMART ATTENDANCE - IMPORT TOOL")
    print("="*60)
    print("\nChoose import method:")
    print("1. Import from pickle file (encodings.pickle)")
    print("2. Import from folder structure (student_images/)")
    print("3. Verify existing data")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        pickle_file = input("\nEnter pickle file path [encodings.pickle]: ").strip()
        if not pickle_file:
            pickle_file = 'encodings.pickle'
        
        if os.path.exists(pickle_file):
            import_from_pickle_interactive(pickle_file)
        else:
            print(f"File not found: {pickle_file}")
    
    elif choice == '2':
        folder = input("\nEnter student images folder [student_images]: ").strip()
        if not folder:
            folder = 'student_images'
        
        if os.path.exists(folder):
            import_from_folders_interactive(folder)
        else:
            print(f"Folder not found: {folder}")
    
    elif choice == '3':
        verify_import()
    
    elif choice == '4':
        print("\nGoodbye!")
    
    else:
        print("\nInvalid choice")

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--verify':
            verify_import()
        elif sys.argv[1] == '--help':
            print("""
Usage:
    python import_encodings.py                 # Interactive menu
    python import_encodings.py --verify        # Verify imported data
    python import_encodings.py --help          # Show this help

Note: This version requires branch, year, and section selection
      for the new database schema.
            """)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        interactive_menu()

if __name__ == '__main__':
    main()