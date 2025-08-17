#!/usr/bin/env python3
"""
Test automatic supply merge functionality
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

# Add the current directory to Python path
sys.path.append('.')

# Initialize Firebase
if not firebase_admin._apps:
    try:
        if os.path.exists('serviceAccount.json'):
            cred = credentials.Certificate('serviceAccount.json')
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase initialized successfully!")
        else:
            print("❌ serviceAccount.json not found")
            exit(1)
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        exit(1)

db = firestore.client()

def test_supply_merge():
    """Test if automatic supply merge is working"""
    
    print("🧪 TESTING AUTOMATIC SUPPLY MERGE")
    print("=" * 50)
    
    # Check if we have any existing students
    students_ref = db.collection('student_results')
    existing_docs = list(students_ref.limit(5).stream())
    
    print(f"📊 Found {len(existing_docs)} existing student records")
    
    if len(existing_docs) == 0:
        print("❌ No existing students found - cannot test supply merge")
        return
    
    # Show sample existing student
    sample_doc = existing_docs[0]
    sample_data = sample_doc.to_dict()
    student_id = sample_data.get('student_id', 'Unknown')
    exam_type = sample_data.get('examType', 'Unknown')
    subjects = sample_data.get('subjectGrades', [])
    
    print(f"\n📋 Sample existing student:")
    print(f"  Student ID: {student_id}")
    print(f"  Exam Type: {exam_type}")
    print(f"  Subjects: {len(subjects)}")
    
    if subjects:
        print(f"  Sample subjects:")
        for i, subject in enumerate(subjects[:3]):
            code = subject.get('code', 'N/A')
            grade = subject.get('grade', 'N/A')
            print(f"    {i+1}. {code}: {grade}")
    
    # Create a test supply student with same ID but different grades
    test_supply_student = {
        'student_id': student_id,
        'examType': 'supply',
        'subjectGrades': []
    }
    
    # Create test supply subjects (simulate F→C conversion)
    if subjects:
        for subject in subjects[:2]:  # Test with first 2 subjects
            supply_subject = subject.copy()
            supply_subject['grade'] = 'C'  # Change to passing grade
            supply_subject['result'] = 'Pass'
            test_supply_student['subjectGrades'].append(supply_subject)
    
    print(f"\n🧪 Test supply data created:")
    print(f"  Student ID: {test_supply_student['student_id']}")
    print(f"  Supply subjects: {len(test_supply_student['subjectGrades'])}")
    
    # Now test the automatic merge function
    try:
        # Import the function from app.py
        from app import automatic_supply_merge
        
        print(f"\n🚀 Testing automatic_supply_merge function...")
        
        test_supply_students = [test_supply_student]
        merged_results = automatic_supply_merge(test_supply_students, 'jntuk')
        
        if merged_results:
            print(f"✅ Merge function returned {len(merged_results)} results")
            
            merged_student = merged_results[0]
            merge_report = merged_student.get('mergeReport', {})
            
            print(f"📊 Merge report:")
            print(f"  Students processed: {merge_report.get('total_subjects', 0)}")
            print(f"  Subjects improved: {merge_report.get('subjects_improved', 0)}")
            print(f"  F→Pass conversions: {merge_report.get('f_to_pass_conversions', 0)}")
            print(f"  Grade improvements: {merge_report.get('grade_improvements', 0)}")
            
            if merge_report.get('subjects_improved', 0) > 0:
                print("🎉 AUTOMATIC SUPPLY MERGE IS WORKING!")
            else:
                print("⚠️ No improvements detected - check merge logic")
                
        else:
            print("❌ Merge function returned None or empty results")
            
    except ImportError as e:
        print(f"❌ Could not import automatic_supply_merge: {e}")
    except Exception as e:
        print(f"❌ Error testing merge function: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_supply_merge()
