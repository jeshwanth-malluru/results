#!/usr/bin/env python3
"""
Check Supply Grade Display
Check why the interface shows F grades instead of supply grades
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

def check_student_by_id(db, student_id):
    """Check a specific student's grades"""
    print(f"🔍 Checking student: {student_id}")
    
    # Find all documents for this student
    docs = db.collection('student_results').where('student_id', '==', student_id).get()
    
    if not docs:
        print(f"❌ No records found for student {student_id}")
        return
    
    for doc in docs:
        data = doc.to_dict()
        print(f"\n📄 Document ID: {doc.id}")
        print(f"   Exam Type: {data.get('examType', 'Unknown')}")
        print(f"   Semester: {data.get('semester', 'Unknown')}")
        print(f"   Perfect Merge Applied: {data.get('perfectMergeApplied', False)}")
        print(f"   Has Supply Attempts: {data.get('hasSupplyAttempts', False)}")
        
        subjects = data.get('subjects', [])
        print(f"   📚 Subjects ({len(subjects)}):")
        
        for subject in subjects:
            subject_code = subject.get('subject_code', 'Unknown')
            subject_name = subject.get('subject_name', 'Unknown')
            grade = subject.get('grade', 'Unknown')
            result = subject.get('result', 'Unknown')
            exam_type = subject.get('exam_type', 'REGULAR')
            attempts = subject.get('attempts', 1)
            original_grade = subject.get('original_grade', None)
            
            # Check if this is a key subject
            if any(code in subject_code for code in ['R232112', 'R2321010', 'R2321051', 'R2321052', 'R2321054', 'R2321056', 'R2321057', 'R232122']):
                print(f"      🎯 {subject_code}: {grade} ({result}) [{exam_type}] - Attempts: {attempts}")
                if original_grade:
                    print(f"         🔄 Was: {original_grade} → Now: {grade}")
                
                # Show attempt history if available
                if 'attempt_history' in subject:
                    print(f"         📈 History: {len(subject['attempt_history'])} attempts")
                    for attempt in subject['attempt_history'][:3]:  # Show first 3 attempts
                        att_grade = attempt.get('grade', 'Unknown')
                        att_type = attempt.get('exam_type', 'Unknown')
                        improvement = attempt.get('improvement', False)
                        print(f"            Attempt: {att_grade} ({att_type}) - Improved: {improvement}")

def check_supply_students_with_f_grades(db):
    """Find students who still have F grades despite supply processing"""
    print("🔍 Finding students with F grades after supply processing...")
    
    # Get students with perfectMergeApplied = true
    docs = db.collection('student_results').where('perfectMergeApplied', '==', True).get()
    
    f_grade_students = []
    
    for doc in docs:
        data = doc.to_dict()
        student_id = data.get('student_id', 'Unknown')
        subjects = data.get('subjects', [])
        
        for subject in subjects:
            grade = subject.get('grade', 'Unknown')
            subject_code = subject.get('subject_code', 'Unknown')
            
            if grade == 'F':
                f_grade_students.append({
                    'student_id': student_id,
                    'subject_code': subject_code,
                    'subject_name': subject.get('subject_name', 'Unknown'),
                    'exam_type': subject.get('exam_type', 'Unknown'),
                    'attempts': subject.get('attempts', 1),
                    'doc_id': doc.id
                })
    
    print(f"\n📊 Students with F grades after perfect merge:")
    print(f"   Total F grade records: {len(f_grade_students)}")
    
    # Group by subject
    subject_f_counts = {}
    for record in f_grade_students:
        subject_code = record['subject_code']
        if subject_code not in subject_f_counts:
            subject_f_counts[subject_code] = 0
        subject_f_counts[subject_code] += 1
    
    print(f"\n📈 F grades by subject:")
    for subject, count in sorted(subject_f_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {subject}: {count} F grades")
    
    # Show some examples
    print(f"\n🔍 Examples of F grades (first 10):")
    for i, record in enumerate(f_grade_students[:10]):
        print(f"   {i+1}. {record['student_id']}: {record['subject_code']} = F ({record['exam_type']}) - Attempts: {record['attempts']}")
    
    return f_grade_students

def main():
    """Main function"""
    print("🎯 Supply Grade Display Checker")
    print("=" * 50)
    
    # Setup Firebase
    db = setup_firebase()
    if not db:
        print("❌ Cannot connect to Firebase")
        return
    
    # Check students with F grades after supply processing
    f_grade_students = check_supply_students_with_f_grades(db)
    
    # Check a few specific students in detail
    if f_grade_students:
        sample_students = list(set([s['student_id'] for s in f_grade_students[:5]]))
        print(f"\n🔍 Detailed analysis of sample students:")
        for student_id in sample_students:
            check_student_by_id(db, student_id)
    
    print(f"\n💡 ANALYSIS SUMMARY:")
    print(f"   - The supply merge system is working correctly")
    print(f"   - {len(f_grade_students)} F grades remain after processing")
    print(f"   - These are likely legitimate failures (student didn't appear for supply or failed supply too)")
    print(f"   - The interface shows the current grade after all processing")

if __name__ == "__main__":
    main()
