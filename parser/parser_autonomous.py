import pdfplumber
import re
from datetime import datetime
import time

def parse_autonomous_pdf_generator(file_path, semester="Unknown", university="Autonomous", batch_size=50):
    """Generator version that yields batches of student records for real-time processing"""
    print(f"🚀 Starting optimized batch autonomous parsing of: {file_path}")
    start_time = time.time()
    
    students_processed = 0
    processed_students = set()
    batch_count = 0
    
    # Optimized PDF text extraction
    with pdfplumber.open(file_path) as pdf:
        print(f"📄 PDF has {len(pdf.pages)} pages")
        text_parts = []
        
        for i, page in enumerate(pdf.pages):
            if page.extract_text():
                text_parts.append(page.extract_text())
            
            if i > 0 and i % 10 == 0:
                print(f"📊 Processed {i+1}/{len(pdf.pages)} pages...")
        
        text = "\n".join(text_parts)
    
    # Fast semester detection
    semester_search_text = text[:5000]
    semester_patterns = [
        r'(\d+)\s*(?:st|nd|rd|th)?\s*(?:Semester|SEM|sem)',
        r'Semester\s*[:-]?\s*(\d+)',
        r'SEM\s*[:-]?\s*(\d+)',
        r'B\.?Tech\s*.*?(\d+)\s*(?:st|nd|rd|th)?\s*(?:Semester|SEM|sem)'
    ]
    
    detected_semester = None
    for pattern in semester_patterns:
        matches = re.search(pattern, semester_search_text, re.IGNORECASE)
        if matches:
            sem_num = matches.group(1)
            detected_semester = f"Semester {sem_num}"
            break
    
    if detected_semester and detected_semester != "Semester Unknown":
        semester = detected_semester
    
    print(f"🎯 Using semester: {semester}")
    
    # Enhanced pattern matching - multiple flexible patterns
    student_patterns = [
        re.compile(r'([A-Z0-9]{8,12})\s+([A-FS\-\s]+)\s+(\d+\.\d+)', re.MULTILINE),
        re.compile(r'([A-Z0-9]{8,12})\s*[\s\t]+([A-FS\-\s]+?)[\s\t]+(\d+\.\d+)', re.MULTILINE),
        re.compile(r'(\d{8,12}[A-Z]*)\s+([A-FS\-\s]+)\s+(\d+\.\d+)', re.MULTILINE),
        re.compile(r'\b([A-Z0-9]{8,12})\s+([A-FS\-\s]{8,})\s+(\d+\.\d+)\b', re.MULTILINE)
    ]
    
    # Try patterns until we find matches
    matches = []
    for pattern in student_patterns:
        potential_matches = list(pattern.finditer(text))
        if potential_matches:
            print(f"🔍 Pattern found {len(potential_matches)} matches")
            matches = potential_matches
            break
    
    # If no matches, try general patterns
    if not matches:
        print("🔍 No matches found, trying general patterns...")
        general_patterns = [
            re.compile(r'([A-Z]\d{7,11})\s+([A-FS\-\s]+)\s+(\d+\.\d+)', re.MULTILINE),
            re.compile(r'(\d{7,11}[A-Z]*)\s+([A-FS\-\s]+)\s+(\d+\.\d+)', re.MULTILINE)
        ]
        for pattern in general_patterns:
            potential_matches = list(pattern.finditer(text))
            if potential_matches:
                print(f"🎯 General pattern found {len(potential_matches)} matches")
                matches = potential_matches
                break
    
    # More flexible subject pattern to catch various formats
    subject_patterns = [
        re.compile(r'([A-Z0-9]{6,10})\s+([^A-FS\-\d]+?)(?=\s+[A-Z0-9]{6,10}|\n|$)', re.IGNORECASE),
        re.compile(r'\d+\)\s*([A-Z0-9]+)\s*[-:]?\s*(.+?)(?=\d+\)|$)', re.DOTALL),
        re.compile(r'([A-Z]{2,4}\d{2,4})\s+(.+?)(?=\s+[A-Z]{2,4}\d{2,4}|\n|$)', re.IGNORECASE)
    ]
    
    # Extract subjects using multiple patterns
    subjects_text = text[:15000]  # Increased search area
    subject_list = []
    
    for pattern in subject_patterns:
        subject_matches = pattern.findall(subjects_text)
        for code, name in subject_matches:
            code = code.strip()
            name = re.sub(r'\s+', ' ', name.strip())
            if code and name and len(code) >= 4 and len(name) > 3:
                subject_list.append((code, name))
        
        if len(subject_list) >= 5:  # If we found enough subjects, break
            break
    
    # Remove duplicates while preserving order
    seen = set()
    unique_subjects = []
    for code, name in subject_list:
        if code not in seen:
            unique_subjects.append((code, name))
            seen.add(code)
    
    subject_list = unique_subjects[:15]  # Limit to reasonable number
    num_subjects = len(subject_list)
    
    print(f"📋 Detected {num_subjects} subjects")
    upload_date = datetime.now().strftime("%Y-%m-%d")
    
    # Process students in batches
    print(f"👥 Final count: {len(matches)} student records to process")
    
    current_batch = []
    
    for i, match in enumerate(matches):
        student_id = match.group(1)
        grades_str = match.group(2).strip()
        sgpa = float(match.group(3))
        
        # Fast grade extraction
        grades = re.findall(r'[A-FS\-]+', grades_str)
        
        # Build subjects list efficiently
        subjects = []
        for j in range(min(len(grades), num_subjects)):
            if j < len(subject_list):
                subjects.append({
                    "code": subject_list[j][0],
                    "subject": subject_list[j][1],
                    "grade": grades[j],
                    "internals": 0,
                    "credits": 3.0
                })

        student_record = {
            "student_id": student_id,
            "semester": semester,
            "university": university,
            "upload_date": upload_date,
            "sgpa": sgpa,
            "subjectGrades": subjects
        }
        
        current_batch.append(student_record)
        students_processed += 1
        
        # Yield batch when it reaches the size limit
        if len(current_batch) >= batch_size:
            batch_count += 1
            print(f"🚀 Yielding batch {batch_count}: {len(current_batch)} students (Total: {students_processed})")
            yield current_batch.copy()
            current_batch = []
        
        # Show progress for large datasets
        if students_processed % 500 == 0:
            print(f"🔄 Processed {students_processed}/{len(matches)} student records...")
    
    # Yield remaining students
    if current_batch:
        batch_count += 1
        print(f"🚀 Yielding final batch {batch_count}: {len(current_batch)} students (Total: {students_processed})")
        yield current_batch

    total_time = time.time() - start_time
    print(f"✅ Completed batch parsing in {total_time:.2f} seconds - {students_processed} total students")

def parse_autonomous_pdf(file_path, semester="Unknown", university="Autonomous", streaming_callback=None):
    print(f"🚀 Starting real-time parsing of: {file_path}")
    start_time = time.time()
    
    students_processed = 0
    processed_students = set()  # Track processed students for streaming
    
    # Optimized PDF text extraction - process only necessary pages
    with pdfplumber.open(file_path) as pdf:
        print(f"📄 PDF has {len(pdf.pages)} pages")
        text_parts = []
        
        # Extract text more efficiently - limit to first few pages for metadata, then all for data
        for i, page in enumerate(pdf.pages):
            if page.extract_text():
                text_parts.append(page.extract_text())
                if i < 3:  # First 3 pages for semester detection
                    continue
            # Show progress for large PDFs
            if i > 0 and i % 10 == 0:
                print(f"📊 Processed {i+1}/{len(pdf.pages)} pages...")
        
        text = "\n".join(text_parts)
    
    extraction_time = time.time() - start_time
    print(f"⏱️ PDF text extraction took: {extraction_time:.2f} seconds")
    
    # Debug: Show sample of extracted text
    print(f"📝 Text sample (first 500 chars): {text[:500]}")
    print(f"📏 Total text length: {len(text)} characters")

    # Fast semester detection - search only first part of text
    semester_search_text = text[:5000]  # First 5000 characters should contain semester info
    semester_patterns = [
        r'(\d+)\s*(?:st|nd|rd|th)?\s*(?:Semester|SEM|sem)',
        r'Semester\s*[:-]?\s*(\d+)',
        r'SEM\s*[:-]?\s*(\d+)',
        r'B\.?Tech\s*.*?(\d+)\s*(?:st|nd|rd|th)?\s*(?:Semester|SEM|sem)'
    ]
    
    detected_semester = None
    for pattern in semester_patterns:
        matches = re.search(pattern, semester_search_text, re.IGNORECASE)
        if matches:
            sem_num = matches.group(1)
            detected_semester = f"Semester {sem_num}"
            break
    
    # Use detected semester if found
    if detected_semester and detected_semester != "Semester Unknown":
        semester = detected_semester
    
    print(f"🎯 Detected semester: {detected_semester}, Using: {semester}")

    # Enhanced subject extraction with multiple patterns
    start_subject_time = time.time()
    
    # Multiple patterns to catch different subject formats
    subject_patterns = [
        re.compile(r'\d+\)\s*([A-Z0-9]+)\s*[-:]?\s*(.+?)(?=\d+\)|$)', re.DOTALL),
        re.compile(r'([A-Z]{2,4}\d{2,4})\s+(.+?)(?=\s+[A-Z]{2,4}\d{2,4}|\n|$)', re.IGNORECASE),
        re.compile(r'([A-Z0-9]{4,8})\s+([^A-FS\-\d\n]+)(?=\s+[A-Z0-9]{4,8}|\n|$)', re.IGNORECASE),
        re.compile(r'Subject:\s*([A-Z0-9]+)\s*[-:]?\s*(.+)', re.IGNORECASE),
        re.compile(r'([A-Z0-9]{3,8})\s*[-:]\s*([^A-FS\-\d\n]{10,})', re.IGNORECASE)
    ]
    
    subject_list = []
    seen = set()
    
    # Try each pattern
    for pattern in subject_patterns:
        subject_matches = pattern.findall(text[:20000])  # Search in first 20k characters
        for code, name in subject_matches:
            code = code.strip()
            name = re.sub(r'\s+', ' ', name.strip())
            # Filter valid subjects
            if (code not in seen and len(code) >= 3 and len(name) >= 5 and 
                not re.match(r'^[A-FS\-]+$', name) and  # Not just grades
                not name.isdigit()):  # Not just numbers
                subject_list.append((code, name))
                seen.add(code)
        
        if len(subject_list) >= 6:  # Stop if we found enough subjects
            break
    
    # If no subjects found, create generic ones
    if len(subject_list) == 0:
        print("⚠️ No subjects found, creating generic subject list")
        for i in range(8):  # Assume 8 subjects
            subject_list.append((f"SUB{i+1:02d}", f"Subject {i+1}"))
    
    num_subjects = len(subject_list)
    subject_time = time.time() - start_subject_time
    print(f"📚 Found {num_subjects} subjects in {subject_time:.2f} seconds")
    if subject_list:
        print(f"📋 Sample subjects: {subject_list[:3]}")

    # Enhanced student data extraction with multiple patterns
    start_student_time = time.time()
    
    # Multiple student patterns to handle different formats
    student_patterns = [
        # Standard pattern: StudentID Grades SGPA
        re.compile(r'([A-Z0-9]{8,12})\s+([A-FS\-\s]+)\s+(\d+\.\d{1,2})', re.MULTILINE),
        # Alternative pattern with different spacing
        re.compile(r'([A-Z0-9]{8,12})\s*[\s\t]+([A-FS\-\s]+?)[\s\t]+(\d+\.\d{1,2})', re.MULTILINE),
        # Pattern for roll numbers starting with numbers
        re.compile(r'(\d{8,12}[A-Z]*)\s+([A-FS\-\s]+)\s+(\d+\.\d{1,2})', re.MULTILINE),
        # Flexible pattern with word boundaries
        re.compile(r'\b([A-Z0-9]{8,12})\s+([A-FS\-\s]{8,})\s+(\d+\.\d{1,2})\b', re.MULTILINE)
    ]
    
    all_matches = []
    for pattern in student_patterns:
        matches = list(pattern.finditer(text))
        if matches:
            print(f"🔍 Pattern found {len(matches)} matches")
            all_matches.extend(matches)
            break  # Use first successful pattern
    
    # Remove duplicates based on student ID
    seen_ids = set()
    unique_matches = []
    for match in all_matches:
        student_id = match.group(1)
        if student_id not in seen_ids:
            unique_matches.append(match)
            seen_ids.add(student_id)
    
    print(f"👥 Found {len(unique_matches)} unique student records")
    
    # If no matches found, try a more general pattern
    if len(unique_matches) == 0:
        print("🔍 No matches found, trying general patterns...")
        
        # Very general pattern - any sequence that looks like student data
        general_patterns = [
            re.compile(r'([A-Z]\d{7,11})\s+([A-FS\-\s]+)\s+(\d+\.\d+)', re.MULTILINE),
            re.compile(r'(\d{7,11}[A-Z]*)\s+([A-FS\-\s]+)\s+(\d+\.\d+)', re.MULTILINE),
            re.compile(r'([A-Z0-9]{6,15})\s+([A-FS\-\s]{6,})\s+(\d+\.\d+)', re.MULTILINE)
        ]
        
        for pattern in general_patterns:
            matches = list(pattern.finditer(text))
            if matches:
                print(f"🎯 General pattern found {len(matches)} matches")
                unique_matches = matches
                break
    
    print(f"👥 Final count: {len(unique_matches)} student records to process")
    
    results = []
    upload_date = datetime.now().strftime("%Y-%m-%d")
    
    # Process matches in batches for better memory usage
    batch_size = 100
    for i in range(0, len(unique_matches), batch_size):
        batch = unique_matches[i:i+batch_size]
        
        for match in batch:
            student_id = match.group(1)
            grades_str = match.group(2).strip()
            
            try:
                sgpa = float(match.group(3))
            except ValueError:
                print(f"⚠️ Invalid SGPA for student {student_id}, skipping...")
                continue
            
            # Enhanced grade extraction - handle various separators
            grades = re.findall(r'[A-FS][\+\-]?', grades_str)  # Include + and - modifiers
            if not grades:
                grades = re.findall(r'[A-FS]', grades_str)  # Fallback to simple grades
            
            # Build subjects list efficiently
            subjects = []
            for j in range(min(len(grades), num_subjects)):
                if j < len(subject_list):
                    grade = grades[j] if j < len(grades) else 'F'
                    subjects.append({
                        "code": subject_list[j][0],
                        "subject": subject_list[j][1],
                        "grade": grade,
                        "internals": 0,
                        "credits": 3.0
                    })
            
            # Only add if we have at least some subjects
            if subjects:
                results.append({
                    "student_id": student_id,
                    "semester": semester,
                    "university": university,
                    "upload_date": upload_date,
                    "sgpa": sgpa,
                    "subjectGrades": subjects
                })
                
                # Send real-time update if callback provided
                if streaming_callback and student_id not in processed_students:
                    processed_students.add(student_id)
                    students_processed += 1
                    
                    complete_record = {
                        "student_id": student_id,
                        "semester": semester,
                        "university": university,
                        "upload_date": upload_date,
                        "sgpa": sgpa,
                        "subjectGrades": subjects.copy()
                    }
                    
                    streaming_callback(complete_record, students_processed)
        
        # Show progress for large batches
        if len(unique_matches) > 500 and i % (batch_size * 5) == 0:
            print(f"🔄 Processed {i + len(batch)}/{len(unique_matches)} student records...")
    
    student_time = time.time() - start_student_time
    total_time = time.time() - start_time
    
    print(f"✅ Extracted {len(results)} student records in {student_time:.2f} seconds")
    print(f"🏁 Total parsing time: {total_time:.2f} seconds")
    
    if results and len(results) > 0:
        print(f"📝 Sample record: {results[0]['student_id']} has {len(results[0]['subjectGrades'])} subjects")
    else:
        print("⚠️ No student records found - check PDF format")

    return results
