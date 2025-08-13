#!/usr/bin/env python3
"""
Optimized Batch PDF Processor
Processes multiple JNTUK PDFs efficiently with detailed debugging
"""

import os
import glob
import json
import time
from datetime import datetime
from parser.parser_jntuk import parse_jntuk_pdf_generator
from parser.parser_autonomous import parse_autonomous_pdf_generator
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Configuration Constants
DEFAULT_BATCH_SIZE = 500  # Optimized for fast Firebase uploads
MAX_BATCH_SIZE = 500  # Firestore batch limit

def create_json_file_header(original_filename, format_type, exam_types, year, semesters):
    """Create initial JSON file with metadata and return file path"""
    # Create directories if they don't exist
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    exam_type_str = "_".join(exam_types)
    json_filename = f"parsed_results_{format_type}_{exam_type_str}_{timestamp}.json"
    
    # Initial JSON structure
    json_data = {
        "metadata": {
            "format": format_type,
            "exam_type": exam_types[0] if len(exam_types) == 1 else "mixed",
            "processed_at": datetime.now().isoformat(),
            "total_students": 0,
            "original_filename": original_filename,
            "processing_status": "in_progress",
            "year": year,
            "semesters": semesters
        },
        "firebase_upload": {
            "batches_completed": 0,
            "students_saved": 0,
            "students_updated": 0,
            "duplicates_skipped": 0,
            "upload_started_at": "",
            "upload_completed_at": ""
        },
        "students": []
    }
    
    json_file_path = os.path.join(data_dir, json_filename)
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    print(f"📁 Created JSON file: {json_filename}")
    return json_file_path

def append_batch_to_json(json_file_path, batch_records, batch_num, students_saved, students_updated, students_skipped):
    """Append a batch of records to the JSON file and update metadata"""
    try:
        # Read current JSON
        with open(json_file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Append new records
        json_data['students'].extend(batch_records)
        
        # Update metadata
        json_data['metadata']['total_students'] = len(json_data['students'])
        json_data['metadata']['last_batch_processed'] = batch_num
        json_data['metadata']['last_updated'] = datetime.now().isoformat()
        
        # Update Firebase status with new smart merge statistics
        json_data['firebase_upload']['batches_completed'] = batch_num
        json_data['firebase_upload']['students_saved'] = students_saved
        json_data['firebase_upload']['students_updated'] = students_updated
        json_data['firebase_upload']['duplicates_skipped'] = students_skipped
        
        # Write back to file
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"📝 Updated JSON file: Batch {batch_num}, Total students: {len(json_data['students'])}")
        
    except Exception as e:
        print(f"❌ Error updating JSON file: {str(e)}")

def find_existing_student_record(db, student_id, year, semester):
    """Find existing student record in Firebase for smart merging"""
    try:
        # Query for existing records with same student_id, year, semester
        # We check all exam types to find any existing record
        query_patterns = [
            f"{student_id}_{year.replace(' ', '_')}_{semester.replace(' ', '_')}_regular",
            f"{student_id}_{year.replace(' ', '_')}_{semester.replace(' ', '_')}_supplementary",
            f"{student_id}_{year.replace(' ', '_')}_{semester.replace(' ', '_')}_mixed"
        ]
        
        for doc_id in query_patterns:
            doc_ref = db.collection('student_results').document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                existing_data = doc.to_dict()
                return doc_ref, existing_data
        
        return None, None
        
    except Exception as e:
        print(f"⚠️ Error finding existing record for {student_id}: {e}")
        return None, None

def merge_student_subjects(existing_record, new_student, current_exam_type, upload_timestamp):
    """Intelligently merge student subjects based on priority rules"""
    merge_stats = {
        'subjects_updated': 0,
        'subjects_added': 0,
        'subjects_kept': 0,
        'merge_actions': []
    }
    
    # Get existing subjects as a dictionary for quick lookup
    existing_subjects = {}
    if existing_record and 'subjects' in existing_record:
        for subject in existing_record['subjects']:
            subject_code = subject.get('subject_code')
            if subject_code:
                existing_subjects[subject_code] = subject
    
    # Start with existing subjects
    merged_subjects = existing_subjects.copy()
    
    # Process each subject from new PDF
    new_subjects = new_student.get('subjects', [])
    for new_subject in new_subjects:
        subject_code = new_subject.get('subject_code')
        if not subject_code:
            continue
            
        existing_subject = existing_subjects.get(subject_code)
        
        if existing_subject:
            # Subject exists - apply priority rules
            should_update = should_update_subject(
                existing_subject, 
                new_subject, 
                existing_record.get('examType', 'regular'),
                current_exam_type,
                existing_record.get('uploadedAt', ''),
                upload_timestamp
            )
            
            if should_update:
                # Update subject with new data
                updated_subject = new_subject.copy()
                updated_subject['source'] = current_exam_type
                updated_subject['updated_at'] = upload_timestamp
                merged_subjects[subject_code] = updated_subject
                
                merge_stats['subjects_updated'] += 1
                merge_stats['merge_actions'].append({
                    'type': 'UPDATE',
                    'subject_code': subject_code,
                    'old_result': f"{existing_subject.get('result', 'Unknown')} (Grade: {existing_subject.get('grade', 'N/A')})",
                    'new_result': f"{new_subject.get('result', 'Unknown')} (Grade: {new_subject.get('grade', 'N/A')})",
                    'reason': get_update_reason(existing_record.get('examType', 'regular'), current_exam_type, upload_timestamp)
                })
            else:
                # Keep existing subject
                merge_stats['subjects_kept'] += 1
        else:
            # New subject - add it
            new_subject_copy = new_subject.copy()
            new_subject_copy['source'] = current_exam_type
            new_subject_copy['updated_at'] = upload_timestamp
            merged_subjects[subject_code] = new_subject_copy
            
            merge_stats['subjects_added'] += 1
            merge_stats['merge_actions'].append({
                'type': 'ADD',
                'subject_code': subject_code,
                'new_result': f"{new_subject.get('result', 'Unknown')} (Grade: {new_subject.get('grade', 'N/A')})",
                'reason': 'New subject not in existing record'
            })
    
    # Convert back to list format
    final_subjects = list(merged_subjects.values())
    
    return final_subjects, merge_stats

def should_update_subject(existing_subject, new_subject, existing_exam_type, new_exam_type, existing_timestamp, new_timestamp):
    """Determine if a subject should be updated based on priority rules"""
    # Rule 1: SUPPLY always overwrites REGULAR
    if new_exam_type == 'supplementary' and existing_exam_type == 'regular':
        return True
    
    # Rule 2: Newer uploads always win (timestamp priority)
    if new_timestamp > existing_timestamp:
        return True
    
    # Rule 3: Same exam type, same timestamp - keep existing (no update needed)
    return False

def get_update_reason(existing_exam_type, new_exam_type, timestamp):
    """Get human-readable reason for the update"""
    if new_exam_type == 'supplementary' and existing_exam_type == 'regular':
        return "SUPPLY overwrites REGULAR (newer upload)"
    elif new_exam_type == 'regular' and existing_exam_type == 'supplementary':
        return "Newer REGULAR upload"
    else:
        return "Newer upload takes priority"

def smart_batch_upload_to_firebase(batch_records, year, semesters, exam_types, format_type, doc_id):
    """Upload a batch of records to Firebase with intelligent subject-level merging"""
    try:
        # Check if Firebase is available
        db = firestore.client()
        if db is None:
            print("⚠️ Firebase not available - skipping upload")
            return 0, 0, 0, ["Firebase not available"]
            
        students_saved = 0
        students_updated = 0
        duplicates_skipped = 0
        errors = []
        
        # Current upload timestamp
        upload_timestamp = datetime.now().isoformat()
        current_exam_type = exam_types[0] if exam_types else 'regular'
        
        print(f"🧠 Starting smart merge processing for {len(batch_records)} students...")
        
        for student in batch_records:
            try:
                student_id = student.get('student_id')
                if not student_id:
                    errors.append("Missing student_id")
                    continue
                
                detected_semester = student.get('semester', semesters[0] if semesters else 'Unknown')
                
                # Step 1: Find existing record
                existing_doc_ref, existing_record = find_existing_student_record(
                    db, student_id, year, detected_semester
                )
                
                if existing_record:
                    # Step 2: Smart merge with existing record
                    print(f"🔄 Merging {student_id} - {detected_semester} (existing record found)")
                    
                    # Merge subjects intelligently
                    merged_subjects, merge_stats = merge_student_subjects(
                        existing_record, student, current_exam_type, upload_timestamp
                    )
                    
                    # Create updated record
                    updated_student_data = existing_record.copy()
                    updated_student_data.update({
                        'subjects': merged_subjects,
                        'examType': 'mixed' if current_exam_type != existing_record.get('examType', 'regular') else current_exam_type,
                        'lastUpdatedAt': upload_timestamp,
                        'lastUploadId': doc_id,
                        'totalSubjects': len(merged_subjects),
                        'mergeHistory': existing_record.get('mergeHistory', []) + [{
                            'uploadedAt': upload_timestamp,
                            'examType': current_exam_type,
                            'subjectsUpdated': merge_stats['subjects_updated'],
                            'subjectsAdded': merge_stats['subjects_added']
                        }]
                    })
                    
                    # Update the existing document
                    existing_doc_ref.update(updated_student_data)
                    students_updated += 1
                    
                    # Log merge actions
                    for action in merge_stats['merge_actions']:
                        if action['type'] == 'UPDATE':
                            print(f"   🔄 UPDATE {action['subject_code']}: {action['old_result']} → {action['new_result']}")
                        elif action['type'] == 'ADD':
                            print(f"   ➕ ADD {action['subject_code']}: {action['new_result']}")
                    
                    print(f"   📊 Merge summary: {merge_stats['subjects_updated']} updated, {merge_stats['subjects_added']} added, {merge_stats['subjects_kept']} kept")
                    
                else:
                    # Step 3: Create new record (no existing record found)
                    print(f"➕ Creating new record for {student_id} - {detected_semester}")
                    
                    # Add metadata to subjects
                    subjects_with_metadata = []
                    for subject in student.get('subjects', []):
                        subject_copy = subject.copy()
                        subject_copy['source'] = current_exam_type
                        subject_copy['updated_at'] = upload_timestamp
                        subjects_with_metadata.append(subject_copy)
                    
                    # Create document ID
                    student_doc_id = f"{student_id}_{year.replace(' ', '_')}_{detected_semester.replace(' ', '_')}_{current_exam_type}"
                    
                    # Prepare student data for Firebase
                    firebase_student_data = student.copy()
                    firebase_student_data.update({
                        'year': year,
                        'semester': detected_semester,
                        'examType': current_exam_type,
                        'availableSemesters': semesters,
                        'availableExamTypes': exam_types,
                        'format': format_type,
                        'uploadId': doc_id,
                        'uploadedAt': firestore.SERVER_TIMESTAMP,
                        'lastUpdatedAt': upload_timestamp,
                        'batchProcessed': True,
                        'subjects': subjects_with_metadata,
                        'totalSubjects': len(subjects_with_metadata),
                        'mergeHistory': [{
                            'uploadedAt': upload_timestamp,
                            'examType': current_exam_type,
                            'subjectsAdded': len(subjects_with_metadata),
                            'initialUpload': True
                        }]
                    })
                    
                    # Create new document
                    doc_ref = db.collection('student_results').document(student_doc_id)
                    doc_ref.set(firebase_student_data)
                    students_saved += 1
                    
                    print(f"   ✅ Created with {len(subjects_with_metadata)} subjects")
                    
            except Exception as e:
                # Handle Firebase authentication errors gracefully
                if 'invalid_grant' in str(e).lower() or 'jwt signature' in str(e).lower():
                    print("❌ Firebase authentication error during student processing")
                    return students_saved, students_updated, duplicates_skipped, ["Firebase authentication failed"]
                errors.append(f"Error processing {student.get('student_id', 'unknown')}: {str(e)}")
        
        return students_saved, students_updated, duplicates_skipped, errors
        
    except Exception as e:
        # Handle Firebase authentication errors at the top level
        if 'invalid_grant' in str(e).lower() or 'jwt signature' in str(e).lower():
            print("❌ Firebase authentication error - service account key may be invalid")
            return 0, 0, 0, ["Firebase authentication failed - invalid service account key"]
        return 0, 0, 0, [f"Firebase error: {str(e)}"]

def setup_firebase():
    """Initialize Firebase if not already done with enhanced error handling"""
    try:
        # Check if Firebase is already initialized
        app = firebase_admin.get_app()
        print("✅ Firebase already initialized")
        return firestore.client(app), storage.bucket('plant-ec218.firebasestorage.app')
    except ValueError:
        # Initialize Firebase with enhanced error handling
        try:
            cred = credentials.Certificate('serviceAccount.json')
            app = firebase_admin.initialize_app(cred, {
                'storageBucket': 'plant-ec218.firebasestorage.app'
            })
            print("✅ Firebase initialized")
            
            # Test the connection immediately
            db = firestore.client(app)
            bucket = storage.bucket('plant-ec218.firebasestorage.app')
            
            # Quick test to verify authentication
            try:
                test_collection = db.collection('connection_test')
                test_doc = test_collection.document('test')
                test_doc.set({'test': True, 'timestamp': firestore.SERVER_TIMESTAMP})
                test_doc.delete()  # Clean up
                print("✅ Firebase authentication verified")
                return db, bucket
            except Exception as auth_error:
                if 'invalid_grant' in str(auth_error).lower() or 'jwt signature' in str(auth_error).lower():
                    print("❌ Firebase authentication failed: Invalid JWT signature")
                    print("⚠️ Running in local-only mode (no Firebase uploads)")
                    return None, None
                else:
                    raise auth_error
                    
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            print("⚠️ Running in local-only mode (no Firebase uploads)")
            return None, None
    except Exception as e:
        print(f"❌ Firebase setup error: {e}")
        print("⚠️ Running in local-only mode (no Firebase uploads)")
        return None, None

def detect_pdf_metadata(pdf_path):
    """Detect format (JNTUK/Autonomous), semester and year from PDF content analysis"""
    filename = os.path.basename(pdf_path).lower()
    
    # Detect format first
    format_type = "unknown"
    year = "Unknown"
    semester = "Unknown"
    exam_type = "regular"
    
    # JNTUK indicators
    jntuk_keywords = ['jntuk', 'b.tech', 'btech', 'jawaharlal nehru technological university']
    
    # Autonomous indicators  
    autonomous_keywords = ['autonomous', 'college', 'engineering', 'degree', 'affiliated']
    
    try:
        import pdfplumber
        import re
        
        print(f"🔍 Analyzing PDF content to detect metadata...")
        
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                print("⚠️ PDF has no pages, using filename fallback")
                return fallback_filename_detection(filename)
            
            # Analyze first few pages for comprehensive detection
            pages_to_analyze = min(3, len(pdf.pages))
            combined_text = ""
            
            for i in range(pages_to_analyze):
                page_text = pdf.pages[i].extract_text()
                if page_text:
                    combined_text += page_text.lower() + " "
            
            if not combined_text.strip():
                print("⚠️ Could not extract text from PDF, using filename fallback")
                return fallback_filename_detection(filename)
            
            print(f"📄 Extracted {len(combined_text)} characters from {pages_to_analyze} pages")
            
            # Detect format from content
            if any(keyword in combined_text for keyword in jntuk_keywords):
                format_type = "jntuk"
                print(f"✅ Detected format: JNTUK")
            elif any(keyword in combined_text for keyword in autonomous_keywords):
                format_type = "autonomous"
                print(f"✅ Detected format: Autonomous")
            else:
                # Fallback to filename analysis
                if any(keyword in filename for keyword in jntuk_keywords):
                    format_type = "jntuk"
                elif any(keyword in filename for keyword in autonomous_keywords):
                    format_type = "autonomous"
                else:
                    format_type = "jntuk"  # Default
                print(f"⚠️ Format detection from filename: {format_type}")
            
            # Detect year from content - Look for patterns like "I B.Tech", "II B.Tech", etc.
            # Order matters - more specific patterns first
            year_patterns = [
                r'results\s+of\s+ii\s+b\.?tech\s+i\s+semester',    # Results of II B.Tech I Semester -> 2nd Year
                r'results\s+of\s+ii\s+b\.?tech\s+ii\s+semester',   # Results of II B.Tech II Semester -> 2nd Year
                r'results\s+of\s+iii\s+b\.?tech\s+i\s+semester',   # Results of III B.Tech I Semester -> 3rd Year
                r'results\s+of\s+iii\s+b\.?tech\s+ii\s+semester',  # Results of III B.Tech II Semester -> 3rd Year
                r'results\s+of\s+iv\s+b\.?tech\s+i\s+semester',    # Results of IV B.Tech I Semester -> 4th Year
                r'results\s+of\s+iv\s+b\.?tech\s+ii\s+semester',   # Results of IV B.Tech II Semester -> 4th Year
                r'results\s+of\s+i\s+b\.?tech\s+i\s+semester',     # Results of I B.Tech I Semester -> 1st Year
                r'results\s+of\s+i\s+b\.?tech\s+ii\s+semester',    # Results of I B.Tech II Semester -> 1st Year
                r'ii\s+b\.?tech\s+i\s+semester',     # II B.Tech I Semester -> 2nd Year
                r'ii\s+b\.?tech\s+ii\s+semester',    # II B.Tech II Semester -> 2nd Year
                r'iii\s+b\.?tech\s+i\s+semester',    # III B.Tech I Semester -> 3rd Year
                r'iii\s+b\.?tech\s+ii\s+semester',   # III B.Tech II Semester -> 3rd Year
                r'iv\s+b\.?tech\s+i\s+semester',     # IV B.Tech I Semester -> 4th Year
                r'iv\s+b\.?tech\s+ii\s+semester',    # IV B.Tech II Semester -> 4th Year
                r'i\s+b\.?tech\s+i\s+semester',      # I B.Tech I Semester -> 1st Year
                r'i\s+b\.?tech\s+ii\s+semester',     # I B.Tech II Semester -> 1st Year  
                r'1st\s+year|first\s+year',          # 1st Year, First Year
                r'2nd\s+year|second\s+year',         # 2nd Year, Second Year
                r'3rd\s+year|third\s+year',          # 3rd Year, Third Year
                r'4th\s+year|fourth\s+year'          # 4th Year, Fourth Year
            ]
            
            year_found = False
            for pattern in year_patterns:
                match = re.search(pattern, combined_text)
                if match:
                    matched_text = match.group(0)
                    print(f"🎯 Found year pattern: '{matched_text}'")
                    
                    if ('results of ii b.tech' in matched_text or 'ii b.tech' in matched_text):
                        year = "2nd Year"
                    elif ('results of iii b.tech' in matched_text or 'iii b.tech' in matched_text):
                        year = "3rd Year"
                    elif ('results of iv b.tech' in matched_text or 'iv b.tech' in matched_text):
                        year = "4th Year"
                    elif ('results of i b.tech' in matched_text or 'i b.tech' in matched_text or 
                          'first year' in matched_text or '1st year' in matched_text):
                        year = "1st Year"
                    elif ('second year' in matched_text or '2nd year' in matched_text):
                        year = "2nd Year"
                    elif ('third year' in matched_text or '3rd year' in matched_text):
                        year = "3rd Year"
                    elif ('fourth year' in matched_text or '4th year' in matched_text):
                        year = "4th Year"
                    year_found = True
                    print(f"✅ Detected year from content: {year}")
                    break
            
            if not year_found:
                print("⚠️ Could not detect year from content, trying filename analysis")
                year = extract_year_from_filename(filename)
            
            # Detect semester from content - Look for Roman numerals and patterns
            # Order matters - more specific patterns first
            semester_patterns = [
                r'results\s+of\s+ii\s+b\.?tech\s+i\s+semester',     # Results of II B.Tech I Semester -> Semester 3
                r'results\s+of\s+ii\s+b\.?tech\s+ii\s+semester',    # Results of II B.Tech II Semester -> Semester 4
                r'results\s+of\s+iii\s+b\.?tech\s+i\s+semester',    # Results of III B.Tech I Semester -> Semester 5
                r'results\s+of\s+iii\s+b\.?tech\s+ii\s+semester',   # Results of III B.Tech II Semester -> Semester 6
                r'results\s+of\s+iv\s+b\.?tech\s+i\s+semester',     # Results of IV B.Tech I Semester -> Semester 7
                r'results\s+of\s+iv\s+b\.?tech\s+ii\s+semester',    # Results of IV B.Tech II Semester -> Semester 8
                r'results\s+of\s+i\s+b\.?tech\s+i\s+semester',      # Results of I B.Tech I Semester -> Semester 1
                r'results\s+of\s+i\s+b\.?tech\s+ii\s+semester',     # Results of I B.Tech II Semester -> Semester 2
                r'ii\s+b\.?tech\s+i\s+semester',     # II B.Tech I Semester -> Semester 3
                r'ii\s+b\.?tech\s+ii\s+semester',    # II B.Tech II Semester -> Semester 4
                r'iii\s+b\.?tech\s+i\s+semester',    # III B.Tech I Semester -> Semester 5
                r'iii\s+b\.?tech\s+ii\s+semester',   # III B.Tech II Semester -> Semester 6
                r'iv\s+b\.?tech\s+i\s+semester',     # IV B.Tech I Semester -> Semester 7
                r'iv\s+b\.?tech\s+ii\s+semester',    # IV B.Tech II Semester -> Semester 8
                r'i\s+b\.?tech\s+i\s+semester',      # I B.Tech I Semester -> Semester 1
                r'i\s+b\.?tech\s+ii\s+semester',     # I B.Tech II Semester -> Semester 2
                r'btech\s+2-1|2-1\s+result',         # BTECH 2-1 (2nd year, 1st semester = Semester 3)
                r'semester\s+([ivx]+)',               # Semester I, Semester II, etc.
                r'([ivx]+)\s+semester',               # I Semester, II Semester, etc.
                r'sem\s*-?\s*(\d)',                   # Sem 1, Sem-2, etc.
                r'(\d)(?:st|nd|rd|th)?\s+sem',        # 1st Sem, 2nd Sem, etc.
            ]
            
            semester_found = False
            for pattern in semester_patterns:
                match = re.search(pattern, combined_text)
                if match:
                    matched_text = match.group(0)
                    print(f"🎯 Found semester pattern: '{matched_text}'")
                    
                    # Map complex patterns to semester numbers
                    if 'results of ii b.tech i semester' in matched_text or 'ii b.tech i semester' in matched_text:
                        semester = "Semester 3"  # 2nd year, 1st semester
                    elif 'results of ii b.tech ii semester' in matched_text or 'ii b.tech ii semester' in matched_text:
                        semester = "Semester 4"  # 2nd year, 2nd semester
                    elif 'results of iii b.tech i semester' in matched_text or 'iii b.tech i semester' in matched_text:
                        semester = "Semester 5"
                    elif 'results of iii b.tech ii semester' in matched_text or 'iii b.tech ii semester' in matched_text:
                        semester = "Semester 6"
                    elif 'results of iv b.tech i semester' in matched_text or 'iv b.tech i semester' in matched_text:
                        semester = "Semester 7"
                    elif 'results of iv b.tech ii semester' in matched_text or 'iv b.tech ii semester' in matched_text:
                        semester = "Semester 8"
                    elif 'results of i b.tech i semester' in matched_text or 'i b.tech i semester' in matched_text:
                        semester = "Semester 1"
                    elif 'results of i b.tech ii semester' in matched_text or 'i b.tech ii semester' in matched_text:
                        semester = "Semester 2"
                    elif 'btech 2-1' in matched_text or '2-1 result' in matched_text:
                        semester = "Semester 3"  # 2-1 means 2nd year, 1st semester = Semester 3
                    # Handle standalone semester patterns
                    elif 'semester i' in matched_text or 'i semester' in matched_text:
                        # Need to check the year context for standalone semester patterns
                        if year == "2nd Year":
                            semester = "Semester 3"
                        elif year == "3rd Year":
                            semester = "Semester 5"
                        elif year == "4th Year":
                            semester = "Semester 7"
                        else:
                            semester = "Semester 1"
                    elif 'semester ii' in matched_text or 'ii semester' in matched_text:
                        if year == "2nd Year":
                            semester = "Semester 4"
                        elif year == "3rd Year":
                            semester = "Semester 6"
                        elif year == "4th Year":
                            semester = "Semester 8"
                        else:
                            semester = "Semester 2"
                    elif 'semester iii' in matched_text or 'iii semester' in matched_text:
                        semester = "Semester 3"
                    elif 'semester iv' in matched_text or 'iv semester' in matched_text:
                        semester = "Semester 4"
                    elif 'semester v' in matched_text or 'v semester' in matched_text:
                        semester = "Semester 5"
                    elif 'semester vi' in matched_text or 'vi semester' in matched_text:
                        semester = "Semester 6"
                    elif 'semester vii' in matched_text or 'vii semester' in matched_text:
                        semester = "Semester 7"
                    elif 'semester viii' in matched_text or 'viii semester' in matched_text:
                        semester = "Semester 8"
                    # Handle numeric patterns
                    elif '1' in matched_text:
                        if year == "2nd Year":
                            semester = "Semester 3"
                        elif year == "3rd Year":
                            semester = "Semester 5"
                        elif year == "4th Year":
                            semester = "Semester 7"
                        else:
                            semester = "Semester 1"
                    elif '2' in matched_text:
                        if year == "2nd Year":
                            semester = "Semester 4"
                        elif year == "3rd Year":
                            semester = "Semester 6"
                        elif year == "4th Year":
                            semester = "Semester 8"
                        else:
                            semester = "Semester 2"
                    elif '3' in matched_text:
                        semester = "Semester 3"
                    elif '4' in matched_text:
                        semester = "Semester 4"
                    elif '5' in matched_text:
                        semester = "Semester 5"
                    elif '6' in matched_text:
                        semester = "Semester 6"
                    elif '7' in matched_text:
                        semester = "Semester 7"
                    elif '8' in matched_text:
                        semester = "Semester 8"
                    
                    semester_found = True
                    print(f"✅ Detected semester from content: {semester}")
                    break
                    
            # Additional check for filename patterns if not found in content
            if not semester_found:
                # Check filename for 2-1 pattern specifically
                if re.search(r'btech\s+2-1|2-1\s+result', filename):
                    semester = "Semester 3"  # 2-1 means 2nd year, 1st semester = Semester 3
                    semester_found = True
                    print(f"✅ Detected semester from filename pattern: {semester}")
            
            if not semester_found:
                print("⚠️ Could not detect semester from content, trying filename analysis")
                semester = extract_semester_from_filename(filename)
            
            # Detect exam type from content
            if re.search(r'supplementary|supply|supple', combined_text):
                exam_type = "supplementary"
                print(f"✅ Detected exam type: {exam_type}")
            elif re.search(r'regular|main', combined_text):
                exam_type = "regular"
                print(f"✅ Detected exam type: {exam_type}")
            else:
                # Fallback to filename
                if "supplementary" in filename or "supply" in filename:
                    exam_type = "supplementary"
                else:
                    exam_type = "regular"
                print(f"⚠️ Exam type from filename: {exam_type}")
    
    except Exception as e:
        print(f"❌ Error analyzing PDF content: {e}")
        print("⚠️ Falling back to filename analysis")
        return fallback_filename_detection(filename)
    
    print(f"📊 Final detection - Format: {format_type}, Year: {year}, Semester: {semester}, Exam Type: {exam_type}")
    
    return {
        'year': year,
        'semesters': [semester],
        'exam_types': [exam_type],
        'format': format_type
    }

def extract_year_from_filename(filename):
    """Extract year from filename as fallback"""
    import re
    
    print(f"🔍 Analyzing filename for year: {filename}")
    
    # Try various year patterns in filename
    year_patterns = [
        (r'i\s+b\.?tech\s+i\s+semester', "1st Year"),           # I B.Tech I Semester
        (r'i\s+b\.?tech\s+ii\s+semester', "1st Year"),          # I B.Tech II Semester
        (r'1st\s+btech\s+1st\s+sem', "1st Year"),               # 1st BTech 1st Sem
        (r'btech\s+2-1', "1st Year"),                           # BTECH 2-1 (2nd semester of 1st year)
        (r'ii\s+b\.?tech', "2nd Year"),                         # II B.Tech
        (r'2nd\s+year', "2nd Year"),                            # 2nd Year
        (r'iii\s+b\.?tech', "3rd Year"),                        # III B.Tech
        (r'3rd\s+year', "3rd Year"),                            # 3rd Year
        (r'iv\s+b\.?tech', "4th Year"),                         # IV B.Tech
        (r'4th\s+year', "4th Year"),                            # 4th Year
    ]
    
    for pattern, year_name in year_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            print(f"📁 Extracted year from filename: {year_name} (pattern: {pattern})")
            return year_name
    
    print("❓ Could not determine year from filename")
    return "Unknown"

def extract_semester_from_filename(filename):
    """Extract semester from filename as fallback"""
    import re
    
    print(f"🔍 Analyzing filename for semester: {filename}")
    
    # Try various semester patterns in filename
    semester_patterns = [
        (r'i\s+b\.?tech\s+i\s+semester', "Semester 1"),         # I B.Tech I Semester
        (r'1st\s+btech\s+1st\s+sem', "Semester 1"),             # 1st BTech 1st Sem
        (r'1st\s+sem', "Semester 1"),                           # 1st Sem
        (r'i\s+semester', "Semester 1"),                        # I Semester
        
        (r'i\s+b\.?tech\s+ii\s+semester', "Semester 2"),        # I B.Tech II Semester
        (r'btech\s+2-1', "Semester 3"),                         # BTECH 2-1 (2nd year, 1st semester)
        (r'2nd\s+sem', "Semester 2"),                           # 2nd Sem
        (r'ii\s+semester', "Semester 2"),                       # II Semester
        
        (r'ii\s+b\.?tech\s+i\s+semester', "Semester 3"),        # II B.Tech I Semester
        (r'3rd\s+sem', "Semester 3"),                           # 3rd Sem
        (r'iii\s+semester', "Semester 3"),                      # III Semester
        
        (r'ii\s+b\.?tech\s+ii\s+semester', "Semester 4"),       # II B.Tech II Semester
        (r'4th\s+sem', "Semester 4"),                           # 4th Sem
        (r'iv\s+semester', "Semester 4"),                       # IV Semester
        
        (r'iii\s+b\.?tech\s+i\s+semester', "Semester 5"),       # III B.Tech I Semester
        (r'5th\s+sem', "Semester 5"),                           # 5th Sem
        (r'v\s+semester', "Semester 5"),                        # V Semester
        
        (r'iii\s+b\.?tech\s+ii\s+semester', "Semester 6"),      # III B.Tech II Semester
        (r'6th\s+sem', "Semester 6"),                           # 6th Sem
        (r'vi\s+semester', "Semester 6"),                       # VI Semester
        
        (r'iv\s+b\.?tech\s+i\s+semester', "Semester 7"),        # IV B.Tech I Semester
        (r'7th\s+sem', "Semester 7"),                           # 7th Sem
        (r'vii\s+semester', "Semester 7"),                      # VII Semester
        
        (r'iv\s+b\.?tech\s+ii\s+semester', "Semester 8"),       # IV B.Tech II Semester
        (r'8th\s+sem', "Semester 8"),                           # 8th Sem
        (r'viii\s+semester', "Semester 8"),                     # VIII Semester
    ]
    
    for pattern, semester_name in semester_patterns:
        if re.search(pattern, filename, re.IGNORECASE):
            print(f"📁 Extracted semester from filename: {semester_name} (pattern: {pattern})")
            return semester_name
    
    print("❓ Could not determine semester from filename")
    return "Unknown"

def fallback_filename_detection(filename):
    """Fallback detection when PDF content analysis fails"""
    print("⚠️ Using fallback filename detection")
    
    # Basic format detection
    jntuk_keywords = ['jntuk', 'b.tech', 'btech', 'jawaharlal nehru technological university']
    autonomous_keywords = ['autonomous', 'college', 'engineering', 'degree', 'affiliated']
    
    if any(keyword in filename for keyword in jntuk_keywords):
        format_type = "jntuk"
    elif any(keyword in filename for keyword in autonomous_keywords):
        format_type = "autonomous"
    else:
        format_type = "jntuk"  # Default
    
    year = extract_year_from_filename(filename)
    semester = extract_semester_from_filename(filename)
    
    # Exam type
    exam_type = "supplementary" if ("supplementary" in filename or "supply" in filename) else "regular"
    
    return {
        'year': year,
        'semesters': [semester],
        'exam_types': [exam_type],
        'format': format_type
    }

def process_single_pdf(pdf_path, db, bucket, batch_size=DEFAULT_BATCH_SIZE):
    """Process a single PDF with configurable batch processing and Firebase fallback"""
    print(f"\n🚀 Processing: {os.path.basename(pdf_path)}")
    print(f"⚙️ Using batch size: {batch_size}")
    
    # Check Firebase availability
    firebase_available = db is not None and bucket is not None
    if firebase_available:
        print("✅ Firebase enabled")
    else:
        print("⚠️ Firebase disabled - local JSON only")
    
    start_time = time.time()
    
    # Detect metadata
    metadata = detect_pdf_metadata(pdf_path)
    print(f"📊 Detected: {metadata}")
    
    # Initialize JSON file and get timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = create_json_file_header(
        os.path.basename(pdf_path),
        metadata['format'], 
        metadata['exam_types'], 
        metadata['year'], 
        metadata['semesters']
    )
    doc_id = f"upload_{timestamp}"
    
    # Process PDF in batches
    total_students = 0
    total_saved = 0
    total_updated = 0
    total_skipped = 0
    batch_count = 0
    
    try:
        print(f"🔍 Starting batch processing with {batch_size} records per batch...")
        
        # Choose the appropriate parser based on format
        if metadata['format'] == 'autonomous':
            print(f"🏛️ Using Autonomous parser for {metadata['format']} format")
            parser_generator = parse_autonomous_pdf_generator(pdf_path, batch_size=batch_size)
        else:
            print(f"🎓 Using JNTUK parser for {metadata['format']} format")
            parser_generator = parse_jntuk_pdf_generator(pdf_path, batch_size=batch_size)
        
        for batch_records in parser_generator:
            batch_count += 1
            current_batch_size = len(batch_records)
            total_students += current_batch_size
            
            print(f"📦 Processing batch {batch_count}: {current_batch_size} students")
            
            # Upload to Firebase if available
            if firebase_available:
                saved, updated, skipped, errors = smart_batch_upload_to_firebase(
                    batch_records, 
                    metadata['year'], 
                    metadata['semesters'], 
                    metadata['exam_types'], 
                    metadata['format'], 
                    doc_id
                )
                
                # Check if Firebase authentication failed
                if errors and any('authentication failed' in str(error).lower() for error in errors):
                    print("⚠️ Firebase authentication failed - switching to local-only mode")
                    firebase_available = False
                    saved, updated, skipped = 0, 0, 0
            else:
                # Local-only mode
                saved, updated, skipped, errors = 0, 0, 0, []
                print("📝 Saving to JSON only (Firebase disabled)")
            
            # Always append to JSON with the results
            append_batch_to_json(json_path, batch_records, batch_count, saved, updated, skipped)
            
            total_saved += saved
            total_updated += updated
            total_skipped += skipped
            
            if errors:
                print(f"⚠️ Batch {batch_count} errors: {errors}")
            
            if firebase_available:
                print(f"✅ Batch {batch_count} complete: {saved} new, {updated} updated, {skipped} skipped")
            else:
                print(f"✅ Batch {batch_count} complete: {current_batch_size} saved to JSON")
        
        # Finalize JSON file
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Update final metadata
            json_data['metadata']['processing_status'] = 'completed'
            json_data['metadata']['total_students'] = total_students
            json_data['metadata']['completed_at'] = datetime.now().isoformat()
            json_data['metadata']['firebase_enabled'] = firebase_available
            json_data['firebase_upload']['upload_completed_at'] = datetime.now().isoformat()
            json_data['firebase_upload']['final_saved_count'] = total_saved
            json_data['firebase_upload']['final_updated_count'] = total_updated
            json_data['firebase_upload']['final_skipped_count'] = total_skipped
            json_data['firebase_upload']['firebase_available'] = firebase_available
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
        except Exception as e:
            print(f"⚠️ Error finalizing JSON: {e}")
        
        processing_time = time.time() - start_time
        
        print(f"🎯 PDF Processing Complete!")
        print(f"📊 Total batches processed: {batch_count}")
        print(f"👥 Total students: {total_students}")
        if firebase_available:
            print(f"➕ New records created: {total_saved}")
            print(f"🔄 Existing records updated: {total_updated}")
            print(f"⏭️ Records skipped: {total_skipped}")
        else:
            print(f"📝 Saved to JSON: {total_students}")
        print(f"⚡ Records per second: {total_students/processing_time:.1f}")
        print(f"⏱️ Processing time: {processing_time:.2f} seconds")
        print(f"📁 JSON saved: {json_path}")
        
        return {
            'success': True,
            'total_students': total_students,
            'saved': total_saved,
            'updated': total_updated,
            'skipped': total_skipped,
            'processing_time': processing_time,
            'json_path': json_path,
            'batch_size_used': batch_size,
            'batches_processed': batch_count,
            'firebase_enabled': firebase_available
        }
        
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")
        return {
            'success': False,
            'error': str(e),
            'total_students': total_students,
            'processing_time': time.time() - start_time
        }

def main(batch_size=DEFAULT_BATCH_SIZE):
    """Main batch processing function with configurable batch size"""
    print("🚀 Starting Optimized Batch PDF Processing")
    print(f"⚙️ Configuration: Batch size = {batch_size}")
    print("=" * 60)
    
    # Validate batch size
    if batch_size > MAX_BATCH_SIZE:
        print(f"⚠️ Warning: Batch size {batch_size} exceeds Firebase limit {MAX_BATCH_SIZE}")
        batch_size = MAX_BATCH_SIZE
        print(f"⚙️ Adjusted batch size to: {batch_size}")
    
    # Setup Firebase
    db, bucket = setup_firebase()
    
    # Find all PDF files and deduplicate
    pdf_files = []
    pdf_patterns = [
        "*.pdf", "*.PDF"
    ]
    
    for pattern in pdf_patterns:
        pdf_files.extend(glob.glob(pattern, recursive=False))
    
    # Remove duplicates by converting to set and back
    pdf_files = list(set(pdf_files))
    
    # Filter PDFs for both JNTUK and Autonomous formats
    supported_pdfs = []
    for pdf in pdf_files:
        filename = os.path.basename(pdf).lower()
        # Check for JNTUK keywords
        jntuk_keywords = ['btech', 'b.tech', 'semester', 'result', 'jntuk', 'examination', 'jawaharlal nehru']
        # Check for Autonomous keywords
        autonomous_keywords = ['autonomous', 'college', 'engineering', 'degree', 'affiliated']
        
        if (any(keyword in filename for keyword in jntuk_keywords) or 
            any(keyword in filename for keyword in autonomous_keywords)):
            supported_pdfs.append(pdf)
    
    print(f"📁 Found {len(supported_pdfs)} supported PDF files (JNTUK + Autonomous):")
    for pdf in supported_pdfs:
        print(f"   📄 {os.path.basename(pdf)}")
    
    if not supported_pdfs:
        print("❌ No supported PDF files found!")
        print("💡 Make sure your PDFs contain keywords like: btech, semester, result, autonomous, college, etc.")
        return
    
    # Process each PDF
    results = []
    total_start_time = time.time()
    
    for i, pdf_path in enumerate(supported_pdfs, 1):
        print(f"\n{'='*60}")
        print(f"📄 Processing PDF {i}/{len(supported_pdfs)}")
        print(f"{'='*60}")
        
        result = process_single_pdf(pdf_path, db, bucket, batch_size)
        results.append({
            'pdf': os.path.basename(pdf_path),
            'result': result
        })
    
    # Summary
    total_time = time.time() - total_start_time
    print(f"\n{'='*60}")
    print(f"🎯 BATCH PROCESSING COMPLETE!")
    print(f"{'='*60}")
    
    total_students = sum(r['result'].get('total_students', 0) for r in results)
    total_saved = sum(r['result'].get('saved', 0) for r in results)
    total_updated = sum(r['result'].get('updated', 0) for r in results)
    total_skipped = sum(r['result'].get('skipped', 0) for r in results)
    total_batches = sum(r['result'].get('batches_processed', 0) for r in results)
    successful_pdfs = sum(1 for r in results if r['result'].get('success', False))
    
    print(f"📊 PDFs processed: {len(supported_pdfs)}")
    print(f"✅ Successful: {successful_pdfs}")
    print(f"❌ Failed: {len(supported_pdfs) - successful_pdfs}")
    print(f"📦 Total batches: {total_batches}")
    print(f"⚙️ Batch size used: {batch_size}")
    print(f"👥 Total students extracted: {total_students}")
    print(f"➕ New records created: {total_saved}")
    print(f"🔄 Records updated (smart merge): {total_updated}")
    print(f"⏭️ Records skipped: {total_skipped}")
    print(f"⚡ Overall processing rate: {total_students/total_time:.1f} records/second")
    print(f"⏱️ Total processing time: {total_time:.2f} seconds")
    print(f"⚡ Average per PDF: {total_time/len(supported_pdfs):.2f} seconds")
    
    # Detailed results
    print(f"\n📋 Detailed Results:")
    for result in results:
        pdf_name = result['pdf']
        res = result['result']
        if res.get('success'):
            batches = res.get('batches_processed', 0)
            rate = res.get('total_students', 0) / res.get('processing_time', 1)
            firebase_status = "Firebase" if res.get('firebase_enabled', False) else "JSON-only"
            new_records = res.get('saved', 0)
            updated_records = res.get('updated', 0)
            print(f"✅ {pdf_name}: {res.get('total_students', 0)} students, {batches} batches, {rate:.1f} rec/s")
            print(f"   📊 {new_records} new, {updated_records} updated ({firebase_status})")
        else:
            print(f"❌ {pdf_name}: FAILED - {res.get('error', 'Unknown error')}")

if __name__ == "__main__":
    # Allow command line batch size override
    import sys
    
    batch_size = DEFAULT_BATCH_SIZE
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
            print(f"⚙️ Using command line batch size: {batch_size}")
        except ValueError:
            print(f"⚠️ Invalid batch size argument, using default: {DEFAULT_BATCH_SIZE}")
    
    main(batch_size)
