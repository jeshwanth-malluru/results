#!/usr/bin/env python3
"""
Complete 2-1 Supply PDF Processing with Working Logic
This will process your actual supply PDF and merge it correctly
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

def complete_supply_processing():
    """Complete processing of the 2-1 supply PDF"""
    
    print("🚀 COMPLETE 2-1 SUPPLY PDF PROCESSING")
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
        
        # Step 3: Process merging
        print(f"\n🔄 Processing supply merge...")
        
        # Create lookup for regular students
        regular_lookup = {}
        for student in regular_students:
            htno = student.get('student_id')
            if htno:
                regular_lookup[htno] = student
        
        improvements = {
            'students_processed': 0,
            'students_found': 0,
            'students_updated': 0,
            'grades_improved': 0,
            'f_grade_improvements': 0,
            'new_subjects_added': 0,
            'details': []
        }
        
        updated_students = []
        
        # Process each supply student
        for supply_student in supply_results:
            supply_htno = supply_student.get('student_id')
            improvements['students_processed'] += 1
            
            if not supply_htno:
                continue
            
            # Find matching regular student
            regular_student = regular_lookup.get(supply_htno)
            
            if not regular_student:
                continue
                
            improvements['students_found'] += 1
            
            # Get subjects
            regular_subjects = regular_student.get('subjectGrades', [])
            supply_subjects = supply_student.get('subjectGrades', [])
            
            if not supply_subjects:
                continue
            
            # Create lookup for regular subjects by code
            regular_subject_lookup = {}
            for subject in regular_subjects:
                code = subject.get('code')
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
                supply_code = supply_subject.get('code')
                supply_grade = supply_subject.get('grade', 'F')
                supply_result = supply_subject.get('result', 'Fail')
                
                if not supply_code:
                    continue
                
                # Find matching regular subject
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
                            if subj.get('code') == supply_code:
                                updated_subject_list[i] = supply_subject.copy()
                                updated_subject_list[i]['attempts'] = 2
                                updated_subject_list[i]['previousGrade'] = regular_grade
                                updated_subject_list[i]['previousResult'] = regular_result
                                updated_subject_list[i]['improvement'] = f"{regular_grade}→{supply_grade}"
                                break
                        
                        student_changes.append({
                            'subject': supply_code,
                            'regular_grade': regular_grade,
                            'supply_grade': supply_grade,
                            'improvement': f"{regular_grade}→{supply_grade}",
                            'reason': update_reason
                        })
                        
                        improvements['grades_improved'] += 1
                        has_improvements = True
                
                else:
                    # Add new subject
                    new_subject = supply_subject.copy()
                    new_subject['attempts'] = 1
                    new_subject['isNewFromSupply'] = True
                    updated_subject_list.append(new_subject)
                    improvements['new_subjects_added'] += 1
                    has_improvements = True
                    
                    student_changes.append({
                        'subject': supply_code,
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
                
                print(f"  ✅ {supply_htno}: {len(student_changes)} improvements")
        
        # Step 4: Save results
        print(f"\n💾 Saving results...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"complete_supply_merge_{timestamp}.json"
        
        output_data = {
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'supply_pdf': pdf_path,
                'regular_source': str(latest_file),
                'processing_type': 'complete_supply_merge',
                'original_filename': 'Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf'
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
                'new_subjects': improvements['new_subjects_added']
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Step 5: Display results
        print(f"  ✓ Results saved to: {output_file}")
        
        print(f"\n🎯 FINAL PROCESSING SUMMARY:")
        print(f"  📊 Supply students processed: {improvements['students_processed']}")
        print(f"  🔍 Students found in regular: {improvements['students_found']}")
        print(f"  ✅ Students with improvements: {improvements['students_updated']}")
        print(f"  📈 Total grade improvements: {improvements['grades_improved']}")
        print(f"  🎓 F→Pass conversions: {improvements['f_grade_improvements']}")
        print(f"  🆕 New subjects added: {improvements['new_subjects_added']}")
        
        if improvements['details']:
            print(f"\n📋 DETAILED IMPROVEMENTS:")
            for i, detail in enumerate(improvements['details'][:10]):  # Show first 10
                print(f"  {i+1}. {detail['htno']} ({detail['name']}): {detail['improvements']} improvements")
                for change in detail['changes'][:2]:  # Show first 2 changes
                    print(f"     - {change['subject']}: {change['improvement']} ({change['reason']})")
                if len(detail['changes']) > 2:
                    print(f"     ... and {len(detail['changes']) - 2} more")
            
            if len(improvements['details']) > 10:
                print(f"  ... and {len(improvements['details']) - 10} more students")
        
        print(f"\n🎉 Processing complete! Your 2-1 supply results have been merged.")
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
    result_file = complete_supply_processing()
    if result_file:
        print(f"\n🏁 All done! Check the result file: {result_file}")
    else:
        print(f"\n💥 Processing failed. Please check the errors above.")
