#!/usr/bin/env python3
"""
Firebase Supply Grade Check
Check if supply grades are properly merged in Firebase
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json

def setup_firebase():
    """Initialize Firebase"""
    try:
        app = firebase_admin.get_app()
        print("✅ Firebase already initialized")
        return firestore.client(app)
    except ValueError:
        try:
            cred = credentials.Certificate('serviceAccount.json')
            app = firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized")
            return firestore.client(app)
        except Exception as e:
            print(f"❌ Firebase setup error: {e}")
            return None

def check_specific_student_grades(db, student_id_to_check):
    """Check grades for a specific student"""
    print(f"🔍 Checking grades for student: {student_id_to_check}")
    
    # Find documents containing this student ID
    docs = db.collection('student_results').where('student_id', '==', student_id_to_check).get()
    
    if not docs:
        print(f"❌ No records found for student {student_id_to_check}")
        return
    
    for doc in docs:
        data = doc.to_dict()
        print(f"\n📄 Document: {doc.id}")
        print(f"   Exam Type: {data.get('examType', 'Unknown')}")
        print(f"   Last Updated: {data.get('lastUpdatedAt', 'Unknown')}")
        print(f"   Has Supply Attempts: {data.get('hasSupplyAttempts', False)}")
        print(f"   Perfect Merge Applied: {data.get('perfectMergeApplied', False)}")
        
        subjects = data.get('subjects', [])
        print(f"   Total Subjects: {len(subjects)}")
        
        # Check for ADS and other key subjects
        target_subjects = ['R232112', 'R2321052', 'R2321054', 'R2321010']  # ADS, DLCO, OOP, EVS
        
        for subject in subjects:
            subject_code = subject.get('subject_code', '')
            if subject_code in target_subjects or 'R232112' in subject_code:
                grade = subject.get('grade', 'Unknown')
                result = subject.get('result', 'Unknown')
                exam_type = subject.get('exam_type', 'Unknown')
                attempts = subject.get('attempts', 1)
                original_grade = subject.get('original_grade', None)
                
                print(f"   📚 {subject_code}: {grade} ({result}) - {exam_type} - Attempts: {attempts}")
                if original_grade:
                    print(f"      🔄 Original Grade: {original_grade} → {grade}")
                
                # Check for improvement history
                if 'attempt_history' in subject:
                    print(f"      📈 Attempt History: {len(subject['attempt_history'])} records")
                    for attempt in subject['attempt_history']:
                        attempt_num = attempt.get('attempt', 'Unknown')
                        attempt_grade = attempt.get('grade', 'Unknown')
                        attempt_type = attempt.get('exam_type', 'Unknown')
                        improvement = attempt.get('improvement', False)
                        print(f"         Attempt #{attempt_num}: {attempt_grade} ({attempt_type}) - Improved: {improvement}")

def check_ads_students(db):
    """Check students who have ADS subject"""
    print("🔍 Checking students with Advanced Data Structures subject...")
    
    # Query for documents containing ADS subject
    docs = db.collection('student_results').get()
    
    ads_students = []
    f_grade_count = 0
    pass_grade_count = 0
    
    for doc in docs:
        data = doc.to_dict()
        student_id = data.get('student_id', 'Unknown')
        subjects = data.get('subjects', [])
        
        for subject in subjects:
            subject_code = subject.get('subject_code', '')
            subject_name = subject.get('subject_name', '')
            
            # Check if this is ADS subject
            if 'R232112' in subject_code or 'ADVANCED DATA STRUCTURES' in subject_name.upper():
                grade = subject.get('grade', 'Unknown')
                result = subject.get('result', 'Unknown')
                exam_type = subject.get('exam_type', 'Unknown')
                attempts = subject.get('attempts', 1)
                
                ads_students.append({
                    'student_id': student_id,
                    'subject_code': subject_code,
                    'grade': grade,
                    'result': result,
                    'exam_type': exam_type,
                    'attempts': attempts,
                    'doc_id': doc.id
                })
                
                if grade == 'F':
                    f_grade_count += 1
                else:
                    pass_grade_count += 1
    
    print(f"\n📊 ADS Subject Analysis:")
    print(f"   Total ADS records: {len(ads_students)}")
    print(f"   F grades: {f_grade_count}")
    print(f"   Pass grades: {pass_grade_count}")
    
    # Show sample of F grades
    print(f"\n❌ Students with F grade in ADS (first 10):")
    f_students = [s for s in ads_students if s['grade'] == 'F']
    for i, student in enumerate(f_students[:10]):
        print(f"   {i+1}. {student['student_id']}: {student['grade']} ({student['exam_type']}) - Attempts: {student['attempts']}")
    
    # Show sample of pass grades
    print(f"\n✅ Students with passing grade in ADS (first 10):")
    pass_students = [s for s in ads_students if s['grade'] != 'F']
    for i, student in enumerate(pass_students[:10]):
        print(f"   {i+1}. {student['student_id']}: {student['grade']} ({student['exam_type']}) - Attempts: {student['attempts']}")
    
    return ads_students

def main():
    """Main function"""
    print("🔥 Firebase Supply Grade Checker")
    print("=" * 50)
    
    # Setup Firebase
    db = setup_firebase()
    if not db:
        print("❌ Cannot connect to Firebase")
        return
    
    # Check overall ADS statistics
    ads_students = check_ads_students(db)
    
    # Check specific students (you can modify these)
    specific_students = ['24485A0501', '24485A0502', '24485A0503']  # Replace with actual student IDs
    
    print(f"\n🎯 Detailed Analysis for Specific Students:")
    for student_id in specific_students:
        try:
            check_specific_student_grades(db, student_id)
        except Exception as e:
            print(f"❌ Error checking {student_id}: {e}")

if __name__ == "__main__":
    main()
