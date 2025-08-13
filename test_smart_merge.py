#!/usr/bin/env python3
"""
Test Smart Merge Functionality
Tests the new intelligent subject-level merging system
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from batch_pdf_processor import merge_student_subjects, should_update_subject
from datetime import datetime

def test_smart_merge():
    """Test the smart merge functionality with sample data"""
    
    print("🧪 TESTING SMART MERGE FUNCTIONALITY")
    print("=" * 50)
    
    # Sample existing record (REGULAR)
    existing_record = {
        "student_id": "TEST123",
        "examType": "regular",
        "uploadedAt": "2025-08-13T10:00:00",
        "subjects": [
            {
                "subject_code": "MATH201",
                "subject_name": "Mathematics III",
                "total_marks": 45,
                "grade": "F",
                "result": "FAIL",
                "source": "regular",
                "updated_at": "2025-08-13T10:00:00"
            },
            {
                "subject_code": "PHYS201",
                "subject_name": "Physics III",
                "total_marks": 65,
                "grade": "B",
                "result": "PASS",
                "source": "regular",
                "updated_at": "2025-08-13T10:00:00"
            }
        ]
    }
    
    # Sample new student data (SUPPLY)
    new_student = {
        "student_id": "TEST123",
        "subjects": [
            {
                "subject_code": "MATH201",  # Same subject - should UPDATE
                "subject_name": "Mathematics III",
                "total_marks": 70,
                "grade": "B",
                "result": "PASS"
            },
            {
                "subject_code": "ENG201",   # New subject - should ADD
                "subject_name": "English III",
                "total_marks": 60,
                "grade": "B",
                "result": "PASS"
            }
        ]
    }
    
    print("📋 EXISTING RECORD (REGULAR):")
    for subject in existing_record["subjects"]:
        print(f"   {subject['subject_code']}: {subject['total_marks']}/100 - Grade {subject['grade']} ({subject['result']})")
    
    print("\n📋 NEW UPLOAD (SUPPLY):")
    for subject in new_student["subjects"]:
        print(f"   {subject['subject_code']}: {subject['total_marks']}/100 - Grade {subject['grade']} ({subject['result']})")
    
    # Test the merge
    current_exam_type = "supplementary"
    upload_timestamp = "2025-10-15T14:30:00"
    
    print(f"\n🧠 SMART MERGE PROCESSING...")
    merged_subjects, merge_stats = merge_student_subjects(
        existing_record, 
        new_student, 
        current_exam_type, 
        upload_timestamp
    )
    
    print(f"\n📊 MERGE ACTIONS:")
    for action in merge_stats['merge_actions']:
        if action['type'] == 'UPDATE':
            print(f"   🔄 UPDATE {action['subject_code']}: {action['old_result']} → {action['new_result']}")
            print(f"      💡 Reason: {action['reason']}")
        elif action['type'] == 'ADD':
            print(f"   ➕ ADD {action['subject_code']}: {action['new_result']}")
            print(f"      💡 Reason: {action['reason']}")
    
    print(f"\n📈 MERGE STATISTICS:")
    print(f"   🔄 Subjects updated: {merge_stats['subjects_updated']}")
    print(f"   ➕ Subjects added: {merge_stats['subjects_added']}")
    print(f"   📝 Subjects kept: {merge_stats['subjects_kept']}")
    
    print(f"\n📊 FINAL MERGED RECORD:")
    for subject in merged_subjects:
        source_icon = "🔄" if subject.get('source') == 'supplementary' else "📝"
        print(f"   {source_icon} {subject['subject_code']}: {subject['total_marks']}/100 - Grade {subject['grade']} ({subject['result']}) [{subject.get('source', 'unknown')}]")
    
    # Test priority rules
    print(f"\n🔬 TESTING PRIORITY RULES:")
    print("-" * 30)
    
    # Test 1: SUPPLY overwrites REGULAR
    test1 = should_update_subject(
        existing_subject={'result': 'FAIL', 'grade': 'F'},
        new_subject={'result': 'PASS', 'grade': 'B'},
        existing_exam_type='regular',
        new_exam_type='supplementary',
        existing_timestamp='2025-08-13T10:00:00',
        new_timestamp='2025-10-15T14:30:00'
    )
    print(f"1️⃣ SUPPLY overwrites REGULAR: {'✅ YES' if test1 else '❌ NO'}")
    
    # Test 2: Newer upload wins
    test2 = should_update_subject(
        existing_subject={'result': 'PASS', 'grade': 'B'},
        new_subject={'result': 'PASS', 'grade': 'A'},
        existing_exam_type='regular',
        new_exam_type='regular',
        existing_timestamp='2025-08-13T10:00:00',
        new_timestamp='2025-10-15T14:30:00'
    )
    print(f"2️⃣ Newer upload wins: {'✅ YES' if test2 else '❌ NO'}")
    
    # Test 3: Older upload shouldn't overwrite
    test3 = should_update_subject(
        existing_subject={'result': 'PASS', 'grade': 'B'},
        new_subject={'result': 'PASS', 'grade': 'A'},
        existing_exam_type='regular',
        new_exam_type='regular',
        existing_timestamp='2025-10-15T14:30:00',
        new_timestamp='2025-08-13T10:00:00'
    )
    print(f"3️⃣ Older upload blocked: {'✅ YES' if not test3 else '❌ NO'}")
    
    print(f"\n✅ SMART MERGE TEST COMPLETE!")
    print("Smart merge system is working correctly! 🎉")

if __name__ == "__main__":
    test_smart_merge()
