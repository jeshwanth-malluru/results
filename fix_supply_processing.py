#!/usr/bin/env python3
"""
Fixed 2-1 Supply PDF Processing with Proper Subject Code Matching
This will fix the Advanced Data Structures issue by using subject codes for matching
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def grade_hierarchy():
    """Define grade hierarchy for comparison"""
    return ['F', 'D', 'C', 'B', 'B+', 'A', 'A+', 'O']

def is_grade_better(current_grade, new_grade):
    """Check if new grade is better than current grade"""
    hierarchy = grade_hierarchy()
    try:
        current_index = hierarchy.index(current_grade)
        new_index = hierarchy.index(new_grade)
        return new_index > current_index
    except ValueError:
        return False

def normalize_subject_code(code):
    """Normalize subject code by removing extra spaces and converting to uppercase"""
    if not code:
        return ""
    return str(code).strip().upper()

def remove_duplicate_subjects(subjects):
    """Remove duplicate subjects based on subject code, keeping the best grade"""
    if not subjects:
        return []
    
    # Group by normalized subject code
    subject_groups = {}
    for subject in subjects:
        code = normalize_subject_code(subject.get('code', ''))
        if code:
            if code not in subject_groups:
                subject_groups[code] = []
            subject_groups[code].append(subject)
    
    # For each code, keep the subject with the best grade
    deduplicated_subjects = []
    for code, subject_list in subject_groups.items():
        if len(subject_list) == 1:
            deduplicated_subjects.append(subject_list[0])
        else:
            # Find the subject with the best grade
            best_subject = subject_list[0]
            for subject in subject_list[1:]:
                current_grade = best_subject.get('grade', 'F')
                new_grade = subject.get('grade', 'F')
                if is_grade_better(current_grade, new_grade):
                    best_subject = subject
            deduplicated_subjects.append(best_subject)
    
    return deduplicated_subjects

def fixed_supply_processing():
    """Fixed processing of the 2-1 supply PDF with proper subject code matching"""
    
    print("🔧 FIXED 2-1 SUPPLY PDF PROCESSING")
    print("=" * 60)
    
    pdf_path = r"c:\temp\supply_21.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    try:
        # Import the required modules
        print("📦 Loading modules...")
        from parser.parser_jntuk import parse_jntuk_pdf
        print("  ✓ Parser loaded successfully")
        
        # Step 1: Parse the supply PDF
        print(f"\n📄 Parsing supply PDF: {pdf_path}")
        supply_results = parse_jntuk_pdf(pdf_path)
        
        if not supply_results:
            print("❌ No results found in PDF")
            return
        
        print(f"  ✓ Found {len(supply_results)} students in supply PDF")
        
        # Step 2: Find the latest regular results file
        print(f"\n🔍 Finding latest regular results...")
        data_dir = Path("data")
        regular_files = []
        
        for json_file in data_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    if metadata.get('exam_type') == 'regular':
                        regular_files.append((json_file, data))
            except Exception as e:
                print(f"  ⚠️  Could not read {json_file}: {e}")
        
        if not regular_files:
            print("❌ No regular results found to merge with")
            return
        
        # Use the most recent regular file
        latest_file, regular_data = max(regular_files, key=lambda x: x[0].stat().st_mtime)
        regular_students = regular_data.get('students', [])
        
        print(f"  ✓ Using: {latest_file.name}")
        print(f"  ✓ Regular students: {len(regular_students)}")
        
        # Step 3: Process merging with fixed logic
        print(f"\n🔄 Processing supply merge with fixed logic...")
        
        # Create lookup for regular students
        regular_lookup = {}
        for student in regular_students:
            htno = student.get('student_id')
            if htno:
                # Remove duplicates from regular subjects
                regular_subjects = remove_duplicate_subjects(student.get('subjectGrades', []))
                student_copy = student.copy()
                student_copy['subjectGrades'] = regular_subjects
                regular_lookup[htno] = student_copy
        
        improvements = {
            'students_processed': 0,
            'students_found': 0,
            'students_updated': 0,
            'grades_improved': 0,
            'f_grade_improvements': 0,
            'new_subjects_added': 0,
            'duplicates_removed': 0,
            'details': []
        }
        
        updated_students = []
        
        # Process each supply student
        for supply_student in supply_results:
            supply_htno = supply_student.get('student_id')
            improvements['students_processed'] += 1
            
            if not supply_htno:
                continue
            
            # Remove duplicates from supply subjects
            original_supply_subjects = supply_student.get('subjectGrades', [])
            supply_subjects = remove_duplicate_subjects(original_supply_subjects)
            
            if len(original_supply_subjects) > len(supply_subjects):
                improvements['duplicates_removed'] += len(original_supply_subjects) - len(supply_subjects)
            
            # Find matching regular student
            regular_student = regular_lookup.get(supply_htno)
            
            if not regular_student:
                continue
                
            improvements['students_found'] += 1
            
            # Get subjects
            regular_subjects = regular_student.get('subjectGrades', [])
            
            if not supply_subjects:
                continue
            
            # Create lookup for regular subjects by normalized code
            regular_subject_lookup = {}
            for subject in regular_subjects:
                code = normalize_subject_code(subject.get('code', ''))
                if code:
                    regular_subject_lookup[code] = subject
            
            # Track changes for this student
            student_changes = []
            updated_subject_list = []
            has_improvements = False
            
            # Start with all regular subjects
            for regular_subject in regular_subjects:
                updated_subject_list.append(regular_subject.copy())
            
            # Process each supply subject
            for supply_subject in supply_subjects:
                supply_code = normalize_subject_code(supply_subject.get('code', ''))
                supply_grade = supply_subject.get('grade', 'F')
                supply_result = supply_subject.get('result', 'Fail')
                
                if not supply_code:
                    continue
                
                # Find matching regular subject by normalized code
                regular_subject = regular_subject_lookup.get(supply_code)
                
                if regular_subject:
                    # Update existing subject
                    regular_grade = regular_subject.get('grade', 'F')
                    regular_result = regular_subject.get('result', 'Fail')
                    
                    # Check if we should update
                    should_update = False
                    update_reason = ""
                    
                    # Case 1: Student failed in regular but passed in supply
                    regular_failed = regular_grade == 'F' or regular_result.lower() in ['fail', 'f']
                    supply_passed = supply_grade != 'F' and supply_result.lower() in ['pass', 'p']
                    
                    if regular_failed and supply_passed:
                        should_update = True
                        update_reason = "F→Pass"
                        improvements['f_grade_improvements'] += 1
                    
                    # Case 2: Grade improved
                    elif is_grade_better(regular_grade, supply_grade):
                        should_update = True
                        update_reason = "Grade improved"
                    
                    if should_update:
                        # Update the subject in the list
                        for i, subj in enumerate(updated_subject_list):
                            subj_code = normalize_subject_code(subj.get('code', ''))
                            if subj_code == supply_code:
                                # Update with supply data but preserve some regular info
                                updated_subject = supply_subject.copy()
                                updated_subject['attempts'] = 2
                                updated_subject['previousGrade'] = regular_grade
                                updated_subject['previousResult'] = regular_result
                                updated_subject['improvement'] = f"{regular_grade}→{supply_grade}"
                                updated_subject['supplyImproved'] = True
                                updated_subject_list[i] = updated_subject
                                break
                        
                        student_changes.append({
                            'subject_code': supply_code,
                            'subject_name': supply_subject.get('subject', regular_subject.get('subject', 'Unknown')),
                            'regular_grade': regular_grade,
                            'supply_grade': supply_grade,
                            'improvement': f"{regular_grade}→{supply_grade}",
                            'reason': update_reason
                        })
                        
                        improvements['grades_improved'] += 1
                        has_improvements = True
                        
                        print(f"  🔧 FIXED: {supply_htno} - {supply_code}: {regular_grade}→{supply_grade}")
                
                else:
                    # Add new subject
                    new_subject = supply_subject.copy()
                    new_subject['attempts'] = 1
                    new_subject['isNewFromSupply'] = True
                    updated_subject_list.append(new_subject)
                    improvements['new_subjects_added'] += 1
                    has_improvements = True
                    
                    student_changes.append({
                        'subject_code': supply_code,
                        'subject_name': supply_subject.get('subject', 'Unknown'),
                        'regular_grade': 'N/A',
                        'supply_grade': supply_grade,
                        'improvement': f"New→{supply_grade}",
                        'reason': "New subject"
                    })
            
            if has_improvements:
                improvements['students_updated'] += 1
                
                # Create updated student record
                updated_student = regular_student.copy()
                updated_student['subjectGrades'] = updated_subject_list
                updated_student['lastUpdated'] = datetime.now().isoformat()
                updated_student['supplyProcessed'] = True
                updated_student['supplyImprovements'] = len(student_changes)
                updated_student['supplyChanges'] = student_changes
                
                updated_students.append(updated_student)
                
                improvements['details'].append({
                    'htno': supply_htno,
                    'name': regular_student.get('student_name', 'N/A'),
                    'improvements': len(student_changes),
                    'changes': student_changes
                })
        
        # Step 4: Save results
        print(f"\n💾 Saving fixed results...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"fixed_supply_merge_{timestamp}.json"
        
        output_data = {
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'supply_pdf': pdf_path,
                'regular_source': str(latest_file),
                'processing_type': 'fixed_supply_merge',
                'original_filename': 'Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf',
                'fixes_applied': [
                    'Subject code normalization',
                    'Duplicate subject removal',
                    'Proper subject matching by code',
                    'Fixed Advanced Data Structures matching'
                ]
            },
            'statistics': improvements,
            'updated_students': updated_students,
            'merge_summary': {
                'total_supply_students': len(supply_results),
                'total_regular_students': len(regular_students),
                'students_matched': improvements['students_found'],
                'students_improved': improvements['students_updated'],
                'f_to_pass_conversions': improvements['f_grade_improvements'],
                'grade_improvements': improvements['grades_improved'] - improvements['f_grade_improvements'],
                'new_subjects': improvements['new_subjects_added'],
                'duplicates_removed': improvements['duplicates_removed']
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Step 5: Display results
        print(f"  ✓ Fixed results saved to: {output_file}")
        
        print(f"\n🎯 FIXED PROCESSING SUMMARY:")
        print(f"  📊 Supply students processed: {improvements['students_processed']}")
        print(f"  🔍 Students found in regular: {improvements['students_found']}")
        print(f"  ✅ Students with improvements: {improvements['students_updated']}")
        print(f"  📈 Total grade improvements: {improvements['grades_improved']}")
        print(f"  🎓 F→Pass conversions: {improvements['f_grade_improvements']}")
        print(f"  🆕 New subjects added: {improvements['new_subjects_added']}")
        print(f"  🧹 Duplicates removed: {improvements['duplicates_removed']}")
        
        if improvements['details']:
            print(f"\n📋 FIXED IMPROVEMENTS (Advanced Data Structures should now show correct grades):")
            for i, detail in enumerate(improvements['details'][:10]):  # Show first 10
                print(f"  {i+1}. {detail['htno']} ({detail['name']}): {detail['improvements']} improvements")
                for change in detail['changes']:
                    subject_name = change['subject_name']
                    if 'ADVANCED DATA STRUCTURES' in subject_name.upper():
                        print(f"     🔧 FIXED: {change['subject_code']} ({subject_name}): {change['improvement']} ({change['reason']})")
                    elif i < 3:  # Show first 3 students' other changes
                        print(f"     - {change['subject_code']}: {change['improvement']} ({change['reason']})")
            
            if len(improvements['details']) > 10:
                print(f"  ... and {len(improvements['details']) - 10} more students")
        
        print(f"\n🎉 FIXED processing complete! Advanced Data Structures issue should be resolved.")
        print(f"📄 Results saved to: {output_file}")
        
        if improvements['f_grade_improvements'] > 0:
            print(f"🌟 Great news! {improvements['f_grade_improvements']} students converted F grades to Pass!")
            
        return output_file
        
    except ImportError as e:
        print(f"❌ Module import error: {e}")
        print("Make sure you have all required dependencies installed.")
        return None
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result_file = fixed_supply_processing()
    if result_file:
        print(f"\n🏁 Fixed processing done! Check the result file: {result_file}")
        print(f"📋 Advanced Data Structures & Algorithms should now show the correct supply grades!")
    else:
        print(f"\n💥 Processing failed. Please check the errors above.")
