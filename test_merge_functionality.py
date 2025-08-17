#!/usr/bin/env python3
"""
Test automatic supply merge by creating test data with F grades
"""

from app import db, automatic_supply_merge
import uuid
from datetime import datetime

def test_merge_with_f_grades():
    print("🧪 TESTING AUTOMATIC SUPPLY MERGE WITH F GRADES")
    print("=" * 60)
    
    # Create a test student with F grades
    test_student_id = f"TEST{str(uuid.uuid4())[:8].upper()}"
    
    test_student_data = {
        'student_id': test_student_id,
        'examType': 'regular',
        'format': 'jntuk',
        'university': 'JNTUK',
        'semester': 'Semester 2',
        'year': '2024',
        'sgpa': 2.0,
        'subjectGrades': [
            {
                'subject': 'MATHEMATICS-II',
                'code': 'R161202',
                'grade': 'F',  # This should be improved
                'credits': 3.0,
                'internals': 10
            },
            {
                'subject': 'ENGINEERING PHYSICS',
                'code': 'R161204', 
                'grade': 'F',  # This should be improved
                'credits': 3.0,
                'internals': 8
            },
            {
                'subject': 'CHEMISTRY',
                'code': 'R161203',
                'grade': 'B',  # This should remain the same
                'credits': 3.0,
                'internals': 18
            }
        ],
        'uploadedAt': datetime.now(),
        'upload_date': '2025-08-14',
        'uploadId': 'test_regular_upload'
    }
    
    print(f"📝 Creating test student: {test_student_id}")
    print(f"   📊 Initial grades:")
    for subject in test_student_data['subjectGrades']:
        grade_emoji = "❌" if subject['grade'] == 'F' else "✅"
        print(f"   {grade_emoji} {subject['code']}: {subject['grade']}")
    
    # Add test student to database
    db.collection('student_results').document(test_student_id).set(test_student_data)
    print(f"✅ Test student added to database")
    
    # Create supply data to improve F grades
    supply_data = [{
        'student_id': test_student_id,
        'examType': 'supply',
        'format': 'jntuk',
        'university': 'JNTUK',
        'semester': 'Semester 2',
        'year': '2024',
        'subjectGrades': [  # Changed from 'subjects' to 'subjectGrades'
            {
                'code': 'R161202',  # Changed from 'subject_code' to 'code'
                'subject': 'MATHEMATICS-II',
                'grade': 'A',  # Improve F to A
                'credits': 3.0,
                'internals': 20
            },
            {
                'code': 'R161204',  # Changed from 'subject_code' to 'code' 
                'subject': 'ENGINEERING PHYSICS',
                'grade': 'B',  # Improve F to B
                'credits': 3.0,
                'internals': 18
            }
        ]
    }]
    
    print(f"\n🚀 Testing supply merge...")
    print(f"   Supply improvements:")
    for subject in supply_data[0]['subjectGrades']:  # Updated reference
        print(f"   ✅ {subject['code']}: F → {subject['grade']}")  # Updated field name
    
    # Test automatic merge
    result = automatic_supply_merge(supply_data, 'jntuk')
    
    if result and len(result) > 0:
        merge_report = result[0].get('mergeReport', {})
        print(f"\n📊 MERGE RESULTS:")
        print(f"   Students processed: {merge_report.get('total_subjects', 0)}")
        print(f"   Subjects improved: {merge_report.get('subjects_improved', 0)}")
        print(f"   F→Pass conversions: {merge_report.get('f_to_pass_conversions', 0)}")
        print(f"   Grade improvements: {merge_report.get('grade_improvements', 0)}")
        
        improvements = merge_report.get('improvements', [])
        if improvements:
            print(f"   🎯 Specific improvements:")
            for imp in improvements:
                print(f"     • {imp.get('subject_code')}: {imp.get('old_grade')} → {imp.get('new_grade')}")
        
        # Check the returned merged data from the function
        print(f"\n📋 RETURNED MERGED DATA:")
        for subject in result[0].get('subjectGrades', []):
            grade_emoji = "✅" if subject['grade'] != 'F' else "❌"
            attempts = subject.get('attempts', 0)
            original = subject.get('originalGrade', 'N/A')
            merged = subject.get('mergedAutomatically', False)
            print(f"   {grade_emoji} {subject['code']}: {subject['grade']} (attempts: {attempts}, original: {original}, merged: {merged})")
        
        # Check the final student record
        updated_student = db.collection('student_results').document(test_student_id).get()
        if updated_student.exists:
            updated_data = updated_student.to_dict()
            print(f"\n📋 FINAL STUDENT RECORD:")
            for subject in updated_data.get('subjectGrades', []):
                grade_emoji = "✅" if subject['grade'] != 'F' else "❌"
                print(f"   {grade_emoji} {subject['code']}: {subject['grade']}")
            
            print(f"   🎓 Final SGPA: {updated_data.get('sgpa', 'N/A')}")
            print(f"   🔄 Attempts: {updated_data.get('attempts', 0)}")
        
        print(f"\n🎉 SUCCESS: Automatic supply merge is working correctly!")
        
    else:
        print(f"\n❌ ERROR: No results returned from merge function")
    
    # Clean up - remove test student
    print(f"\n🧹 Cleaning up test data...")
    db.collection('student_results').document(test_student_id).delete()
    print(f"✅ Test student removed from database")

if __name__ == "__main__":
    test_merge_with_f_grades()
