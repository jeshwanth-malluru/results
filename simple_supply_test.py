#!/usr/bin/env python3
"""
Simple Supply PDF Upload Test
Tests the supply upload functionality step by step
"""

import os
import sys
import json
from datetime import datetime

def test_supply_processing():
    """Test supply processing without Firebase dependencies"""
    print("🧪 TESTING SUPPLY PROCESSING (No Firebase)")
    print("=" * 60)
    
    # Mock data that would come from parsing a supply PDF
    supply_students = [
        {
            "student_id": "20R01A0501",
            "student_name": "JOHN DOE",
            "semester": "Semester 3",
            "year": "2nd Year",
            "subjects": [
                {
                    "subject_code": "CS301",
                    "subject_name": "Data Structures",
                    "grade": "C",
                    "result": "Pass",
                    "credits": 4
                },
                {
                    "subject_code": "MA301", 
                    "subject_name": "Mathematics III",
                    "grade": "B",
                    "result": "Pass",
                    "credits": 4
                }
            ]
        },
        {
            "student_id": "20R01A0502",
            "student_name": "JANE SMITH",
            "semester": "Semester 3", 
            "year": "2nd Year",
            "subjects": [
                {
                    "subject_code": "CS301",
                    "subject_name": "Data Structures",
                    "grade": "B+",
                    "result": "Pass",
                    "credits": 4
                },
                {
                    "subject_code": "EN301",
                    "subject_name": "Technical English",
                    "grade": "A",
                    "result": "Pass", 
                    "credits": 3
                }
            ]
        }
    ]
    
    # Mock existing regular results (what would be in Firebase)
    existing_regular_results = {
        "20R01A0501": {
            "student_id": "20R01A0501",
            "student_name": "JOHN DOE",
            "subjects": [
                {
                    "subject_code": "CS301",
                    "subject_name": "Data Structures", 
                    "grade": "F",
                    "result": "Fail",
                    "attempts": 1,
                    "credits": 4
                },
                {
                    "subject_code": "MA301",
                    "subject_name": "Mathematics III",
                    "grade": "D", 
                    "result": "Pass",
                    "attempts": 1,
                    "credits": 4
                },
                {
                    "subject_code": "PH301",
                    "subject_name": "Engineering Physics",
                    "grade": "C",
                    "result": "Pass", 
                    "attempts": 1,
                    "credits": 3
                }
            ]
        },
        "20R01A0502": {
            "student_id": "20R01A0502", 
            "student_name": "JANE SMITH",
            "subjects": [
                {
                    "subject_code": "CS301",
                    "subject_name": "Data Structures",
                    "grade": "B",
                    "result": "Pass",
                    "attempts": 1,
                    "credits": 4
                },
                {
                    "subject_code": "MA301",
                    "subject_name": "Mathematics III", 
                    "grade": "F",
                    "result": "Fail",
                    "attempts": 1,
                    "credits": 4
                }
            ]
        }
    }
    
    print("📚 EXISTING REGULAR RESULTS:")
    for student_id, data in existing_regular_results.items():
        print(f"   {student_id}: {data['student_name']}")
        for subject in data['subjects']:
            print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']}) - Attempt #{subject['attempts']}")
    
    print("\n📖 SUPPLY PDF RESULTS:")
    for student in supply_students:
        print(f"   {student['student_id']}: {student['student_name']}")
        for subject in student['subjects']:
            print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']})")
    
    # Simulate smart merge processing
    print("\n🔄 SMART MERGE PROCESSING:")
    print("=" * 40)
    
    merge_stats = {
        'students_processed': 0,
        'students_updated': 0,
        'subjects_overwritten': 0,
        'subjects_added': 0, 
        'total_attempts_tracked': 0,
        'grade_improvements': []
    }
    
    upload_timestamp = datetime.now().isoformat()
    
    for supply_student in supply_students:
        student_id = supply_student['student_id']
        merge_stats['students_processed'] += 1
        
        if student_id in existing_regular_results:
            print(f"\n🔍 Processing {student_id} - {supply_student['student_name']}")
            merge_stats['students_updated'] += 1
            
            existing_student = existing_regular_results[student_id]
            existing_subjects = {s['subject_code']: s for s in existing_student['subjects']}
            
            for supply_subject in supply_student['subjects']:
                subject_code = supply_subject['subject_code']
                supply_grade = supply_subject['grade']
                supply_result = supply_subject['result']
                
                if subject_code in existing_subjects:
                    existing_subject = existing_subjects[subject_code]
                    existing_grade = existing_subject['grade']
                    existing_result = existing_subject['result']
                    current_attempts = existing_subject.get('attempts', 1)
                    
                    # Check if we should overwrite
                    should_overwrite = False
                    overwrite_reason = ""
                    
                    # Rule 1: Failed to Pass
                    if existing_result == "Fail" and supply_result == "Pass":
                        should_overwrite = True
                        overwrite_reason = "Failed → Passed"
                    
                    # Rule 2: Grade improvement
                    elif is_grade_better(supply_grade, existing_grade):
                        should_overwrite = True
                        overwrite_reason = "Grade improved"
                    
                    if should_overwrite:
                        print(f"   ✅ OVERWRITE {subject_code}: {existing_grade} → {supply_grade} ({overwrite_reason})")
                        merge_stats['subjects_overwritten'] += 1
                        merge_stats['grade_improvements'].append({
                            'student_id': student_id,
                            'subject_code': subject_code,
                            'from_grade': existing_grade,
                            'to_grade': supply_grade,
                            'attempt_number': current_attempts + 1,
                            'reason': overwrite_reason
                        })
                        
                        # Update the existing record
                        existing_subject.update({
                            'grade': supply_grade,
                            'result': supply_result,
                            'attempts': current_attempts + 1,
                            'last_updated': upload_timestamp,
                            'improved_from_supply': True,
                            'improvement_reason': overwrite_reason
                        })
                    else:
                        print(f"   📝 TRACK {subject_code}: {supply_grade} (no improvement from {existing_grade})")
                        existing_subject['attempts'] = current_attempts + 1
                        existing_subject['last_supply_attempt'] = upload_timestamp
                    
                    merge_stats['total_attempts_tracked'] += 1
                    
                else:
                    # New subject from supply
                    print(f"   ➕ ADD {subject_code}: {supply_grade} (new subject)")
                    existing_student['subjects'].append({
                        **supply_subject,
                        'attempts': 1,
                        'added_from_supply': True,
                        'added_at': upload_timestamp
                    })
                    merge_stats['subjects_added'] += 1
        else:
            print(f"⚠️ Student {student_id} not found in existing records")
    
    print("\n📊 FINAL MERGE STATISTICS:")
    print("=" * 40)
    for key, value in merge_stats.items():
        if key != 'grade_improvements':
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("\n🎉 GRADE IMPROVEMENTS:")
    for improvement in merge_stats['grade_improvements']:
        print(f"   {improvement['student_id']} - {improvement['subject_code']}: "
              f"{improvement['from_grade']} → {improvement['to_grade']} "
              f"(Attempt #{improvement['attempt_number']}) - {improvement['reason']}")
    
    print("\n✅ FINAL STUDENT RECORDS:")
    print("=" * 40)
    for student_id, data in existing_regular_results.items():
        print(f"\n📝 {student_id}: {data['student_name']}")
        for subject in data['subjects']:
            attempts_str = f"Attempt #{subject.get('attempts', 1)}"
            improved_flag = "📈" if subject.get('improved_from_supply') else ""
            new_flag = "🆕" if subject.get('added_from_supply') else ""
            print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']}) - {attempts_str} {improved_flag}{new_flag}")
    
    return merge_stats

def is_grade_better(new_grade, old_grade):
    """Check if new grade is better than old grade"""
    grade_order = ['O', 'A+', 'A', 'B+', 'B', 'C', 'D', 'F', 'Ab', 'MP']
    
    try:
        old_index = grade_order.index(old_grade) if old_grade in grade_order else len(grade_order)
        new_index = grade_order.index(new_grade) if new_grade in grade_order else len(grade_order)
        return new_index < old_index  # Lower index = better grade
    except:
        return False

def show_api_usage_examples():
    """Show practical examples of using the API"""
    print("\n\n🌐 API USAGE EXAMPLES")
    print("=" * 60)
    
    print("\n1️⃣ Using curl (Command line):")
    print("""
# Upload supply PDF to production server
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" \\
  -H "X-API-Key: your-api-key-here" \\
  -F "pdf=@BTECH_2-1_SUPPLY_FEB_2025.pdf" \\
  -F "format=jntuk"
""")
    
    print("2️⃣ Using Python requests:")
    print("""
import requests

# Upload supply PDF
url = "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf"
with open("BTECH_2-1_SUPPLY_FEB_2025.pdf", "rb") as f:
    files = {"pdf": f}
    data = {"format": "jntuk"}
    headers = {"X-API-Key": "your-api-key-here"}
    
    response = requests.post(url, files=files, data=data, headers=headers)
    result = response.json()
    
    print(f"Students processed: {result['stats']['total_processed']}")
    print(f"Subjects overwritten: {result['stats']['subjects_overwritten']}")
""")
    
    print("3️⃣ Start local server for testing:")
    print("""
# In your backend directory
cd "c:\\Users\\jeshw_3agky5x\\Desktop\\student-result-project\\Result-Analysis\\backend"

# Start the Flask server
python app.py

# Then use this URL for testing
# http://localhost:5000/upload-supply-pdf
""")

if __name__ == "__main__":
    test_supply_processing()
    show_api_usage_examples()
