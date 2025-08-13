import pdfplumber
import re
from datetime import datetime
from collections import defaultdict
import time

def parse_jntuk_pdf_generator(file_path, batch_size=50):
    """Generator version that yields batches of student records for real-time processing"""
    print(f"🚀 Starting optimized batch JNTUK parsing of: {file_path}")
    start_time = time.time()
    
    results = defaultdict(lambda: {
        "subjectGrades": [],
        "totalCredits": 0
    })
    
    current_semester = None
    current_exam_type = "regular"
    upload_date = datetime.now().strftime("%Y-%m-%d")
    students_processed = 0
    processed_students = set()
    batch_count = 0
    
    # Enhanced Grade points for SGPA calculation - supports all possible variations
    grade_points = {
        'S': 10, 'A+': 10, 'A': 9, 'A-': 8.5, 'B+': 8, 'B': 7, 'B-': 6.5,
        'C+': 6, 'C': 5, 'C-': 4.5, 'D+': 4, 'D': 3, 'E': 2, 'F': 0, 
        'MP': 0, 'ABSENT': 0, 'AB': 0, 'MALPRACTICE': 0, 'WITHHELD': 0,
        'INCOMPLETE': 0, 'REVALUATION': 0, 'DETAINED': 0
    }
    
    with pdfplumber.open(file_path) as pdf:
        print(f"📄 JNTUK PDF has {len(pdf.pages)} pages")
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            # Show progress for large PDFs
            if page_num > 0 and page_num % 5 == 0:
                print(f"📊 Processed {page_num+1}/{len(pdf.pages)} pages...")

            # Enhanced semester detection - multiple pattern support
            if not current_semester or page_num < 5:
                # Pattern 1: Standard format
                semester_match = re.search(r"([I|II|III|IV]+)\s+B\.Tech\s+([I|II|III|IV|V|VI|VII|VIII]+)\s+Semester", text, re.IGNORECASE)
                if not semester_match:
                    # Pattern 2: Alternative formats
                    semester_match = re.search(r"B\.?Tech\s+([I|II|III|IV|V|VI|VII|VIII]+)\s+Sem", text, re.IGNORECASE)
                if not semester_match:
                    # Pattern 3: Simple semester detection
                    semester_match = re.search(r"(\d+)\s*(st|nd|rd|th)?\s*Sem", text, re.IGNORECASE)
                if not semester_match:
                    # Pattern 4: Roman numeral only
                    semester_match = re.search(r"Semester\s*([I|II|III|IV|V|VI|VII|VIII]+)", text, re.IGNORECASE)
                
                if semester_match:
                    sem_str = semester_match.group(1)
                    # Handle both roman numerals and regular numbers
                    roman_to_num = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8}
                    if sem_str in roman_to_num:
                        sem_num = roman_to_num[sem_str]
                    else:
                        try:
                            sem_num = int(sem_str)
                        except:
                            sem_num = 1
                    current_semester = f"Semester {sem_num}"
                    print(f"🎯 Detected semester: {current_semester}")
            
            # Enhanced exam type detection - check once per PDF
            if page_num < 5:
                if re.search(r"supply|supplementary|supple", text, re.IGNORECASE):
                    current_exam_type = "supply"

            # Process students from this page
            page_students = []
            
            # Table extraction
            try:
                tables = page.extract_tables()
                if tables:
                    print(f"🔍 Found {len(tables)} tables on page {page_num}")
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            print(f"❌ Table {table_idx} is empty or too small")
                            continue
                        
                        print(f"✅ Processing table {table_idx} with {len(table)} rows")
                        print(f"📊 Sample rows: {table[:3]}")  # Show first 3 rows
                            
                        for row_idx, row in enumerate(table[1:]):  # Skip header
                            if not row or len(row) < 6:
                                if row_idx < 5:  # Only show first few invalid rows
                                    print(f"❌ Row {row_idx} invalid: {row}")
                                continue
                            
                            if row_idx < 3:  # Show first few valid rows for debugging
                                print(f"🔍 Processing row {row_idx}: {row}")
                                
                            try:
                                # Handle multiple row formats flexibly
                                if len(row) == 7:
                                    _, htno, subcode, subname, internals, grade, credits = row
                                elif len(row) == 6:
                                    htno, subcode, subname, internals, grade, credits = row
                                elif len(row) >= 13:
                                    # Handle new format with grades as columns (like CR24 format)
                                    # Skip rows that are just headers or summary rows
                                    if str(row[1]).strip() and len(str(row[1]).strip()) >= 8:
                                        htno = row[1]
                                        # For grade-column format, we need to parse differently
                                        print(f"🔍 Detected grade-column format for HTNO: {htno}")
                                        # Skip this format for now, handle in separate logic below
                                        continue
                                elif len(row) >= 5:
                                    # Try to auto-detect column positions
                                    potential_htno = None
                                    for i, cell in enumerate(row):
                                        cell_str = str(cell).strip()
                                        if len(cell_str) >= 8 and re.match(r'^[A-Z0-9]+$', cell_str):
                                            potential_htno = cell_str
                                            break
                                    
                                    if potential_htno:
                                        htno = potential_htno
                                        # Try to find other fields
                                        remaining_cells = [c for c in row if c != htno]
                                        if len(remaining_cells) >= 4:
                                            subcode = remaining_cells[0] if remaining_cells[0] else ""
                                            subname = remaining_cells[1] if remaining_cells[1] else ""
                                            internals = remaining_cells[-3] if len(remaining_cells) > 2 else 0
                                            grade = remaining_cells[-2] if len(remaining_cells) > 1 else "F"
                                            credits = remaining_cells[-1] if remaining_cells else 0
                                        else:
                                            continue
                                    else:
                                        if row_idx < 3:
                                            print(f"❌ Could not identify HTNO in row {row_idx}: {row}")
                                        continue
                                else:
                                    if row_idx < 3:
                                        print(f"❌ Invalid row length {len(row)} in row {row_idx}: {row}")
                                    continue

                                # Enhanced student ID pattern matching - supports all JNTUK formats
                                htno_str = str(htno).strip()
                                if not htno_str:
                                    if row_idx < 3:
                                        print(f"❌ Empty HTNO in row {row_idx}")
                                    continue
                                
                                # Support comprehensive JNTUK student ID formats
                                valid_patterns = [
                                    r'^\d{2}[A-Z0-9]{8}$',          # 20B91A0501 (standard)
                                    r'^\d{2}[A-Z0-9]{9}$',          # 20B91A05010 (extended)
                                    r'^\d{4}[A-Z0-9]{8}$',          # 2020B91A0501 (full year)
                                    r'^\d{2}[A-Z0-9]{6,10}$',       # Variable length
                                    r'^[A-Z0-9]{10,14}$',           # Alphanumeric format
                                    r'^\d{2}[A-Z]{2}\d[A-Z]\d{4}$', # Pattern like 20B8A0501
                                    r'^\d{2}[A-Z]{3}\d[A-Z]\d{3,4}$' # Extended patterns
                                ]
                                
                                is_valid_htno = any(re.match(pattern, htno_str) for pattern in valid_patterns)
                                
                                # Additional validation - check if it looks like a student ID
                                if not is_valid_htno and len(htno_str) >= 8:
                                    # Try to match any reasonable student ID pattern
                                    if re.match(r'^[A-Z0-9]{8,15}$', htno_str) and any(c.isdigit() for c in htno_str):
                                        is_valid_htno = True
                                        print(f"⚠️ Using fallback pattern for HTNO: {htno_str}")
                                
                                if not is_valid_htno:
                                    if row_idx < 5:
                                        print(f"❌ Invalid HTNO '{htno_str}' in row {row_idx}")
                                    continue
                                
                                if row_idx < 3:
                                    print(f"✅ Valid HTNO found: {htno_str}")

                                # Enhanced internals and credits parsing
                                try:
                                    internals_str = str(internals).strip().upper()
                                    if internals_str in ['ABSENT', 'AB', 'ABS', '-', '']:
                                        internals_val = 0
                                    else:
                                        internals_val = int(float(internals_str))
                                except (ValueError, TypeError):
                                    internals_val = 0
                                
                                try:
                                    credits_str = str(credits).strip()
                                    if credits_str in ['-', '', 'NIL']:
                                        credits_val = 0.0
                                    else:
                                        credits_val = float(credits_str)
                                except (ValueError, TypeError):
                                    credits_val = 0.0
                                
                                # Enhanced grade validation
                                grade_str = str(grade).strip().upper()
                                valid_grades = ['S', 'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 
                                              'D+', 'D', 'E', 'F', 'MP', 'ABSENT', 'AB', 'MALPRACTICE', 
                                              'WITHHELD', 'INCOMPLETE', 'REVALUATION', 'DETAINED']
                                
                                if grade_str not in valid_grades:
                                    # Try to clean the grade
                                    grade_str = re.sub(r'[^A-Z+\-]', '', grade_str)
                                    if grade_str not in valid_grades:
                                        if row_idx < 3:
                                            print(f"⚠️ Unknown grade '{grade}' -> using 'F'")
                                        grade_str = 'F'

                                student = results[htno_str]  # Use cleaned HTNO
                                student['student_id'] = htno_str
                                student['university'] = "JNTUK"
                                student['semester'] = current_semester or "Unknown"
                                student['examType'] = current_exam_type
                                student['upload_date'] = upload_date

                                student['subjectGrades'].append({
                                    "code": str(subcode or "").strip(),
                                    "subject": str(subname or "").strip(),
                                    "internals": internals_val,
                                    "grade": grade_str,  # Use cleaned grade
                                    "credits": credits_val
                                })

                                student['totalCredits'] += credits_val
                                
                                # Add to page students if not already processed
                                if htno_str not in processed_students:
                                    processed_students.add(htno_str)
                                    page_students.append(htno_str)
                                    
                            except (ValueError, TypeError, AttributeError):
                                continue
            except Exception:
                pass

            # Special handler for grade-column format (like CR24 Results)
            try:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                        
                        # Check if this looks like a grade-column format
                        header_row = table[0] if table else []
                        if len(header_row) > 10 and any('SGPA' in str(cell) for cell in header_row[-3:]):
                            print(f"🎯 Detected grade-column format table")
                            
                            # Extract subject codes from header (skip first 2-3 columns which are usually S.No, HTNO)
                            subject_codes = []
                            for cell in header_row[2:-1]:  # Skip S.No, HTNO and SGPA
                                if cell and str(cell).strip():
                                    subject_codes.append(str(cell).strip())
                            
                            print(f"📚 Found {len(subject_codes)} subjects: {subject_codes[:5]}...")
                            
                            # Process each student row
                            for row_idx, row in enumerate(table[1:]):
                                if not row or len(row) < len(header_row):
                                    continue
                                
                                # Extract HTNO (usually second column)
                                htno_str = str(row[1]).strip() if len(row) > 1 else ""
                                if not htno_str or not re.match(r'^[A-Z0-9]{8,15}$', htno_str):
                                    continue
                                
                                print(f"🔍 Processing grade-column student: {htno_str}")
                                
                                student = results[htno_str]
                                student['student_id'] = htno_str
                                student['university'] = "JNTUK"
                                student['semester'] = current_semester or "Unknown"
                                student['examType'] = current_exam_type
                                student['upload_date'] = upload_date
                                
                                # Process grades for each subject
                                for i, subject_code in enumerate(subject_codes):
                                    grade_col_idx = i + 2  # Adjust for S.No, HTNO columns
                                    if grade_col_idx < len(row):
                                        grade = str(row[grade_col_idx]).strip().upper()
                                        
                                        # Skip empty or invalid grades
                                        if not grade or grade in ['-', 'None', '']:
                                            continue
                                            
                                        # Default credits (can be refined based on subject type)
                                        credits = 3.0  # Most subjects are 3 credits
                                        if 'LAB' in subject_code.upper() or 'L' in subject_code[-1:]:
                                            credits = 1.5
                                        elif 'WORKSHOP' in subject_code.upper():
                                            credits = 2.0
                                        
                                        student['subjectGrades'].append({
                                            "code": subject_code,
                                            "subject": subject_code,  # Use code as name for now
                                            "internals": 0,  # Not available in this format
                                            "grade": grade,
                                            "credits": credits
                                        })
                                        
                                        student['totalCredits'] += credits
                                
                                # Add to page students if not already processed
                                if htno_str not in processed_students and student.get('subjectGrades'):
                                    processed_students.add(htno_str)
                                    page_students.append(htno_str)
                                    print(f"✅ Added grade-column student: {htno_str} with {len(student['subjectGrades'])} subjects")
                                    
            except Exception as e:
                print(f"⚠️ Error in grade-column processing: {e}")

            # Line-based extraction
            try:
                lines = text.split('\n')
                for line in lines:
                    if not line.strip() or 'Htno' in line or 'Subcode' in line:
                        continue

                    parts = line.strip().split()
                    if len(parts) >= 6:
                        try:
                            if len(parts) > 1 and len(str(parts[1])) == 10 and re.match(r'\d{2}[A-Z0-9]{8}', str(parts[1])):
                                htno = parts[1]
                                
                                if htno in processed_students:
                                    continue
                                    
                                subcode = parts[2] if len(parts) > 2 else ""
                                credits = parts[-1]
                                grade = parts[-2]
                                internals = parts[-3]

                                if (re.match(r'\d+|ABSENT', str(internals)) and 
                                    re.match(r'[A-F][\+\-]?|MP|ABSENT|S|COMPLE', str(grade)) and
                                    re.match(r'\d+(?:\.\d+)?', str(credits))):

                                    internals_val = 0 if str(internals) == 'ABSENT' else int(internals)
                                    credits_val = float(credits)
                                    subname_parts = parts[3:-3] if len(parts) > 6 else []
                                    subname = ' '.join(subname_parts)

                                    student = results[htno]
                                    student['student_id'] = htno
                                    student['university'] = "JNTUK"
                                    student['semester'] = current_semester or "Unknown"
                                    student['examType'] = current_exam_type
                                    student['upload_date'] = upload_date

                                    student['subjectGrades'].append({
                                        "code": str(subcode).strip(),
                                        "subject": subname.strip(),
                                        "internals": internals_val,
                                        "grade": str(grade).strip(),
                                        "credits": credits_val
                                    })

                                    student['totalCredits'] += credits_val
                                    
                                    # Add to page students if not already processed
                                    if htno not in processed_students:
                                        processed_students.add(htno)
                                        page_students.append(htno)
                                        
                        except (ValueError, IndexError, AttributeError):
                            continue
            except Exception:
                pass
            
            # Yield batch when we have enough students
            if len(page_students) >= batch_size:
                batch_records = []
                students_to_process = page_students[:batch_size]
                
                for htno in students_to_process:
                    student_data = results[htno]
                    if student_data.get('subjectGrades'):
                        # Calculate SGPA
                        total_points = 0
                        total_credits = 0
                        
                        for subject in student_data['subjectGrades']:
                            grade = subject.get('grade', 'F')
                            credits = subject.get('credits', 0)
                            points = grade_points.get(grade, 0)
                            total_points += points * credits
                            total_credits += credits
                        
                        sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
                        
                        batch_records.append({
                            "student_id": student_data['student_id'],
                            "semester": student_data['semester'],
                            "university": student_data['university'],
                            "upload_date": student_data['upload_date'],
                            "sgpa": sgpa,
                            "subjectGrades": student_data['subjectGrades']
                        })
                
                if batch_records:
                    batch_count += 1
                    students_processed += len(batch_records)
                    print(f"🚀 Yielding batch {batch_count}: {len(batch_records)} students (Total: {students_processed})")
                    yield batch_records
                
                # Remove processed students from page_students
                page_students = page_students[batch_size:]
            
            # Also check if we've accumulated enough students across all results
            if len(results) >= batch_size and len(results) % batch_size == 0:
                # Yield a batch from accumulated results
                batch_records = []
                students_to_yield = []
                
                for htno, student_data in list(results.items()):
                    if htno not in processed_students and len(students_to_yield) < batch_size:
                        students_to_yield.append(htno)
                        processed_students.add(htno)
                
                for htno in students_to_yield:
                    student_data = results[htno]
                    if student_data.get('subjectGrades'):
                        # Calculate SGPA
                        total_points = 0
                        total_credits = 0
                        
                        for subject in student_data['subjectGrades']:
                            grade = subject.get('grade', 'F')
                            credits = subject.get('credits', 0)
                            points = grade_points.get(grade, 0)
                            total_points += points * credits
                            total_credits += credits
                        
                        sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
                        
                        batch_records.append({
                            "student_id": student_data['student_id'],
                            "semester": student_data['semester'],
                            "university": student_data['university'],
                            "upload_date": student_data['upload_date'],
                            "sgpa": sgpa,
                            "subjectGrades": student_data['subjectGrades']
                        })
                
                if batch_records:
                    batch_count += 1
                    students_processed += len(batch_records)
                    print(f"🚀 Yielding page batch {batch_count}: {len(batch_records)} students (Total: {students_processed})")
                    yield batch_records

    # Yield remaining students in proper batches
    remaining_students = []
    for htno, student_data in results.items():
        if student_data.get('subjectGrades'):
            remaining_students.append(htno)
    
    print(f"🔍 Found {len(remaining_students)} total students with subject grades")
    
    # Process remaining students in batches
    for i in range(0, len(remaining_students), batch_size):
        batch_htnos = remaining_students[i:i + batch_size]
        batch_records = []
        
        for htno in batch_htnos:
            student_data = results[htno]
            # Calculate SGPA
            total_points = 0
            total_credits = 0
            
            for subject in student_data['subjectGrades']:
                grade = subject.get('grade', 'F')
                credits = subject.get('credits', 0)
                points = grade_points.get(grade, 0)
                total_points += points * credits
                total_credits += credits
            
            sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
            
            batch_records.append({
                "student_id": student_data['student_id'],
                "semester": student_data['semester'],
                "university": student_data['university'],
                "upload_date": student_data['upload_date'],
                "sgpa": sgpa,
                "subjectGrades": student_data['subjectGrades']
            })
        
        if batch_records:
            batch_count += 1
            students_processed += len(batch_records)
            print(f"🚀 Yielding final batch {batch_count}: {len(batch_records)} students (Total: {students_processed})")
            yield batch_records

    total_time = time.time() - start_time
    print(f"✅ Completed batch parsing in {total_time:.2f} seconds - {students_processed} total students")

def parse_jntuk_pdf(file_path, streaming_callback=None):
    print(f"🚀 Starting real-time JNTUK parsing of: {file_path}")
    start_time = time.time()
    
    results = defaultdict(lambda: {
        "subjectGrades": [],
        "totalCredits": 0
    })

    current_semester = None
    current_exam_type = "regular"
    upload_date = datetime.now().strftime("%Y-%m-%d")  # Calculate once
    students_processed = 0
    processed_students = set()  # Track processed students for streaming
    
    # Enhanced Grade points for SGPA calculation - supports all possible variations
    grade_points = {
        'S': 10, 'A+': 10, 'A': 9, 'A-': 8.5, 'B+': 8, 'B': 7, 'B-': 6.5,
        'C+': 6, 'C': 5, 'C-': 4.5, 'D+': 4, 'D': 3, 'E': 2, 'F': 0, 
        'MP': 0, 'ABSENT': 0, 'AB': 0, 'MALPRACTICE': 0, 'WITHHELD': 0,
        'INCOMPLETE': 0, 'REVALUATION': 0, 'DETAINED': 0
    }
    
    with pdfplumber.open(file_path) as pdf:
        print(f"📄 JNTUK PDF has {len(pdf.pages)} pages")
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            # Show progress for large PDFs
            if page_num > 0 and page_num % 5 == 0:
                print(f"📊 Processed {page_num+1}/{len(pdf.pages)} pages...")

            # Optimized semester detection - search only first few pages
            if not current_semester or page_num < 3:
                semester_match = re.search(r"([I|II|III|IV]+)\s+B\.Tech\s+([I|II|III|IV|V|VI|VII|VIII]+)\s+Semester", text)
                if semester_match:
                    sem_roman = semester_match.group(2)
                    roman_to_num = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8}
                    sem_num = roman_to_num.get(sem_roman, 1)
                    current_semester = f"Semester {sem_num}"
                    print(f"🎯 Detected semester: {current_semester}")
            
            # Optimized exam type detection - check once per PDF
            if page_num < 3:
                if re.search(r"supply|supplementary|supple", text, re.IGNORECASE):
                    current_exam_type = "supply"

            # Optimized table extraction
            try:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        if not table or len(table) < 2:
                            continue
                            
                        for row in table[1:]:  # Skip header
                            if not row or len(row) < 6:
                                continue
                                
                            try:
                                if len(row) == 7:
                                    _, htno, subcode, subname, internals, grade, credits = row
                                elif len(row) == 6:
                                    htno, subcode, subname, internals, grade, credits = row
                                else:
                                    continue

                                if not htno or not re.match(r'\d{2}[A-Z0-9]{8}', str(htno)):
                                    continue

                                internals_val = 0 if str(internals).strip() == 'ABSENT' else int(internals or 0)
                                credits_val = float(credits or 0)

                                student = results[htno]
                                student['student_id'] = htno
                                student['university'] = "JNTUK"
                                student['semester'] = current_semester or "Unknown"
                                student['examType'] = current_exam_type
                                student['upload_date'] = upload_date

                                student['subjectGrades'].append({
                                    "code": str(subcode or "").strip(),
                                    "subject": str(subname or "").strip(),
                                    "internals": internals_val,
                                    "grade": str(grade or "").strip(),
                                    "credits": credits_val
                                })

                                student['totalCredits'] += credits_val
                                
                                # Send real-time update if callback provided
                                if streaming_callback and htno not in processed_students:
                                    processed_students.add(htno)
                                    students_processed += 1
                                    
                                    # Calculate and send complete student record
                                    grade_points = {
                                        'S': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 
                                        'C': 5, 'D': 4, 'F': 0, 'MP': 0, 'ABSENT': 0
                                    }
                                    
                                    total_points = 0
                                    total_credits = 0
                                    for subject in student['subjectGrades']:
                                        grade = subject.get('grade', 'F')
                                        credits = subject.get('credits', 0)
                                        points = grade_points.get(grade, 0)
                                        total_points += points * credits
                                        total_credits += credits
                                    
                                    sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
                                    
                                    complete_record = {
                                        "student_id": student['student_id'],
                                        "semester": student['semester'],
                                        "university": student['university'],
                                        "upload_date": student['upload_date'],
                                        "sgpa": sgpa,
                                        "subjectGrades": student['subjectGrades'].copy()
                                    }
                                    
                                    streaming_callback(complete_record, students_processed)
                            except (ValueError, TypeError, AttributeError):
                                continue
            except Exception:
                pass

            # Fast line-based extraction for other formats
            try:
                lines = text.split('\n')
                for line in lines:
                    if not line.strip() or 'Htno' in line or 'Subcode' in line:
                        continue

                    parts = line.strip().split()
                    if len(parts) >= 6:
                        try:
                            if len(parts) > 1 and len(str(parts[1])) == 10 and re.match(r'\d{2}[A-Z0-9]{8}', str(parts[1])):
                                htno = parts[1]
                                subcode = parts[2] if len(parts) > 2 else ""
                                credits = parts[-1]
                                grade = parts[-2]
                                internals = parts[-3]

                                if (re.match(r'\d+|ABSENT', str(internals)) and 
                                    re.match(r'[A-F][\+\-]?|MP|ABSENT|S|COMPLE', str(grade)) and
                                    re.match(r'\d+(?:\.\d+)?', str(credits))):

                                    internals_val = 0 if str(internals) == 'ABSENT' else int(internals)
                                    credits_val = float(credits)
                                    subname_parts = parts[3:-3] if len(parts) > 6 else []
                                    subname = ' '.join(subname_parts)

                                    student = results[htno]
                                    student['student_id'] = htno
                                    student['university'] = "JNTUK"
                                    student['semester'] = current_semester or "Unknown"
                                    student['examType'] = current_exam_type
                                    student['upload_date'] = upload_date

                                    student['subjectGrades'].append({
                                        "code": str(subcode).strip(),
                                        "subject": subname.strip(),
                                        "internals": internals_val,
                                        "grade": str(grade).strip(),
                                        "credits": credits_val
                                    })

                                    student['totalCredits'] += credits_val
                                    
                                    # Send real-time update if callback provided
                                    if streaming_callback and htno not in processed_students:
                                        processed_students.add(htno)
                                        students_processed += 1
                                        
                                        # Calculate and send complete student record
                                        grade_points = {
                                            'S': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 
                                            'C': 5, 'D': 4, 'F': 0, 'MP': 0, 'ABSENT': 0
                                        }
                                        
                                        total_points = 0
                                        total_credits = 0
                                        for subject in student['subjectGrades']:
                                            grade = subject.get('grade', 'F')
                                            credits = subject.get('credits', 0)
                                            points = grade_points.get(grade, 0)
                                            total_points += points * credits
                                            total_credits += credits
                                        
                                        sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
                                        
                                        complete_record = {
                                            "student_id": student['student_id'],
                                            "semester": student['semester'],
                                            "university": student['university'],
                                            "upload_date": student['upload_date'],
                                            "sgpa": sgpa,
                                            "subjectGrades": student['subjectGrades'].copy()
                                        }
                                        
                                        streaming_callback(complete_record, students_processed)
                        except (ValueError, IndexError, AttributeError):
                            continue
            except Exception:
                pass

    # Convert results to final format with SGPA calculation
    final_results = []
    grade_points = {
        'S': 10, 'A+': 9, 'A': 8, 'B+': 7, 'B': 6, 
        'C': 5, 'D': 4, 'F': 0, 'MP': 0, 'ABSENT': 0
    }
    
    for htno, student_data in results.items():
        if student_data.get('subjectGrades'):
            # Calculate SGPA
            total_points = 0
            total_credits = 0
            
            for subject in student_data['subjectGrades']:
                grade = subject.get('grade', 'F')
                credits = subject.get('credits', 0)
                points = grade_points.get(grade, 0)
                total_points += points * credits
                total_credits += credits
            
            sgpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0
            
            final_results.append({
                "student_id": student_data['student_id'],
                "semester": student_data['semester'],
                "university": student_data['university'],
                "upload_date": student_data['upload_date'],
                "sgpa": sgpa,
                "subjectGrades": student_data['subjectGrades']
            })

    total_time = time.time() - start_time
    print(f"✅ Extracted {len(final_results)} JNTUK student records in {total_time:.2f} seconds")
    
    if final_results:
        print(f"📝 Sample record: {final_results[0]['student_id']} has {len(final_results[0]['subjectGrades'])} subjects")
    else:
        print("⚠️ No JNTUK student records found - check PDF format")

    return final_results
