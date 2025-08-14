#!/usr/bin/env python3
"""
Supply Processing Demo - Complete Example
Shows exactly how supply result processing works with realistic data
"""

def demo_complete_supply_processing():
    """Complete demonstration of supply processing workflow"""
    print("🎯 COMPLETE SUPPLY PROCESSING DEMONSTRATION")
    print("=" * 60)
    
    # Step 1: Show existing regular results in Firebase (simulation)
    print("\n📋 STEP 1: EXISTING REGULAR RESULTS IN FIREBASE")
    print("-" * 50)
    
    existing_students = {
        "20R01A0501": {
            "student_id": "20R01A0501",
            "name": "John Doe",
            "semester": "Semester 3",
            "year": "2nd Year",
            "exam_type": "REGULAR",
            "subjects": [
                {
                    "subject_code": "CS301",
                    "subject_name": "Data Structures",
                    "grade": "F",
                    "result": "Fail",
                    "credits": 4,
                    "attempts": 1,
                    "exam_type": "REGULAR"
                },
                {
                    "subject_code": "MA301",
                    "subject_name": "Mathematics III",
                    "grade": "D",
                    "result": "Pass",
                    "credits": 4,
                    "attempts": 1,
                    "exam_type": "REGULAR"
                },
                {
                    "subject_code": "PH301",
                    "subject_name": "Physics III",
                    "grade": "C",
                    "result": "Pass",
                    "credits": 3,
                    "attempts": 1,
                    "exam_type": "REGULAR"
                }
            ]
        },
        "20R01A0502": {
            "student_id": "20R01A0502",
            "name": "Jane Smith",
            "semester": "Semester 3",
            "year": "2nd Year",
            "exam_type": "REGULAR",
            "subjects": [
                {
                    "subject_code": "CS301",
                    "subject_name": "Data Structures",
                    "grade": "B",
                    "result": "Pass",
                    "credits": 4,
                    "attempts": 1,
                    "exam_type": "REGULAR"
                },
                {
                    "subject_code": "MA301",
                    "subject_name": "Mathematics III",
                    "grade": "F",
                    "result": "Fail",
                    "credits": 4,
                    "attempts": 1,
                    "exam_type": "REGULAR"
                }
            ]
        }
    }
    
    for student_id, student in existing_students.items():
        print(f"\n👤 Student: {student_id} ({student['name']})")
        print(f"   📚 Year: {student['year']}, Semester: {student['semester']}")
        print(f"   📊 Regular Results:")
        for subject in student['subjects']:
            print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']}) - Attempt #{subject['attempts']}")
    
    # Step 2: Show supply PDF results (what gets parsed)
    print("\n\n📄 STEP 2: SUPPLY PDF RESULTS (Parsed from PDF)")
    print("-" * 50)
    
    supply_results = [
        {
            "student_id": "20R01A0501",
            "name": "John Doe",
            "semester": "Semester 3",
            "year": "2nd Year",
            "exam_type": "SUPPLY",
            "subjects": [
                {
                    "subject_code": "CS301",
                    "subject_name": "Data Structures",
                    "grade": "C",  # F → C (IMPROVEMENT!)
                    "result": "Pass",
                    "credits": 4,
                    "exam_type": "SUPPLY"
                },
                {
                    "subject_code": "MA301",
                    "subject_name": "Mathematics III", 
                    "grade": "B",  # D → B (IMPROVEMENT!)
                    "result": "Pass",
                    "credits": 4,
                    "exam_type": "SUPPLY"
                },
                {
                    "subject_code": "PH301",
                    "subject_name": "Physics III",
                    "grade": "D",  # C → D (DOWNGRADE - should NOT overwrite)
                    "result": "Pass",
                    "credits": 3,
                    "exam_type": "SUPPLY"
                },
                {
                    "subject_code": "EN301",
                    "subject_name": "English III",
                    "grade": "B",  # NEW SUBJECT
                    "result": "Pass",
                    "credits": 2,
                    "exam_type": "SUPPLY"
                }
            ]
        },
        {
            "student_id": "20R01A0502",
            "name": "Jane Smith",
            "semester": "Semester 3",
            "year": "2nd Year", 
            "exam_type": "SUPPLY",
            "subjects": [
                {
                    "subject_code": "MA301",
                    "subject_name": "Mathematics III",
                    "grade": "C",  # F → C (FAILED to PASSED!)
                    "result": "Pass",
                    "credits": 4,
                    "exam_type": "SUPPLY"
                },
                {
                    "subject_code": "CS301",
                    "subject_name": "Data Structures",
                    "grade": "A",  # B → A (IMPROVEMENT!)
                    "result": "Pass",
                    "credits": 4,
                    "exam_type": "SUPPLY"
                }
            ]
        }
    ]
    
    print("📋 Supply Results to Process:")
    for student in supply_results:
        print(f"\n👤 Student: {student['student_id']} ({student['name']})")
        print(f"   📊 Supply Results:")
        for subject in student['subjects']:
            print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']})")
    
    # Step 3: Smart merge processing simulation
    print("\n\n🔄 STEP 3: SMART MERGE PROCESSING")
    print("-" * 50)
    
    from batch_pdf_processor import smart_supply_merge_by_subject, is_grade_improvement
    
    final_results = {}
    supply_timestamp = "2025-08-13T15:30:00Z"
    
    for supply_student in supply_results:
        student_id = supply_student['student_id']
        print(f"\n🔍 Processing {student_id}...")
        
        # Find existing student
        existing_student = existing_students.get(student_id)
        if not existing_student:
            print(f"   ❌ No existing record found for {student_id}")
            continue
            
        print(f"   ✅ Found existing record for {student_id}")
        
        # Convert subjects to dictionary format for merge function
        existing_subjects = {}
        for subject in existing_student['subjects']:
            existing_subjects[subject['subject_code']] = subject
            
        supply_subjects = {}
        for subject in supply_student['subjects']:
            supply_subjects[subject['subject_code']] = subject
        
        # Perform smart merge
        merged_subjects, merge_report = smart_supply_merge_by_subject(
            existing_subjects, 
            supply_subjects, 
            supply_timestamp
        )
        
        print(f"   📊 Merge Results:")
        print(f"      Subjects Overwritten: {merge_report['subjects_overwritten']}")
        print(f"      Subjects Added: {merge_report['subjects_added']}")
        print(f"      Attempts Tracked: {merge_report['attempts_tracked']}")
        
        print(f"   📈 Detailed Actions:")
        for action in merge_report['actions']:
            print(f"      {action}")
        
        # Store final result
        final_student = existing_student.copy()
        final_student['subjects'] = list(merged_subjects.values())
        final_student['last_updated'] = supply_timestamp
        final_student['has_supply_attempts'] = True
        final_results[student_id] = final_student
    
    # Step 4: Show final results
    print("\n\n📊 STEP 4: FINAL RESULTS AFTER SUPPLY PROCESSING")
    print("-" * 50)
    
    for student_id, student in final_results.items():
        print(f"\n👤 Student: {student_id} ({student['name']})")
        print(f"   📚 Final Academic Record:")
        
        for subject in student['subjects']:
            attempts = subject.get('attempts', 1)
            exam_type = subject.get('exam_type', 'REGULAR')
            improved = subject.get('improved_from_regular', False) or subject.get('improved_grade', False)
            new_subject = subject.get('new_subject_from_supply', False)
            
            status_icon = ""
            if improved:
                status_icon = " 🎉 IMPROVED"
            elif new_subject:
                status_icon = " ➕ NEW"
            elif attempts > 1:
                status_icon = " 📝 TRACKED"
            
            print(f"      {subject['subject_code']}: {subject['grade']} ({subject['result']}) - Attempt #{attempts} [{exam_type}]{status_icon}")
            
            # Show attempt history if available
            if 'attempt_history' in subject and len(subject['attempt_history']) > 1:
                history_text = " → ".join([f"Attempt {h['attempt']}: {h['grade']}" for h in subject['attempt_history']])
                print(f"         📈 History: {history_text}")
    
    # Step 5: Show Firebase document structure
    print("\n\n💾 STEP 5: FIREBASE DOCUMENT STRUCTURE")
    print("-" * 50)
    
    print("📄 Example final Firebase document for 20R01A0501:")
    print("""
{
  "student_id": "20R01A0501",
  "name": "John Doe",
  "year": "2nd Year",
  "semester": "Semester 3",
  "exam_type": "MIXED",
  "has_supply_attempts": true,
  "last_updated": "2025-08-13T15:30:00Z",
  "subjects": {
    "CS301": {
      "subject_code": "CS301",
      "subject_name": "Data Structures", 
      "grade": "C",
      "result": "Pass",
      "credits": 4,
      "attempts": 2,
      "exam_type": "SUPPLY",
      "original_grade": "F",
      "improved_from_regular": true,
      "improvement_date": "2025-08-13T15:30:00Z",
      "attempt_history": [
        {
          "attempt": 1,
          "exam_type": "REGULAR",
          "grade": "F",
          "result": "Fail",
          "timestamp": "2025-06-15T10:00:00Z"
        },
        {
          "attempt": 2,
          "exam_type": "SUPPLY",
          "grade": "C", 
          "result": "Pass",
          "timestamp": "2025-08-13T15:30:00Z",
          "improvement": true,
          "previous_grade": "F"
        }
      ]
    },
    "MA301": {
      "subject_code": "MA301",
      "subject_name": "Mathematics III",
      "grade": "B",
      "result": "Pass", 
      "credits": 4,
      "attempts": 2,
      "exam_type": "SUPPLY",
      "original_grade": "D",
      "improved_grade": true,
      "improvement_date": "2025-08-13T15:30:00Z",
      "attempt_history": [
        {
          "attempt": 1,
          "exam_type": "REGULAR",
          "grade": "D",
          "result": "Pass",
          "timestamp": "2025-06-15T10:00:00Z"
        },
        {
          "attempt": 2,
          "exam_type": "SUPPLY", 
          "grade": "B",
          "result": "Pass",
          "timestamp": "2025-08-13T15:30:00Z",
          "improvement": true,
          "previous_grade": "D"
        }
      ]
    },
    "PH301": {
      "subject_code": "PH301",
      "subject_name": "Physics III",
      "grade": "C",  // PRESERVED - supply grade D was worse
      "result": "Pass",
      "credits": 3,
      "attempts": 2,  // BUT attempt count still tracked
      "exam_type": "REGULAR",  // Original exam type preserved
      "last_supply_attempt": "2025-08-13T15:30:00Z",
      "attempt_history": [
        {
          "attempt": 1,
          "exam_type": "REGULAR",
          "grade": "C",
          "result": "Pass",
          "timestamp": "2025-06-15T10:00:00Z"
        },
        {
          "attempt": 2,
          "exam_type": "SUPPLY",
          "grade": "D",
          "result": "Pass", 
          "timestamp": "2025-08-13T15:30:00Z",
          "improvement": false,
          "note": "Supply attempt recorded, no grade improvement"
        }
      ]
    },
    "EN301": {
      "subject_code": "EN301",
      "subject_name": "English III",
      "grade": "B",
      "result": "Pass",
      "credits": 2,
      "attempts": 1,
      "exam_type": "SUPPLY",
      "new_subject_from_supply": true,
      "added_date": "2025-08-13T15:30:00Z",
      "attempt_history": [
        {
          "attempt": 1,
          "exam_type": "SUPPLY",
          "grade": "B",
          "result": "Pass",
          "timestamp": "2025-08-13T15:30:00Z",
          "note": "New subject added from supply"
        }
      ]
    }
  }
}
    """)
    
    # Step 6: Show API response
    print("\n\n🌐 STEP 6: API RESPONSE")
    print("-" * 50)
    
    print("📡 Response from /upload-supply-pdf endpoint:")
    print("""
{
  "message": "Successfully processed supply results with smart merge.",
  "result": {
    "status": "success",
    "stats": {
      "total_processed": 2,
      "students_found_in_firebase": 2,
      "students_not_found": 0,
      "students_updated": 2,
      "subjects_overwritten": 4,
      "subjects_added": 1,
      "total_attempts_tracked": 5
    },
    "processing_time": 2.34,
    "improvement_report": {
      "total_improvements": 4,
      "students_with_improvements": 2
    }
  },
  "stats": {
    "total_processed": 2,
    "students_updated": 2,
    "subjects_overwritten": 4
  },
  "improvements": {
    "grade_improvements": [
      {
        "student_id": "20R01A0501",
        "subject_code": "CS301", 
        "from_grade": "F",
        "to_grade": "C",
        "attempt_number": 2
      },
      {
        "student_id": "20R01A0501",
        "subject_code": "MA301",
        "from_grade": "D", 
        "to_grade": "B",
        "attempt_number": 2
      },
      {
        "student_id": "20R01A0502",
        "subject_code": "MA301",
        "from_grade": "F",
        "to_grade": "C", 
        "attempt_number": 2
      },
      {
        "student_id": "20R01A0502",
        "subject_code": "CS301",
        "from_grade": "B",
        "to_grade": "A",
        "attempt_number": 2
      }
    ]
  },
  "firebase": {
    "enabled": true,
    "processing_time": 2.34,
    "storage_url": "https://storage.googleapis.com/plant-ec218.firebasestorage.app/supply_jntuk_20250813_153000_supply_results.pdf"
  }
}
    """)

def demo_grade_comparison_logic():
    """Show how grade comparison works"""
    print("\n\n🧪 GRADE COMPARISON LOGIC DEMONSTRATION")
    print("=" * 60)
    
    from batch_pdf_processor import is_grade_improvement
    
    print("📊 Grade Hierarchy: O > A+ > A > B+ > B > C > D > F")
    print("\n🔍 Grade Comparison Examples:")
    
    test_cases = [
        ("F", "D", "Failed student now passes"),
        ("F", "C", "Failed student gets good grade"), 
        ("F", "B", "Failed student gets very good grade"),
        ("D", "C", "Pass grade improves"),
        ("C", "B", "Good grade becomes better"),
        ("B", "A", "Very good grade becomes excellent"),
        ("C", "C", "Same grade (no change)"),
        ("B", "C", "Grade decreased (no overwrite)"),
        ("A", "B", "Excellent to good (no overwrite)"),
        ("C", "D", "Good to pass (no overwrite)")
    ]
    
    for old_grade, new_grade, description in test_cases:
        result = is_grade_improvement(old_grade, new_grade)
        status = "✅ OVERWRITE" if result else "❌ PRESERVE"
        print(f"   {old_grade} → {new_grade}: {status} ({description})")

def demo_attempt_counting():
    """Show how attempt counting works"""
    print("\n\n🔢 ATTEMPT COUNTING DEMONSTRATION")
    print("=" * 60)
    
    print("📋 Student Journey Example:")
    print("👤 Student: 20R01A0501")
    print("📚 Subject: CS301 (Data Structures)")
    print()
    
    attempts = [
        {
            "attempt": 1,
            "exam_type": "REGULAR",
            "date": "June 2025",
            "grade": "F",
            "result": "Fail",
            "action": "Initial regular exam attempt"
        },
        {
            "attempt": 2, 
            "exam_type": "SUPPLY",
            "date": "August 2025",
            "grade": "C",
            "result": "Pass", 
            "action": "Supply exam - OVERWRITE (F→C, Fail→Pass)"
        },
        {
            "attempt": 3,
            "exam_type": "SUPPLY",
            "date": "December 2025", 
            "grade": "B",
            "result": "Pass",
            "action": "Another supply attempt - OVERWRITE (C→B, improvement)"
        },
        {
            "attempt": 4,
            "exam_type": "SUPPLY",
            "date": "June 2026",
            "grade": "B",
            "result": "Pass", 
            "action": "Supply attempt - TRACK ONLY (B→B, no improvement)"
        }
    ]
    
    current_grade = "F"
    current_result = "Fail"
    
    for attempt in attempts:
        print(f"🔄 Attempt #{attempt['attempt']} ({attempt['exam_type']}) - {attempt['date']}")
        print(f"   📊 Grade: {current_grade} → {attempt['grade']}")
        print(f"   📋 Result: {current_result} → {attempt['result']}")
        print(f"   ⚡ Action: {attempt['action']}")
        
        # Update current if this is an improvement
        if attempt['action'].startswith("Supply exam - OVERWRITE") or attempt['action'].startswith("Another supply attempt - OVERWRITE"):
            current_grade = attempt['grade']
            current_result = attempt['result']
        
        print(f"   💾 Firebase Record: Grade={current_grade}, Attempts={attempt['attempt']}")
        print()
    
    print(f"🎯 Final Result: Grade {current_grade} with {len(attempts)} total attempts")

if __name__ == "__main__":
    demo_complete_supply_processing()
    demo_grade_comparison_logic()
    demo_attempt_counting()
