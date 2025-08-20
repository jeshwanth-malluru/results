#!/usr/bin/env python3
"""
Test autonomous PDF parsing to check if it's working
"""

import sys
import os
sys.path.append('.')

from parser.parser_autonomous import parse_autonomous_pdf

def test_autonomous_pdf_parsing():
    """Test parsing of local autonomous PDFs"""
    print("🧪 Testing Autonomous PDF Parsing")
    print("=" * 50)
    
    # List of local PDFs to test
    test_pdfs = [
        "1st BTech 1st Sem (CR24) Results.pdf",
        "BTECH 2-1 RESULT FEB 2025.pdf",
        "Results of I B.Tech II Semester (R23R20R19R16) RegularSupplementary Examinations, July-2024.pdf"
    ]
    
    for pdf_file in test_pdfs:
        if os.path.exists(pdf_file):
            print(f"\n📄 Testing: {pdf_file}")
            print("-" * 40)
            
            try:
                # Test parsing
                results = parse_autonomous_pdf(pdf_file)
                
                if results:
                    print(f"   ✅ Parsing successful!")
                    print(f"   📊 Students found: {len(results)}")
                    
                    # Show sample results
                    for i, student in enumerate(results[:3]):  # Show first 3
                        print(f"   🎓 Student {i+1}:")
                        print(f"      📝 ID: {student.get('student_id', 'N/A')}")
                        print(f"      👤 Name: {student.get('student_name', student.get('name', 'N/A'))}")
                        print(f"      📚 Semester: {student.get('semester', 'N/A')}")
                        print(f"      📈 SGPA: {student.get('sgpa', 'N/A')}")
                        
                        subjects = student.get('subjectGrades', student.get('subjects', []))
                        print(f"      📖 Subjects: {len(subjects)}")
                        
                        if i < len(results) - 1:
                            print()
                    
                    if len(results) > 3:
                        print(f"   ... and {len(results) - 3} more students")
                        
                    # Check if data is properly formatted for Firebase
                    sample_student = results[0]
                    required_fields = ['student_id', 'student_name', 'semester']
                    missing_fields = [field for field in required_fields if not sample_student.get(field)]
                    
                    if missing_fields:
                        print(f"   ⚠️ Missing required fields: {missing_fields}")
                    else:
                        print(f"   ✅ All required fields present")
                        
                else:
                    print(f"   ❌ No students found in PDF")
                    print(f"   💡 PDF might be in a different format or corrupted")
                    
            except Exception as e:
                print(f"   ❌ Parsing failed: {e}")
                import traceback
                print(f"   🔍 Error details: {traceback.format_exc()}")
        else:
            print(f"\n📄 {pdf_file} - File not found")
    
    print(f"\n" + "=" * 50)
    print("📊 AUTONOMOUS PDF PARSING SUMMARY")
    print("=" * 50)
    
    working_pdfs = []
    failed_pdfs = []
    
    for pdf_file in test_pdfs:
        if os.path.exists(pdf_file):
            try:
                results = parse_autonomous_pdf(pdf_file)
                if results:
                    working_pdfs.append(pdf_file)
                else:
                    failed_pdfs.append(pdf_file)
            except:
                failed_pdfs.append(pdf_file)
    
    if working_pdfs:
        print("✅ PDFs that parsed successfully:")
        for pdf in working_pdfs:
            print(f"   📄 {pdf}")
    
    if failed_pdfs:
        print("❌ PDFs that failed to parse:")
        for pdf in failed_pdfs:
            print(f"   📄 {pdf}")
    
    if not working_pdfs and not failed_pdfs:
        print("⚠️ No test PDFs found")
        print("💡 Make sure you have autonomous format PDFs in the workspace")
    
    return len(working_pdfs), len(failed_pdfs)

if __name__ == "__main__":
    test_autonomous_pdf_parsing()
