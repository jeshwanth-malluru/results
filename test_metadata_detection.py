#!/usr/bin/env python3
"""
Test script for the new metadata detection system
"""

import os
import glob
from batch_pdf_processor import detect_pdf_metadata

def test_metadata_detection():
    """Test the new metadata detection on available PDFs"""
    print("🧪 Testing Enhanced PDF Metadata Detection")
    print("=" * 60)
    
    # Find all PDF files
    pdf_files = []
    pdf_patterns = ["*.pdf", "*.PDF"]
    
    for pattern in pdf_patterns:
        pdf_files.extend(glob.glob(pattern, recursive=False))
    
    # Remove duplicates
    pdf_files = list(set(pdf_files))
    
    if not pdf_files:
        print("❌ No PDF files found for testing")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files to test:")
    for pdf in pdf_files:
        print(f"   📄 {os.path.basename(pdf)}")
    
    print("\n" + "=" * 60)
    print("🔍 Testing Metadata Detection")
    print("=" * 60)
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n📄 Test {i}/{len(pdf_files)}: {os.path.basename(pdf_path)}")
        print("-" * 50)
        
        try:
            metadata = detect_pdf_metadata(pdf_path)
            
            print(f"📊 RESULTS:")
            print(f"   Format: {metadata['format']}")
            print(f"   Year: {metadata['year']}")
            print(f"   Semester: {metadata['semesters'][0]}")
            print(f"   Exam Type: {metadata['exam_types'][0]}")
            
        except Exception as e:
            print(f"❌ Error detecting metadata: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Metadata Detection Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_metadata_detection()
