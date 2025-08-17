#!/usr/bin/env python3
"""
Test real automatic supply merge functionality
"""

from app import db, automatic_supply_merge

def test_real_merge():
    print("🔍 FINDING STUDENT WITH F GRADES FOR TESTING...")
    print("=" * 50)
    
    # Find a student with F grades
    docs = list(db.collection('students').where('examType', '==', 'regular').limit(50).stream())
    student_with_f = None
    
    for doc in docs:
        data = doc.to_dict()
        subjects = data.get('subjectGrades', [])
        f_grades = [s for s in subjects if s.get('grade') == 'F']
        
        if f_grades:
            student_with_f = data
            print(f"📊 Found student {data['student_id']} with {len(f_grades)} F grades:")
            for f in f_grades[:3]:  # Show first 3 F grades
                print(f"  ❌ {f.get('code', 'N/A')}: {f.get('grade')} - {f.get('subject', 'N/A')}")
            break
    
    if not student_with_f:
        print("⚠️ No student with F grades found for testing")
        return
    
    # Create test supply data to improve those F grades
    student_id = student_with_f['student_id']
    f_subjects = [s for s in student_with_f.get('subjectGrades', []) if s.get('grade') == 'F']
    
    print(f"\n🧪 CREATING SUPPLY TEST DATA FOR {student_id}")
    print("=" * 50)
    
    # Create supply grades with passing grades for F subjects
    supply_subjects = []
    for i, f_subject in enumerate(f_subjects[:2]):  # Test with first 2 F subjects
        new_grade = ['A', 'B', 'C', 'D', 'E'][i % 5]  # Cycle through passing grades
        supply_subjects.append({
            'subject_code': f_subject.get('code'),
            'subject': f_subject.get('subject'),
            'grade': new_grade,
            'credits': f_subject.get('credits', 3.0),
            'internals': f_subject.get('internals', 15)
        })
        print(f"  ✅ {f_subject.get('code')}: F → {new_grade}")
    
    test_supply_data = [{
        'student_id': student_id,
        'subjects': supply_subjects
    }]
    
    print(f"\n🚀 TESTING AUTOMATIC SUPPLY MERGE...")
    print("=" * 50)
    
    # Test the merge
    result = automatic_supply_merge(test_supply_data, 'jntuk')
    
    if result:
        merge_report = result[0].get('mergeReport', {})
        print(f"📈 MERGE RESULTS:")
        print(f"  Students processed: {merge_report.get('total_subjects', 0)}")
        print(f"  Subjects improved: {merge_report.get('subjects_improved', 0)}")
        print(f"  F→Pass conversions: {merge_report.get('f_to_pass_conversions', 0)}")
        print(f"  Grade improvements: {merge_report.get('grade_improvements', 0)}")
        
        improvements = merge_report.get('improvements', [])
        if improvements:
            print(f"  🎯 Improvements made:")
            for imp in improvements:
                print(f"    • {imp.get('subject_code')}: {imp.get('old_grade')} → {imp.get('new_grade')}")
        else:
            print("  ⚠️ No improvements detected")
    else:
        print("  ❌ No results returned from merge function")

if __name__ == "__main__":
    test_real_merge()
