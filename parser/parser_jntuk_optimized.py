import pdfplumber
import re
from datetime import datetime
from collections import defaultdict
import time

def parse_jntuk_pdf(file_path):
    print(f"🚀 Starting JNTUK parsing of: {file_path}")
    start_time = time.time()
    
    results = defaultdict(lambda: {"subjectGrades": []})
    current_semester = None
    current_exam_type = "regular"
    upload_date = datetime.now().strftime("%Y-%m-%d")
    
    with pdfplumber.open(file_path) as pdf:
        print(f"📄 PDF has {len(pdf.pages)} pages")
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            # Progress indicator
            if page_num > 0 and page_num % 10 == 0:
                print(f"📊 Processed {page_num+1}/{len(pdf.pages)} pages...")

            # Semester detection (first 3 pages only)
            if not current_semester and page_num < 3:
                semester_match = re.search(r"([I|II|III|IV]+)\s+B\.Tech\s+([I|II|III|IV|V|VI|VII|VIII]+)\s+Semester", text)
                if semester_match:
                    sem_roman = semester_match.group(2)
                    roman_to_num = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7, 'VIII': 8}
                    sem_num = roman_to_num.get(sem_roman, 1)
                    current_semester = f"Semester {sem_num}"
                    print(f"🎯 Detected semester: {current_semester}")
            
            # Exam type detection (first 3 pages only)
            if page_num < 3 and re.search(r"supply|supplementary", text, re.IGNORECASE):
                current_exam_type = "supply"

            # Table extraction
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
                            student['upload_date'] = upload_date

                            student['subjectGrades'].append({
                                "code": str(subcode or "").strip(),
                                "subject": str(subname or "").strip(),
                                "internals": internals_val,
                                "grade": str(grade or "").strip(),
                                "credits": credits_val
                            })
                        except (ValueError, TypeError, AttributeError):
                            continue

    # Convert to final format with SGPA calculation
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
    print(f"✅ Extracted {len(final_results)} student records in {total_time:.2f} seconds")
    
    if final_results:
        print(f"📝 Sample: {final_results[0]['student_id']} has {len(final_results[0]['subjectGrades'])} subjects")

    return final_results
