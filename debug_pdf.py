#!/usr/bin/env python3
"""
Debug script to check PDF content for BTECH 2-1 file
"""

import pdfplumber
import re

def debug_pdf_content():
    pdf_path = "BTECH 2-1 RESULT FEB 2025.pdf"
    
    print(f"🔍 Debugging PDF content for: {pdf_path}")
    print("=" * 60)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i in range(min(2, len(pdf.pages))):
                print(f"\n📄 Page {i+1} content:")
                print("-" * 40)
                text = pdf.pages[i].extract_text()
                if text:
                    # Show first 1000 characters
                    print(text[:1000])
                    print("..." if len(text) > 1000 else "")
                    
                    # Check for specific patterns
                    print(f"\n🔍 Pattern analysis:")
                    if re.search(r'2-1', text.lower()):
                        print("✅ Found '2-1' pattern")
                    if re.search(r'ii semester', text.lower()):
                        print("✅ Found 'II Semester' pattern")
                    if re.search(r'i semester', text.lower()):
                        print("✅ Found 'I Semester' pattern")
                    if re.search(r'second semester', text.lower()):
                        print("✅ Found 'Second Semester' pattern")
                        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_pdf_content()
