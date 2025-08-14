#!/usr/bin/env python3
"""
Test 2-1 Supply Processing Logic
This script simulates the processing of your 2-1 supply PDF
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simulate_supply_processing():
    """Simulate processing the 2-1 supply PDF"""
    
    print("🧪 SIMULATING 2-1 SUPPLY PDF PROCESSING")
    print("=" * 60)
    
    # First, let's check if we can import the necessary modules
    try:
        print("📦 Checking dependencies...")
        
        # Check if batch processor exists
        if os.path.exists('batch_pdf_processor.py'):
            print("  ✓ batch_pdf_processor.py found")
        else:
            print("  ❌ batch_pdf_processor.py not found")
            return
        
        # Check if PDF parsers exist
        parser_dir = 'parser'
        if os.path.exists(parser_dir):
            print(f"  ✓ {parser_dir} directory found")
            if os.path.exists(os.path.join(parser_dir, 'parser_jntuk.py')):
                print("  ✓ JNTUK parser found")
            else:
                print("  ⚠️  JNTUK parser not found")
        else:
            print(f"  ❌ {parser_dir} directory not found")
        
        # Check PDF file
        pdf_path = r"c:\temp\supply_21.pdf"
        if os.path.exists(pdf_path):
            file_size = os.path.getsize(pdf_path) / 1024  # KB
            print(f"  ✓ Supply PDF found ({file_size:.1f} KB)")
        else:
            print(f"  ❌ Supply PDF not found at {pdf_path}")
            return
        
        print("\n🔬 WHAT WOULD HAPPEN:")
        print("1. 📄 Parse the 2-1 supply PDF using JNTUK parser")
        print("2. 🔍 Extract student HTNOs and subject grades")
        print("3. 🔗 Connect to Firebase to find existing 2-1 regular results")
        print("4. 📊 For each student found:")
        print("   - Match by HTNO (student ID)")
        print("   - Compare grades by subject code")
        print("   - Replace F grades with better supply grades")
        print("   - Keep original grades if supply grade is worse")
        print("   - Track attempt counts (attempt #2 for supply)")
        print("5. 💾 Update Firebase with merged results")
        print("6. 📈 Generate improvement report")
        
        print(f"\n📋 EXPECTED IMPROVEMENTS:")
        print("✅ Students who had F grades in regular exams")
        print("✅ And passed those subjects in supply exams")
        print("✅ Will have their grades updated (F→D, F→C, etc.)")
        print("✅ Attempt count will show '2' for supply subjects")
        print("✅ Original pass grades remain unchanged")
        
        # Check if we have any existing data files to show what we'd merge with
        data_dir = 'data'
        if os.path.exists(data_dir):
            json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
            if json_files:
                print(f"\n📁 EXISTING DATA FILES ({len(json_files)} found):")
                for i, filename in enumerate(json_files[:3]):  # Show first 3
                    print(f"  {i+1}. {filename}")
                if len(json_files) > 3:
                    print(f"  ... and {len(json_files) - 3} more")
                    
                # Try to show a sample from the most recent file
                try:
                    latest_file = max(json_files, key=lambda f: os.path.getctime(os.path.join(data_dir, f)))
                    latest_path = os.path.join(data_dir, latest_file)
                    with open(latest_path, 'r') as f:
                        data = json.load(f)
                        total_students = len(data.get('students', []))
                        metadata = data.get('metadata', {})
                        print(f"\n📊 LATEST DATA FILE: {latest_file}")
                        print(f"  Students: {total_students}")
                        print(f"  Format: {metadata.get('format', 'unknown')}")
                        print(f"  Exam Type: {metadata.get('exam_type', 'unknown')}")
                        print(f"  Processed: {metadata.get('processed_at', 'unknown')}")
                        
                        if total_students > 0:
                            sample_student = data['students'][0]
                            print(f"\n👨‍🎓 SAMPLE STUDENT (would be matched for merge):")
                            print(f"  HTNO: {sample_student.get('student_id', 'N/A')}")
                            print(f"  Name: {sample_student.get('student_name', 'N/A')}")
                            print(f"  Semester: {sample_student.get('semester', 'N/A')}")
                            subjects = sample_student.get('subjectGrades', [])
                            if subjects:
                                print(f"  Subjects: {len(subjects)}")
                                # Show any F grades that could be improved
                                f_grades = [s for s in subjects if s.get('grade') == 'F']
                                if f_grades:
                                    print(f"  F grades (could be improved): {len(f_grades)}")
                                    for fg in f_grades[:2]:  # Show first 2
                                        print(f"    - {fg.get('code', 'N/A')}: F (could become D/C/B if passed in supply)")
                                else:
                                    print(f"  No F grades found (good performance!)")
                except Exception as e:
                    print(f"  ⚠️  Could not read sample data: {e}")
            else:
                print(f"\n📁 No JSON data files found in {data_dir}")
        else:
            print(f"\n📁 Data directory {data_dir} not found")
        
        print(f"\n🚀 TO PROCEED WITH ACTUAL UPLOAD:")
        print("1. Make sure your Flask server is running")
        print("2. Use one of these methods:")
        print("   • Python script: python upload_21_supply.py")
        print("   • PowerShell: Run upload_21_supply_fixed.ps1")
        print("   • curl: curl -X POST -H 'X-API-Key: my-very-secret-admin-api-key' \\")
        print("           -F 'pdf=@c:\\temp\\supply_21.pdf' -F 'format=jntuk' \\")
        print("           http://localhost:8080/upload-supply-pdf")
        
    except Exception as e:
        print(f"❌ Error during simulation: {e}")

if __name__ == "__main__":
    simulate_supply_processing()
