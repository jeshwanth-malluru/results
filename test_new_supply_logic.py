#!/usr/bin/env python3
"""
Test New Supply Processing Logic
Demonstrates the updated supply result processing with register number detection
"""

def test_supply_processing_logic():
    """Test the new supply processing logic"""
    print("🧪 Testing New Supply Processing Logic")
    print("=" * 50)
    
    # Test the smart supply merge function
    from batch_pdf_processor import smart_supply_merge_by_subject, is_grade_improvement
    
    # Mock existing regular results (student failed some subjects)
    existing_subjects = {
        "CS101": {
            "subject_code": "CS101",
            "subject_name": "Programming Fundamentals", 
            "grade": "F",
            "result": "Fail",
            "credits": 4,
            "attempts": 1,
            "exam_type": "REGULAR"
        },
        "MA101": {
            "subject_code": "MA101",
            "subject_name": "Mathematics I",
            "grade": "D", 
            "result": "Pass",
            "credits": 4,
            "attempts": 1,
            "exam_type": "REGULAR"
        },
        "PH101": {
            "subject_code": "PH101",
            "subject_name": "Physics",
            "grade": "C",
            "result": "Pass", 
            "credits": 3,
            "attempts": 1,
            "exam_type": "REGULAR"
        }
    }
    
    # Mock supply results (student attempted to improve)
    supply_subjects = {
        "CS101": {
            "subject_code": "CS101", 
            "subject_name": "Programming Fundamentals",
            "grade": "C",  # F → C (IMPROVEMENT - should overwrite)
            "result": "Pass",
            "credits": 4,
            "exam_type": "SUPPLY"
        },
        "MA101": {
            "subject_code": "MA101",
            "subject_name": "Mathematics I", 
            "grade": "B",  # D → B (IMPROVEMENT - should overwrite)
            "result": "Pass",
            "credits": 4,
            "exam_type": "SUPPLY"
        },
        "PH101": {
            "subject_code": "PH101",
            "subject_name": "Physics",
            "grade": "D",  # C → D (DOWNGRADE - should NOT overwrite)
            "result": "Pass",
            "credits": 3,
            "exam_type": "SUPPLY"
        },
        "EN101": {
            "subject_code": "EN101",
            "subject_name": "English",
            "grade": "B",  # NEW SUBJECT - should add
            "result": "Pass", 
            "credits": 2,
            "exam_type": "SUPPLY"
        }
    }
    
    print("📋 BEFORE SUPPLY PROCESSING:")
    print("Regular Results:")
    for code, subject in existing_subjects.items():
        print(f"  {code}: {subject['grade']} ({subject['result']}) - Attempt #{subject['attempts']}")
    
    print("\n📋 SUPPLY RESULTS:")
    for code, subject in supply_subjects.items():
        print(f"  {code}: {subject['grade']} ({subject['result']})")
    
    # Process supply merge
    merged_subjects, merge_report = smart_supply_merge_by_subject(
        existing_subjects, 
        supply_subjects, 
        "2025-08-13T15:30:00Z"
    )
    
    print(f"\n🔄 SUPPLY MERGE RESULTS:")
    print(f"  Subjects Overwritten: {merge_report['subjects_overwritten']}")
    print(f"  Subjects Added: {merge_report['subjects_added']}")
    print(f"  Attempts Tracked: {merge_report['attempts_tracked']}")
    
    print(f"\n📈 DETAILED ACTIONS:")
    for action in merge_report['actions']:
        print(f"  {action}")
    
    print(f"\n📊 FINAL RESULTS AFTER SUPPLY PROCESSING:")
    for code, subject in merged_subjects.items():
        attempts = subject.get('attempts', 1)
        exam_type = subject.get('exam_type', 'REGULAR')
        improved = subject.get('improved_from_regular', False) or subject.get('improved_grade', False)
        improvement_indicator = " 🎉" if improved else ""
        print(f"  {code}: {subject['grade']} ({subject['result']}) - Attempt #{attempts} [{exam_type}]{improvement_indicator}")
    
    print(f"\n✅ Expected Results:")
    print(f"  ✅ CS101: Should be overwritten F→C (failed in regular, passed in supply)")
    print(f"  ✅ MA101: Should be overwritten D→B (grade improvement)")
    print(f"  ❌ PH101: Should NOT be overwritten C→D (grade downgrade)")
    print(f"  ➕ EN101: Should be added as new subject")
    
    # Verify specific cases
    cs101 = merged_subjects.get('CS101', {})
    ma101 = merged_subjects.get('MA101', {})
    ph101 = merged_subjects.get('PH101', {})
    en101 = merged_subjects.get('EN101', {})
    
    print(f"\n🧪 VERIFICATION:")
    print(f"  CS101 overwritten (F→C): {'✅' if cs101.get('grade') == 'C' and cs101.get('attempts', 0) == 2 else '❌'}")
    print(f"  MA101 improved (D→B): {'✅' if ma101.get('grade') == 'B' and ma101.get('attempts', 0) == 2 else '❌'}")
    print(f"  PH101 preserved (C): {'✅' if ph101.get('grade') == 'C' and ph101.get('attempts', 0) == 2 else '❌'}")
    print(f"  EN101 added: {'✅' if en101.get('grade') == 'B' and en101.get('attempts', 0) == 1 else '❌'}")

def test_grade_improvement_cases():
    """Test specific grade improvement detection"""
    print(f"\n🧪 Testing Grade Improvement Detection")
    print("-" * 40)
    
    from batch_pdf_processor import is_grade_improvement
    
    test_cases = [
        # Format: (existing_grade, supply_grade, expected_improvement)
        ('F', 'D', True, "Failed to Pass"),
        ('F', 'C', True, "Failed to Better Pass"), 
        ('F', 'B', True, "Failed to Good Pass"),
        ('D', 'C', True, "Pass to Better Pass"),
        ('D', 'B', True, "Pass to Good Pass"),
        ('C', 'B', True, "Good to Better"),
        ('B', 'A', True, "Better to Excellent"),
        ('C', 'C', False, "Same Grade"), 
        ('B', 'C', False, "Downgrade"),
        ('A', 'B', False, "Downgrade from Excellent"),
        ('F', 'F', False, "Still Failed"),
    ]
    
    for existing, supply, expected, description in test_cases:
        result = is_grade_improvement(existing, supply)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {existing}→{supply}: {result} ({description})")

def demonstrate_api_usage():
    """Demonstrate how to use the new supply processing API"""
    print(f"\n📚 API USAGE EXAMPLE")
    print("=" * 30)
    
    print("""
# Example: Process a supply PDF file
from batch_pdf_processor import process_supply_pdf_with_smart_merge

# Upload and process supply PDF
result = process_supply_pdf_with_smart_merge(
    pdf_path="/path/to/supply_results.pdf",
    format_type="jntuk"  # or "autonomous"
)

# Check results
if result['status'] == 'success':
    stats = result['stats']
    print(f"Students processed: {stats['total_processed']}")
    print(f"Students updated: {stats['students_updated']}")
    print(f"Subjects overwritten: {stats['subjects_overwritten']}")
    print(f"Grade improvements: {stats['subjects_overwritten']}")
else:
    print(f"Error: {result['message']}")

# The function will:
# 1. Parse the supply PDF
# 2. For each student, find existing record in Firebase by register number
# 3. Compare each subject by subject code
# 4. Overwrite grades where supply result is better
# 5. Track attempt counts (Regular=1, First Supply=2, etc.)
# 6. Log all improvements and changes
    """)

if __name__ == "__main__":
    test_supply_processing_logic()
    test_grade_improvement_cases()
    demonstrate_api_usage()
