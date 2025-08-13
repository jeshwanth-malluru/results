"""
Enhanced JNTUK Parser for Multiple PDF Formats
Handles both SGPA-based and subject-per-row formats
"""

import re
import pdfplumber
from collections import defaultdict
from datetime import datetime

def parse_jntuk_sgpa_format(row, subject_codes):
    """
    Parse SGPA format where one row contains multiple subject grades
    Format: [Serial, HTNO, Grade1, Grade2, ..., GradeN, SGPA]
    """
    if len(row) < 3:
        return None
    
    # Extract student ID (second column)
    htno = str(row[1]).strip()
    
    # Validate HTNO pattern
    valid_patterns = [
        r'^\d{2}[A-Z0-9]{8}$',          # 24B81A0101
        r'^\d{2}[A-Z0-9]{9}$',          # 24B81A01010  
        r'^\d{4}[A-Z0-9]{8}$',          # 2024B81A0101
    ]
    
    is_valid_htno = any(re.match(pattern, htno) for pattern in valid_patterns)
    if not is_valid_htno:
        return None
    
    student_data = {
        'student_id': htno,
        'university': "JNTUK",
        'semester': "Unknown",
        'examType': 'regular',
        'upload_date': datetime.now().isoformat(),
        'subjectGrades': [],
        'sgpa': 0.0
    }
    
    # Extract grades (skip serial and htno, last column is SGPA)
    grades = row[2:-1] if len(row) > 3 else []
    sgpa_str = str(row[-1]) if len(row) > 2 else "0.00"
    
    # Parse SGPA
    try:
        student_data['sgpa'] = float(sgpa_str)
    except (ValueError, TypeError):
        student_data['sgpa'] = 0.0
    
    # Map grades to subject codes
    for i, grade in enumerate(grades):
        if i < len(subject_codes):
            subject_code = str(subject_codes[i]).strip()
            grade_str = str(grade).strip()
            
            # Skip empty or invalid grades
            if not grade_str or grade_str in ['None', '']:
                continue
            
            student_data['subjectGrades'].append({
                "code": subject_code,
                "subject": f"Subject {subject_code}",  # Use code as name for now
                "internals": 0,
                "grade": grade_str,
                "credits": 3.0  # Default credits
            })
    
    return student_data

def parse_jntuk_subject_per_row_format(row):
    """
    Parse subject-per-row format 
    Format: [HTNO, SubCode, SubName, Internals, Grade, Credits]
    """
    if len(row) != 6:
        return None
    
    htno, subcode, subname, internals, grade, credits = row
    htno_str = str(htno).strip()
    
    # Validate HTNO pattern
    valid_patterns = [
        r'^\d{2}[A-Z0-9]{8}$',          # 23B81A12D2
        r'^\d{2}[A-Z0-9]{9}$',          # 23B81A12D20  
        r'^\d{4}[A-Z0-9]{8}$',          # 2023B81A12D2
    ]
    
    is_valid_htno = any(re.match(pattern, htno_str) for pattern in valid_patterns)
    if not is_valid_htno:
        return None
    
    try:
        internals_val = 0 if str(internals).strip() == 'ABSENT' else int(internals or 0)
        credits_val = float(credits or 0)
    except (ValueError, TypeError):
        internals_val = 0
        credits_val = 0.0
    
    return {
        'student_id': htno_str,
        'subject': {
            "code": str(subcode or "").strip(),
            "subject": str(subname or "").strip(),
            "internals": internals_val,
            "grade": str(grade or "").strip(),
            "credits": credits_val
        }
    }

def parse_jntuk_pdf_enhanced_generator(file_path, batch_size=50):
    """
    Enhanced JNTUK PDF parser that handles multiple formats
    """
    print(f"🚀 Starting enhanced JNTUK parsing of: {file_path}")
    
    students_data = defaultdict(lambda: {
        'student_id': '',
        'university': "JNTUK", 
        'semester': "Unknown",
        'examType': 'regular',
        'upload_date': datetime.now().isoformat(),
        'subjectGrades': [],
        'sgpa': 0.0
    })
    
    processed_students = set()
    current_semester = "Unknown"
    
    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"📄 JNTUK PDF has {len(pdf.pages)} pages")
            
            # Detect PDF format from first few pages
            pdf_format = "unknown"
            subject_codes = []
            
            # Sample first few pages to detect format
            for page_num in range(min(3, len(pdf.pages))):
                page = pdf.pages[page_num]
                tables = page.extract_tables()
                
                if tables and len(tables) > 0:
                    table = tables[0]
                    if len(table) > 1:
                        # Check header row for format detection
                        header_row = table[0] if table[0] else []
                        data_row = table[1] if len(table) > 1 and table[1] else []
                        
                        print(f"🔍 Header row: {header_row}")
                        print(f"🔍 Sample data row: {data_row}")
                        
                        # Detect SGPA format (multiple grade columns)
                        if len(data_row) > 10 and 'SGPA' in str(header_row).upper():
                            pdf_format = "sgpa"
                            subject_codes = header_row[2:-1] if len(header_row) > 3 else []
                            print(f"✅ Detected SGPA format with {len(subject_codes)} subjects")
                            print(f"📊 Subject codes: {subject_codes[:5]}...")
                            break
                        
                        # Detect subject-per-row format  
                        elif len(data_row) == 6 and any(col in str(header_row).upper() for col in ['HTNO', 'SUBCODE', 'SUBNAME']):
                            pdf_format = "subject_per_row"
                            print(f"✅ Detected subject-per-row format")
                            break
            
            if pdf_format == "unknown":
                print(f"⚠️ Could not detect PDF format, defaulting to subject-per-row")
                pdf_format = "subject_per_row"
            
            # Process pages based on detected format
            for page_num, page in enumerate(pdf.pages):
                if page_num % 5 == 0:
                    print(f"📊 Processed {page_num}/{len(pdf.pages)} pages...")
                
                tables = page.extract_tables()
                if not tables:
                    continue
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Skip header row
                    for row in table[1:]:
                        if not row:
                            continue
                        
                        try:
                            if pdf_format == "sgpa":
                                student_data = parse_jntuk_sgpa_format(row, subject_codes)
                                if student_data:
                                    student_id = student_data['student_id']
                                    students_data[student_id] = student_data
                                    
                            elif pdf_format == "subject_per_row":
                                subject_data = parse_jntuk_subject_per_row_format(row)
                                if subject_data:
                                    student_id = subject_data['student_id']
                                    
                                    # Initialize student if not exists
                                    if student_id not in students_data:
                                        students_data[student_id] = {
                                            'student_id': student_id,
                                            'university': "JNTUK",
                                            'semester': current_semester or "Unknown", 
                                            'examType': 'regular',
                                            'upload_date': datetime.now().isoformat(),
                                            'subjectGrades': [],
                                            'sgpa': 0.0
                                        }
                                    
                                    # Add subject to student
                                    students_data[student_id]['subjectGrades'].append(subject_data['subject'])
                        
                        except Exception as e:
                            print(f"⚠️ Error parsing row {row}: {e}")
                            continue
                
                # Yield batch if we have enough students
                if len(students_data) >= batch_size:
                    batch_records = list(students_data.values())
                    print(f"🚀 Yielding batch: {len(batch_records)} students")
                    yield batch_records
                    students_data.clear()
            
            # Yield final batch
            if students_data:
                batch_records = list(students_data.values())
                print(f"🚀 Yielding final batch: {len(batch_records)} students")
                yield batch_records
                
    except Exception as e:
        print(f"❌ Error processing PDF {file_path}: {e}")
        if students_data:
            yield list(students_data.values())

# Replace the original function in parser_jntuk.py
def parse_jntuk_pdf_generator(file_path, batch_size=50):
    """
    Main entry point - delegates to enhanced parser
    """
    return parse_jntuk_pdf_enhanced_generator(file_path, batch_size)
