#!/usr/bin/env python3
"""
Test Supply Merge Logic
Test if F grades in regular results are properly replaced by passing grades (A, B, C, D, E) in supply results
"""

import json
from datetime import datetime

def is_grade_improvement(old_grade, new_grade):
    """Check if new grade is better than old grade"""
    grade_hierarchy = ['O', 'A+', 'A', 'B+', 'B', 'C', 'D', 'F', 'Ab', 'MP']
    
    try:
        old_index = grade_hierarchy.index(old_grade) if old_grade in grade_hierarchy else len(grade_hierarchy)
        new_index = grade_hierarchy.index(new_grade) if new_grade in grade_hierarchy else len(grade_hierarchy)
        return new_index < old_index  # Lower index = better grade
    except:
        return False

def smart_supply_merge_by_subject(existing_subjects, supply_subjects, supply_timestamp):
    """
    Smart merge logic for supply results with existing regular results:
    1. Find student by register number
    2. Check each subject code in supply results
    3. If student failed in regular but passed in supply - OVERWRITE grade
    4. Track attempt count alongside the grade
    5. Preserve original regular results for already passed subjects
    """
    merged_subjects = existing_subjects.copy()
    merge_report = {
        'subjects_overwritten': 0,
        'subjects_added': 0,
        'attempts_tracked': 0,
        'improvements_detected': [],
        'actions': []
    }
    
    for subject_code, supply_subject in supply_subjects.items():
        supply_grade = supply_subject.get('grade', 'F')
        supply_result = supply_subject.get('result', 'Fail')
        
        if subject_code in existing_subjects:
            existing_subject = existing_subjects[subject_code]
            existing_grade = existing_subject.get('grade', 'F')
            existing_result = existing_subject.get('result', 'Fail')
            current_attempts = existing_subject.get('attempts', 1)
            
            # Check if student failed in regular but passed in supply
            regular_failed = existing_result.lower() in ['fail', 'f'] or existing_grade == 'F'
            supply_passed = supply_result.lower() in ['pass', 'p'] and supply_grade != 'F'
            supply_improved = is_grade_improvement(existing_grade, supply_grade)
            
            print(f"  📊 Subject {subject_code}:")
            print(f"      Regular: {existing_grade} ({existing_result})")
            print(f"      Supply:  {supply_grade} ({supply_result})")
            print(f"      Regular failed: {regular_failed}, Supply passed: {supply_passed}, Improved: {supply_improved}")
            
            if regular_failed and supply_passed:
                # OVERWRITE: Student failed in regular but passed in supply
                merged_subjects[subject_code] = {
                    **supply_subject,
                    'attempts': current_attempts + 1,
                    'exam_type': 'SUPPLY',
                    'original_grade': existing_grade,
                    'original_result': existing_result,
                    'improved_from_regular': True,
                    'improvement_date': supply_timestamp
                }
                
                merge_report['subjects_overwritten'] += 1
                merge_report['improvements_detected'].append({
                    'subject_code': subject_code,
                    'from_grade': existing_grade,
                    'to_grade': supply_grade,
                    'attempt_number': current_attempts + 1
                })
                merge_report['actions'].append(f"✅ {subject_code}: F→{supply_grade} (Regular FAILED → Supply PASSED)")
                print(f"      ✅ OVERWRITTEN: {existing_grade} → {supply_grade}")
                
            elif supply_improved:
                # OVERWRITE: Supply grade is better than existing grade
                merged_subjects[subject_code] = {
                    **supply_subject,
                    'attempts': current_attempts + 1,
                    'exam_type': 'SUPPLY',
                    'original_grade': existing_grade,
                    'original_result': existing_result,
                    'improved_grade': True,
                    'improvement_date': supply_timestamp
                }
                
                merge_report['subjects_overwritten'] += 1
                merge_report['improvements_detected'].append({
                    'subject_code': subject_code,
                    'from_grade': existing_grade,
                    'to_grade': supply_grade,
                    'attempt_number': current_attempts + 1
                })
                merge_report['actions'].append(f"📈 {subject_code}: {existing_grade}→{supply_grade} (Grade IMPROVED)")
                print(f"      📈 IMPROVED: {existing_grade} → {supply_grade}")
                
            else:
                # TRACK ONLY: No improvement, just track the attempt
                merged_subjects[subject_code]['attempts'] = current_attempts + 1
                merged_subjects[subject_code]['last_supply_attempt'] = supply_timestamp
                merge_report['actions'].append(f"📝 {subject_code}: No improvement ({supply_grade})")
                print(f"      📝 NO CHANGE: {existing_grade} (supply: {supply_grade})")
            
            merge_report['attempts_tracked'] += 1
            
        else:
            # NEW SUBJECT: Add supply subject as new
            merged_subjects[subject_code] = {
                **supply_subject,
                'attempts': 1,
                'exam_type': 'SUPPLY',
                'new_subject_from_supply': True,
                'added_date': supply_timestamp
            }
            
            merge_report['subjects_added'] += 1
            merge_report['actions'].append(f"➕ {subject_code}: NEW SUBJECT ({supply_grade})")
            print(f"  ➕ NEW SUBJECT {subject_code}: {supply_grade}")
    
    return merged_subjects, merge_report

def test_supply_merge():
    """Test the supply merge logic with sample data"""
    print("🧪 Testing Supply Merge Logic")
    print("=" * 50)
    
    # Sample regular result (student failed in ADS and DSA)
    regular_subjects = {
        'R2321012': {  # UNIVERSAL HUMAN VALUES
            'subject_code': 'R2321012',
            'subject_name': 'UNIVERSAL HUMAN VALUES-UNDERSTANDING HAR',
            'grade': 'C',
            'result': 'Pass',
            'attempts': 1
        },
        'R232112': {   # ADVANCED DATA STRUCTURES (FAILED)
            'subject_code': 'R232112',
            'subject_name': 'ADVANCED DATA STRUCTURES & ALGORITHMS',
            'grade': 'F',
            'result': 'Fail',
            'attempts': 1
        },
        'R2321052': {  # DIGITAL LOGIC (FAILED)
            'subject_code': 'R2321052',
            'subject_name': 'DIGITAL LOGIC & COMPUTER ORGANIZATION',
            'grade': 'F',
            'result': 'Fail',
            'attempts': 1
        },
        'R2321054': {  # OOP JAVA (PASSED)
            'subject_code': 'R2321054',
            'subject_name': 'OBJECT ORIENTED PROGRAMMING THROUGH JAVA',
            'grade': 'B',
            'result': 'Pass',
            'attempts': 1
        }
    }
    
    # Sample supply result (student passed ADS with grade A, DSA with grade C)
    supply_subjects = {
        'R232112': {   # ADVANCED DATA STRUCTURES (NOW PASSED)
            'subject_code': 'R232112',
            'subject_name': 'ADVANCED DATA STRUCTURES & ALGORITHMS',
            'grade': 'A',
            'result': 'Pass'
        },
        'R2321052': {  # DIGITAL LOGIC (NOW PASSED)
            'subject_code': 'R2321052',
            'subject_name': 'DIGITAL LOGIC & COMPUTER ORGANIZATION',
            'grade': 'C',
            'result': 'Pass'
        }
    }
    
    print("📚 REGULAR SUBJECTS:")
    for code, subject in regular_subjects.items():
        print(f"  {code}: {subject['grade']} ({subject['result']}) - {subject['subject_name']}")
    
    print("\n🎯 SUPPLY SUBJECTS:")
    for code, subject in supply_subjects.items():
        print(f"  {code}: {subject['grade']} ({subject['result']}) - {subject['subject_name']}")
    
    print("\n🔄 MERGING...")
    
    # Test the merge
    supply_timestamp = datetime.now().isoformat()
    merged_subjects, merge_report = smart_supply_merge_by_subject(
        regular_subjects, 
        supply_subjects, 
        supply_timestamp
    )
    
    print(f"\n📊 MERGE RESULTS:")
    print(f"  Subjects overwritten: {merge_report['subjects_overwritten']}")
    print(f"  Subjects added: {merge_report['subjects_added']}")
    print(f"  Attempts tracked: {merge_report['attempts_tracked']}")
    
    print(f"\n📋 MERGE ACTIONS:")
    for action in merge_report['actions']:
        print(f"  {action}")
    
    print(f"\n🎯 IMPROVEMENTS DETECTED:")
    for improvement in merge_report['improvements_detected']:
        print(f"  {improvement['subject_code']}: {improvement['from_grade']} → {improvement['to_grade']} (Attempt #{improvement['attempt_number']})")
    
    print(f"\n📚 FINAL MERGED SUBJECTS:")
    for code, subject in merged_subjects.items():
        exam_type = subject.get('exam_type', 'REGULAR')
        original_grade = subject.get('original_grade', '')
        current_grade = subject.get('grade', '')
        
        if original_grade and original_grade != current_grade:
            print(f"  {code}: {current_grade} ({exam_type}) [Was: {original_grade}] ✅ IMPROVED")
        else:
            print(f"  {code}: {current_grade} ({exam_type})")
    
    # Test specific F→Pass conversion
    print(f"\n🔍 F→PASS CONVERSION TEST:")
    ads_before = regular_subjects.get('R232112', {}).get('grade', 'Not Found')
    ads_after = merged_subjects.get('R232112', {}).get('grade', 'Not Found')
    print(f"  ADS (R232112): {ads_before} → {ads_after}")
    
    dsa_before = regular_subjects.get('R2321052', {}).get('grade', 'Not Found')
    dsa_after = merged_subjects.get('R2321052', {}).get('grade', 'Not Found')
    print(f"  DSA (R2321052): {dsa_before} → {dsa_after}")
    
    # Verify the conversion worked
    if ads_before == 'F' and ads_after == 'A':
        print("  ✅ ADS: F→A conversion SUCCESS")
    else:
        print("  ❌ ADS: F→A conversion FAILED")
        
    if dsa_before == 'F' and dsa_after == 'C':
        print("  ✅ DSA: F→C conversion SUCCESS")
    else:
        print("  ❌ DSA: F→C conversion FAILED")

if __name__ == "__main__":
    test_supply_merge()
