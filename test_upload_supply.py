#!/usr/bin/env python3
"""
🚀 Quick Test: Upload Supply PDF to Your Deployed System
Ready-to-use script for testing supply PDF upload
"""

import requests
import json
import os

def upload_supply_pdf_test():
    """Test uploading one of your existing PDFs as a supply PDF"""
    
    # Your deployed server
    url = "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf"
    api_key = "your-api-key-here"  # Replace with your actual API key
    
    # Look for available PDF files
    pdf_files = [
        "BTECH 2-1 RESULT FEB 2025.pdf",
        "1st BTech 1st Sem (CR24) Results.pdf", 
        "Result of I B.Tech I Semester (R19R20R23) Regular  Supplementary Examinations, Jan-2024.pdf",
        "Results of I B.Tech II Semester (R23R20R19R16) RegularSupplementary Examinations, July-2024.pdf"
    ]
    
    print("🔍 Looking for PDF files to test with...")
    
    available_pdfs = []
    for pdf_file in pdf_files:
        if os.path.exists(pdf_file):
            file_size = os.path.getsize(pdf_file) / (1024 * 1024)  # MB
            available_pdfs.append((pdf_file, file_size))
            print(f"✅ Found: {pdf_file} ({file_size:.1f} MB)")
    
    if not available_pdfs:
        print("❌ No PDF files found. Make sure you're in the backend directory.")
        return
    
    # Use the first available PDF
    test_pdf, size = available_pdfs[0]
    print(f"\n🎯 Testing with: {test_pdf}")
    
    # Determine format (most of your PDFs appear to be JNTUK)
    if "autonomous" in test_pdf.lower():
        format_type = "autonomous"
    else:
        format_type = "jntuk"
    
    print(f"📋 Format: {format_type}")
    print(f"🌐 Server: {url}")
    print(f"🔑 API Key: {api_key[:10]}..." if len(api_key) > 10 else api_key)
    
    # Show what this test will do
    print(f"\n📝 This test will:")
    print(f"   1. Upload {test_pdf} as a supply PDF")
    print(f"   2. Parse the PDF for student results")
    print(f"   3. Look for existing students in Firebase")
    print(f"   4. Apply smart merge logic")
    print(f"   5. Show processing statistics")
    
    # Ask for confirmation
    print(f"\n⚠️  NOTE: Replace 'your-api-key-here' with your actual API key!")
    choice = input("🚀 Proceed with test? (y/n): ").lower()
    
    if choice != 'y':
        print("❌ Test cancelled")
        return
    
    print(f"\n⏳ Uploading {test_pdf}...")
    
    try:
        with open(test_pdf, 'rb') as pdf_file:
            files = {'pdf': pdf_file}
            data = {'format': format_type}
            headers = {'X-API-Key': api_key}
            
            response = requests.post(url, files=files, data=data, headers=headers)
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ SUCCESS! Supply PDF processed")
                print("\n📊 PROCESSING STATISTICS:")
                
                stats = result.get('stats', {})
                for key, value in stats.items():
                    print(f"   {key.replace('_', ' ').title()}: {value}")
                
                # Show improvements
                improvements = result.get('improvements', {}).get('grade_improvements', [])
                if improvements:
                    print("\n🎉 GRADE IMPROVEMENTS:")
                    for imp in improvements:
                        print(f"   {imp['student_id']} - {imp['subject_code']}: {imp['from_grade']} → {imp['to_grade']} (Attempt #{imp['attempt_number']})")
                else:
                    print("\n📝 No grade improvements found")
                    print("   (This is normal if supply grades aren't better than existing grades)")
                
                # Show cloud storage info
                if 'firebase' in result and result['firebase'].get('storage_url'):
                    print(f"\n☁️ PDF stored at: {result['firebase']['storage_url']}")
                
                print(f"\n✅ Full response:")
                print(json.dumps(result, indent=2))
                
            elif response.status_code == 401:
                print("❌ AUTHENTICATION ERROR")
                print("🔑 Please update the API key in this script")
                print("💡 Check your app.py or config files for the correct API key")
                
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ BAD REQUEST: {error_data.get('error', 'Unknown error')}")
                
            else:
                print(f"❌ Error {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Raw response: {response.text}")
                    
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR")
        print("🌐 Cannot connect to the server")
        print("💡 Check if the server URL is correct")
        print("💡 Check your internet connection")
        
    except FileNotFoundError:
        print(f"❌ File not found: {test_pdf}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def show_manual_testing_options():
    """Show alternative testing methods"""
    print("\n\n🛠️ ALTERNATIVE TESTING METHODS")
    print("=" * 50)
    
    print("1️⃣ Test with curl:")
    print("""
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" \\
  -H "X-API-Key: your-api-key-here" \\
  -F "pdf=@BTECH 2-1 RESULT FEB 2025.pdf" \\
  -F "format=jntuk"
    """)
    
    print("2️⃣ Test with Postman:")
    print("   - URL: https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf")
    print("   - Method: POST")
    print("   - Headers: X-API-Key: your-api-key-here")
    print("   - Body: form-data with 'pdf' file and 'format' field")
    
    print("3️⃣ Create a simple HTML upload form")
    print("   - Use the HTML example from the complete guide")

if __name__ == "__main__":
    print("🧪 SUPPLY PDF UPLOAD TEST")
    print("=" * 50)
    
    upload_supply_pdf_test()
    show_manual_testing_options()
