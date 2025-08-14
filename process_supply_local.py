#!/usr/bin/env python3
"""
Standalone 2-1 Supply PDF Processor
This processes your supply PDF locally without needing the Flask server
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def process_supply_locally():
    """Process the supply PDF locally using the existing logic"""
    
    print("🏠 LOCAL 2-1 SUPPLY PDF PROCESSOR")
    print("=" * 50)
    
    pdf_path = r"c:\temp\supply_21.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    try:
        # Import the required modules
        print("📦 Loading modules...")
        from parser.parser_jntuk import parse_jntuk_pdf
        from batch_pdf_processor import smart_supply_merge_by_subject
        print("  ✓ Modules loaded successfully")
        
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
        
        # Step 3: Process each supply student
        print(f"\n🔄 Processing supply results...")
        
        improvements = {
            'students_processed': 0,
            'students_updated': 0,
            'grades_improved': 0,
            'f_grade_improvements': 0,
            'new_subjects_added': 0,
            'details': []
        }
        
        # Create a lookup for regular students by HTNO
        regular_lookup = {}
        for student in regular_students:
            htno = student.get('student_id')
            if htno:
                regular_lookup[htno] = student
        
        print(f"  📊 Regular students indexed: {len(regular_lookup)}")
        
        # Process each supply student
        merged_students = []
        
        for supply_student in supply_results:
            supply_htno = supply_student.get('student_id')
            improvements['students_processed'] += 1
            
            if not supply_htno:
                continue
            
            # Find matching regular student
            regular_student = regular_lookup.get(supply_htno)
            
            if not regular_student:
                print(f"  ⚠️  No regular record found for {supply_htno}")
                continue
            
            # Get subjects
            regular_subjects = regular_student.get('subjectGrades', [])
            supply_subjects = supply_student.get('subjectGrades', [])
            
            if not supply_subjects:
                continue
            
            # Use the smart merge function
            try:
                merged_subjects_dict, merge_report = smart_supply_merge_by_subject(
                    regular_subjects, 
                    supply_subjects, 
                    datetime.now().isoformat()
                )
                
                # Check if any improvements were made
                if merge_report['grades_improved'] > 0:
                    improvements['students_updated'] += 1
                    improvements['grades_improved'] += merge_report['grades_improved']
                    improvements['f_grade_improvements'] += merge_report['f_grade_improvements']
                    improvements['new_subjects_added'] += merge_report['new_subjects_added']
                    
                    # Create updated student record
                    updated_student = regular_student.copy()
                    updated_student['subjectGrades'] = list(merged_subjects_dict.values())
                    updated_student['lastUpdated'] = datetime.now().isoformat()
                    updated_student['supplyProcessed'] = True
                    updated_student['supplyImprovements'] = merge_report
                    
                    merged_students.append(updated_student)
                    
                    improvements['details'].append({
                        'htno': supply_htno,
                        'name': regular_student.get('student_name', 'N/A'),
                        'improvements': merge_report
                    })
                    
                    print(f"  ✅ {supply_htno}: {merge_report['grades_improved']} grades improved")
                
            except Exception as e:
                print(f"  ❌ Error processing {supply_htno}: {e}")
        
        # Step 4: Save results
        print(f"\n💾 Saving results...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"supply_merge_results_{timestamp}.json"
        
        output_data = {
            'metadata': {
                'processed_at': datetime.now().isoformat(),
                'supply_pdf': pdf_path,
                'regular_source': str(latest_file),
                'processing_type': 'local_supply_merge'
            },
            'statistics': improvements,
            'updated_students': merged_students
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Step 5: Display results
        print(f"  ✓ Results saved to: {output_file}")
        
        print(f"\n🎯 PROCESSING SUMMARY:")
        print(f"  👥 Students processed: {improvements['students_processed']}")
        print(f"  ✅ Students updated: {improvements['students_updated']}")
        print(f"  📈 Total grades improved: {improvements['grades_improved']}")
        print(f"  🎓 F→Better improvements: {improvements['f_grade_improvements']}")
        print(f"  🆕 New subjects added: {improvements['new_subjects_added']}")
        
        if improvements['details']:
            print(f"\n📋 DETAILED IMPROVEMENTS:")
            for detail in improvements['details'][:10]:  # Show first 10
                print(f"  {detail['htno']} ({detail['name']}): "
                      f"{detail['improvements']['grades_improved']} improved, "
                      f"{detail['improvements']['f_grade_improvements']} F→Better")
            
            if len(improvements['details']) > 10:
                print(f"  ... and {len(improvements['details']) - 10} more students")
        
        print(f"\n🎉 Processing complete! Your 2-1 supply results have been merged.")
        
    except ImportError as e:
        print(f"❌ Module import error: {e}")
        print("Make sure you have all required dependencies installed.")
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    process_supply_locally()
