#!/usr/bin/env python3
"""
Smart Merge Example - How SUPPLY/REGULAR PDF processing will work
This demonstrates the intelligent subject-level merging system
"""

from datetime import datetime

def example_smart_merge_scenario():
    """
    Example showing how smart merge works with SUPPLY and REGULAR PDFs
    """
    
    print("🎯 SMART MERGE EXAMPLE - SUPPLY/REGULAR PDF Processing")
    print("=" * 60)
    
    # Example: Student ABC123, 2nd Year, Semester 3
    student_id = "ABC123"
    year = "2nd Year" 
    semester = "Semester 3"
    
    print(f"📚 Student: {student_id}")
    print(f"📅 Year: {year}, Semester: {semester}")
    print()
    
    # SCENARIO 1: Initial REGULAR PDF Upload
    print("🔹 SCENARIO 1: Upload REGULAR PDF (Initial)")
    print("-" * 40)
    
    regular_pdf_data = {
        "student_id": "ABC123",
        "student_name": "John Doe",
        "year": "2nd Year",
        "semester": "Semester 3",
        "examType": "regular",
        "uploadedAt": "2025-08-13T10:00:00",
        "subjects": [
            {
                "subject_code": "MATH201",
                "subject_name": "Mathematics III",
                "internal_marks": 18,
                "external_marks": 32,
                "total_marks": 50,
                "grade": "F",
                "result": "FAIL"
            },
            {
                "subject_code": "PHYS201", 
                "subject_name": "Physics III",
                "internal_marks": 20,
                "external_marks": 45,
                "total_marks": 65,
                "grade": "B",
                "result": "PASS"
            },
            {
                "subject_code": "CHEM201",
                "subject_name": "Chemistry III", 
                "internal_marks": 19,
                "external_marks": 41,
                "total_marks": 60,
                "grade": "B",
                "result": "PASS"
            }
        ]
    }
    
    print("✅ REGULAR PDF Results:")
    for subject in regular_pdf_data["subjects"]:
        status = "✅ PASS" if subject["result"] == "PASS" else "❌ FAIL"
        print(f"   {subject['subject_code']}: {subject['total_marks']}/100 - Grade {subject['grade']} {status}")
    
    print(f"\n💾 Action: CREATE new record in Firebase")
    print(f"📄 Document ID: ABC123_2nd_Year_Semester_3_regular")
    print()
    
    # SCENARIO 2: Upload SUPPLY PDF Later
    print("🔹 SCENARIO 2: Upload SUPPLY PDF (2 months later)")
    print("-" * 40)
    
    supply_pdf_data = {
        "student_id": "ABC123",
        "student_name": "John Doe", 
        "year": "2nd Year",
        "semester": "Semester 3",
        "examType": "supplementary",
        "uploadedAt": "2025-10-15T14:30:00",  # 2 months later
        "subjects": [
            {
                "subject_code": "MATH201",  # Re-appeared in supply
                "subject_name": "Mathematics III",
                "internal_marks": 18,
                "external_marks": 52,  # Better marks in supply
                "total_marks": 70,
                "grade": "B", 
                "result": "PASS"  # Now PASSED
            },
            {
                "subject_code": "ENG201",  # New subject not in regular
                "subject_name": "English III",
                "internal_marks": 17,
                "external_marks": 48,
                "total_marks": 65,
                "grade": "B",
                "result": "PASS"
            }
        ]
    }
    
    print("📋 SUPPLY PDF Results:")
    for subject in supply_pdf_data["subjects"]:
        status = "✅ PASS" if subject["result"] == "PASS" else "❌ FAIL" 
        print(f"   {subject['subject_code']}: {subject['total_marks']}/100 - Grade {subject['grade']} {status}")
    
    print()
    
    # SMART MERGE LOGIC
    print("🧠 SMART MERGE PROCESSING:")
    print("-" * 40)
    
    # Step 1: Find existing record
    print("1️⃣ Query Firebase for existing record...")
    print(f"   🔍 Looking for: student_id=ABC123, year=2nd Year, semester=Semester 3")
    print(f"   ✅ Found existing REGULAR record (uploaded: 2025-08-13)")
    print()
    
    # Step 2: Subject-level comparison
    print("2️⃣ Subject-level intelligent merging...")
    
    merge_actions = []
    
    # Check each subject in SUPPLY PDF
    for new_subject in supply_pdf_data["subjects"]:
        subject_code = new_subject["subject_code"]
        
        # Find if this subject exists in regular record
        existing_subject = None
        for reg_subject in regular_pdf_data["subjects"]:
            if reg_subject["subject_code"] == subject_code:
                existing_subject = reg_subject
                break
        
        if existing_subject:
            # Subject exists - check priority rules
            newer_upload = supply_pdf_data["uploadedAt"] > regular_pdf_data["uploadedAt"]
            supply_overwrites = supply_pdf_data["examType"] == "supplementary"
            
            if supply_overwrites and newer_upload:
                action = {
                    "type": "UPDATE",
                    "subject_code": subject_code,
                    "reason": "SUPPLY overwrites REGULAR (newer upload)",
                    "old_result": f"{existing_subject['result']} (Grade: {existing_subject['grade']})",
                    "new_result": f"{new_subject['result']} (Grade: {new_subject['grade']})"
                }
                merge_actions.append(action)
        else:
            # New subject not in existing record
            action = {
                "type": "ADD",
                "subject_code": subject_code,
                "reason": "New subject not in existing record",
                "new_result": f"{new_subject['result']} (Grade: {new_subject['grade']})"
            }
            merge_actions.append(action)
    
    # Display merge actions
    for action in merge_actions:
        if action["type"] == "UPDATE":
            print(f"   🔄 UPDATE {action['subject_code']}: {action['old_result']} → {action['new_result']}")
            print(f"      💡 Reason: {action['reason']}")
        elif action["type"] == "ADD":
            print(f"   ➕ ADD {action['subject_code']}: {action['new_result']}")
            print(f"      💡 Reason: {action['reason']}")
    
    print()
    
    # Step 3: Final merged record
    print("3️⃣ Final merged record after SUPPLY upload...")
    
    final_merged_record = {
        "student_id": "ABC123",
        "student_name": "John Doe",
        "year": "2nd Year", 
        "semester": "Semester 3",
        "examType": "mixed",  # Contains both regular and supply
        "lastUpdatedAt": "2025-10-15T14:30:00",  # Latest upload time
        "subjects": [
            # MATH201 - UPDATED from SUPPLY (was FAIL, now PASS)
            {
                "subject_code": "MATH201",
                "subject_name": "Mathematics III",
                "internal_marks": 18,
                "external_marks": 52,  # Updated from supply
                "total_marks": 70,     # Updated from supply
                "grade": "B",          # Updated from supply  
                "result": "PASS",      # Updated from supply
                "source": "supplementary",
                "updated_at": "2025-10-15T14:30:00"
            },
            # PHYS201 - KEPT from REGULAR (no supply data)
            {
                "subject_code": "PHYS201",
                "subject_name": "Physics III", 
                "internal_marks": 20,
                "external_marks": 45,
                "total_marks": 65,
                "grade": "B",
                "result": "PASS",
                "source": "regular",
                "updated_at": "2025-08-13T10:00:00"
            },
            # CHEM201 - KEPT from REGULAR (no supply data)
            {
                "subject_code": "CHEM201",
                "subject_name": "Chemistry III",
                "internal_marks": 19, 
                "external_marks": 41,
                "total_marks": 60,
                "grade": "B",
                "result": "PASS",
                "source": "regular", 
                "updated_at": "2025-08-13T10:00:00"
            },
            # ENG201 - ADDED from SUPPLY (new subject)
            {
                "subject_code": "ENG201",
                "subject_name": "English III",
                "internal_marks": 17,
                "external_marks": 48, 
                "total_marks": 65,
                "grade": "B",
                "result": "PASS",
                "source": "supplementary",
                "updated_at": "2025-10-15T14:30:00"
            }
        ]
    }
    
    print("📊 FINAL MERGED RECORD:")
    for subject in final_merged_record["subjects"]:
        status = "✅ PASS" if subject["result"] == "PASS" else "❌ FAIL"
        source_icon = "🔄" if subject["source"] == "supplementary" else "📝"
        print(f"   {source_icon} {subject['subject_code']}: {subject['total_marks']}/100 - Grade {subject['grade']} {status} ({subject['source']})")
    
    print()
    
    # Statistics
    print("📈 MERGE STATISTICS:")
    print("-" * 40)
    total_subjects = len(final_merged_record["subjects"])
    updated_subjects = len([s for s in final_merged_record["subjects"] if s["source"] == "supplementary" and s["subject_code"] == "MATH201"])
    added_subjects = len([s for s in final_merged_record["subjects"] if s["source"] == "supplementary" and s["subject_code"] == "ENG201"])
    kept_subjects = len([s for s in final_merged_record["subjects"] if s["source"] == "regular"])
    
    print(f"📊 Total subjects in final record: {total_subjects}")
    print(f"🔄 Subjects updated from SUPPLY: {updated_subjects}")
    print(f"➕ Subjects added from SUPPLY: {added_subjects}")
    print(f"📝 Subjects kept from REGULAR: {kept_subjects}")
    print()
    
    # Benefits
    print("🎯 BENEFITS OF SMART MERGE:")
    print("-" * 40)
    print("✅ No data loss - All subjects preserved")
    print("✅ SUPPLY results overwrite REGULAR failures")
    print("✅ Latest uploads take priority") 
    print("✅ Complete academic history maintained")
    print("✅ Subject-level precision - only update what changed")
    print("✅ Detailed audit trail with timestamps and sources")

def example_conflict_scenarios():
    """
    Examples of different conflict resolution scenarios
    """
    
    print("\n" + "=" * 60)
    print("🔀 CONFLICT RESOLUTION SCENARIOS")
    print("=" * 60)
    
    scenarios = [
        {
            "title": "SUPPLY overwrites REGULAR (Your Rule)",
            "regular": {"result": "FAIL", "grade": "F", "marks": 45},
            "supply": {"result": "PASS", "grade": "B", "marks": 65},
            "action": "UPDATE with SUPPLY data",
            "reason": "SUPPLY always overwrites REGULAR"
        },
        {
            "title": "Newer upload wins (Your Rule)",
            "existing": {"uploaded": "2025-08-13", "marks": 60},
            "new": {"uploaded": "2025-10-15", "marks": 55},
            "action": "UPDATE with newer data", 
            "reason": "Newer upload takes priority"
        },
        {
            "title": "New subject addition",
            "existing": "Subject doesn't exist",
            "new": {"result": "PASS", "grade": "A", "marks": 85},
            "action": "ADD new subject",
            "reason": "New subject not in existing record"
        },
        {
            "title": "Mixed exam types",
            "regular_subjects": ["MATH201", "PHYS201", "CHEM201"],
            "supply_subjects": ["MATH201", "ENG201"],
            "final_record": "4 subjects total (3 from regular, 1 updated, 1 added)",
            "exam_type": "mixed"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}️⃣ {scenario['title']}")
        print("-" * 30)
        for key, value in scenario.items():
            if key != "title":
                print(f"   {key}: {value}")

if __name__ == "__main__":
    example_smart_merge_scenario()
    example_conflict_scenarios()
    
    print("\n" + "=" * 60)
    print("💡 IMPLEMENTATION READY")
    print("=" * 60)
    print("This example shows exactly how the smart merge will work.")
    print("Ready to implement this logic in batch_pdf_processor.py!")
    print("Say 'proceed' to start the implementation.")
