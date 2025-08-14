#!/usr/bin/env python3
"""
Quick Test: Upload Supply PDF
Simple script to test supply PDF upload functionality
"""

import os
import requests
import json
from batch_pdf_processor import process_supply_pdf_with_smart_merge

def test_direct_function_call():
    """Test the supply processing function directly"""
    print("🔧 TESTING DIRECT FUNCTION CALL")
    print("=" * 50)
    
    # Look for existing PDF files
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in current directory")
        return
    
    print(f"📁 Found PDF files: {pdf_files}")
    
    # Use the first PDF file
    pdf_file = pdf_files[0]
    print(f"🎯 Testing with: {pdf_file}")
    
    try:
        # Call the direct function
        result = process_supply_pdf_with_smart_merge(
            pdf_path=pdf_file,
            format_type="jntuk",  # Adjust based on your PDF
            original_filename=pdf_file
        )
        
        print("\n✅ DIRECT FUNCTION CALL SUCCESS!")
        print(f"Result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def test_api_upload_local():
    """Test uploading via local API"""
    print("\n\n🌐 TESTING LOCAL API UPLOAD")
    print("=" * 50)
    
    # Check if there are PDF files
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found for API testing")
        return
    
    pdf_file = pdf_files[0]
    print(f"🎯 Testing API upload with: {pdf_file}")
    
    # Test local API (assuming server is running)
    url = "http://localhost:5000/upload-supply-pdf"
    
    try:
        with open(pdf_file, 'rb') as f:
            files = {'pdf': f}
            data = {'format': 'jntuk'}
            headers = {'X-API-Key': 'test-key'}
            
            print("📤 Uploading to local API...")
            response = requests.post(url, files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ API UPLOAD SUCCESS!")
                print(f"📊 Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(f"Response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the local server running?")
        print("💡 Start server with: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_available_pdfs():
    """Show what PDF files are available for testing"""
    print("📁 AVAILABLE PDF FILES")
    print("=" * 50)
    
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if pdf_files:
        for i, pdf_file in enumerate(pdf_files, 1):
            file_size = os.path.getsize(pdf_file) / (1024 * 1024)  # MB
            print(f"{i}. {pdf_file} ({file_size:.1f} MB)")
    else:
        print("❌ No PDF files found in current directory")
        print("💡 Add some PDF files to test with")

if __name__ == "__main__":
    show_available_pdfs()
    test_direct_function_call()
    test_api_upload_local()
