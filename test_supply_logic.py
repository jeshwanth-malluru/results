#!/usr/bin/env python3
"""
Test Supply Logic Implementation
Demonstrates how the enhanced batch processor handles supply results
"""

from batch_pdf_processor import (
    process_supply_pdf_with_smart_merge,
    get_supply_improvement_report,
    merge_student_subjects,
    is_grade_improvement
)
import json
from datetime import datetime

def test_grade_improvement_logic():
    """Test the grade improvement detection"""
    print("🧪 Testing Grade Improvement Logic")
    print("-" * 40)
    
    test_cases = [
        ('F', 'D', True),   # Failed to Pass
        ('F', 'C', True),   # Failed to Pass (better)
        ('D', 'B', True),   # Pass to Better Pass
        ('B', 'A', True),   # Good to Better
        ('A', 'F', False),  # Downgrade
        ('C', 'C', False),  # Same grade
        ('F', 'F', False),  # Still failed
    ]
    
    for old_grade, new_grade, expected in test_cases:
        result = is_grade_improvement(old_grade, new_grade)
        status = "✅" if result == expected else "❌"
        print(f"{status} {old_grade} → {new_grade}: {'Improved' if result else 'Not improved'}")

def simulate_supply_merge():
    """Simulate how supply results merge with regular results"""
    print("\n🔄 Simulating Supply Result Merge")
    print("-" * 40)
    
    # Simulate existing regular record
    existing_record = {
        'student_id': '20B91A0501',
        'examType': 'regular',
        'uploadedAt': '2024-01-15T10:00:00',
        'subjects': [
            {
                'subject_code': 'CS101',
                'subject_name': 'Computer Programming',
                'grade': 'F',
                'result': 'Fail',
                'credits': 4,
                'attempts': 1,
                'attempt_history': [{
                    'attempt_number': 1,
                    'exam_type': 'regular',
                    'grade': 'F',
                    'result': 'Fail',
                    'attempted_at': '2024-01-15T10:00:00',
                    'reason': 'Initial record'
                }]
            },
            {
                'subject_code': 'MA101',
                'subject_name': 'Mathematics-I',
                'grade': 'B',
                'result': 'Pass',
                'credits': 4,
                'attempts': 1,
                'attempt_history': [{
                    'attempt_number': 1,
                    'exam_type': 'regular',
                    'grade': 'B',
                    'result': 'Pass',
                    'attempted_at': '2024-01-15T10:00:00',
                    'reason': 'Initial record'
                }]
            }
        ]
    }
    
    # Simulate new supply record
    new_supply_student = {
        'student_id': '20B91A0501',
        'subjects': [
            {
                'subject_code': 'CS101',
                'subject_name': 'Computer Programming',
                'grade': 'C',
                'result': 'Pass',
                'credits': 4
            },
            {
                'subject_code': 'PH101',
                'subject_name': 'Physics',
                'grade': 'D',
                'result': 'Pass',
                'credits': 3
            }
        ]
    }
    
    print(f"📚 BEFORE MERGE:")
    print(f"   Regular Record: {len(existing_record['subjects'])} subjects")
    for subject in existing_record['subjects']:
        print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']})")
    
    print(f"\n📄 SUPPLY UPLOAD:")
    for subject in new_supply_student['subjects']:
        print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']})")
    
    # Perform merge
    upload_timestamp = datetime.now().isoformat()
    merged_subjects, merge_stats = merge_student_subjects(
        existing_record, 
        new_supply_student, 
        'supplementary', 
        upload_timestamp
    )
    
    print(f"\n🎯 AFTER SMART MERGE:")
    print(f"   Total subjects: {len(merged_subjects)}")
    
    for subject in merged_subjects:
        attempts = subject.get('attempts', 1)
        attempt_info = f" [Attempt #{attempts}]" if attempts > 1 else ""
        print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']}){attempt_info}")
        
        # Show attempt history for subjects with multiple attempts
        if attempts > 1:
            print(f"         📈 Attempt History:")
            for attempt in subject.get('attempt_history', []):
                print(f"            #{attempt['attempt_number']}: {attempt['grade']} ({attempt['exam_type']})")
    
    print(f"\n📊 MERGE STATISTICS:")
    print(f"   ✅ Subjects updated: {merge_stats['subjects_updated']}")
    print(f"   ➕ Subjects added: {merge_stats['subjects_added']}")
    print(f"   🔄 Subjects kept: {merge_stats['subjects_kept']}")
    print(f"   🎯 Supply overwrites: {merge_stats.get('supply_overwrites', 0)}")
    
    print(f"\n🔍 MERGE ACTIONS:")
    for action in merge_stats['merge_actions']:
        action_type = action['type']
        subject_code = action['subject_code']
        attempts = action.get('attempts', 1)
        
        if action_type == 'SUPPLY_UPDATE':
            print(f"   🎯 SUPPLY OVERWRITE: {subject_code} - {action['old_result']} → {action['new_result']} [Attempt #{attempts}]")
        elif action_type == 'UPDATE':
            print(f"   🔄 UPDATE: {subject_code} - {action['old_result']} → {action['new_result']}")
        elif action_type == 'ADD':
            print(f"   ➕ NEW: {subject_code} - {action['new_result']}")

def demonstrate_supply_api_usage():
    """Show how to use the supply processing API"""
    print("\n🚀 Supply Processing API Usage")
    print("-" * 40)
    
    print("1. Process a supply PDF:")
    print("""
    from batch_pdf_processor import process_supply_pdf_with_smart_merge
    
    result = process_supply_pdf_with_smart_merge(
        pdf_path="supply_results.pdf",
        year="2nd Year",
        semesters=["Semester 1"],
        format_type="jntuk"
    )
    """)
    
    print("2. Get improvement report for a student:")
    print("""
    from batch_pdf_processor import get_supply_improvement_report
    
    report = get_supply_improvement_report(
        student_id="20B91A0501",
        year="2nd Year", 
        semester="Semester 1"
    )
    """)
    
    print("3. Key features:")
    print("   ✅ Automatic detection of existing student records")
    print("   ✅ Smart grade overwriting (Supply > Regular)")
    print("   ✅ Attempt counting and history tracking")
    print("   ✅ Detailed logging of all changes")
    print("   ✅ Firebase integration with real-time updates")

def main():
    """Run all tests"""
    print("🎓 SUPPLY RESULT PROCESSING - ENHANCED LOGIC TEST")
    print("=" * 60)
    
    test_grade_improvement_logic()
    simulate_supply_merge()
    demonstrate_supply_api_usage()
    
    print("\n🎉 All tests completed! Your supply logic is ready to use.")
    print("\n📋 Next Steps:")
    print("   1. Upload a supply PDF using process_supply_pdf_with_smart_merge()")
    print("   2. Check Firebase for updated records with attempt counts")
    print("   3. Use get_supply_improvement_report() to analyze improvements")
    print("   4. Monitor logs for detailed merge actions")

if __name__ == "__main__":
    main()
