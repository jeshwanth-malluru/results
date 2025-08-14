#!/usr/bin/env python3
"""
🚀 Upload Supply PDF with Correct Filename
Fixed curl command and test with your actual PDF
"""

def show_correct_curl_command():
    """Show the corrected curl command with your actual PDF filename"""
    print("✅ CORRECTED CURL COMMAND")
    print("=" * 60)
    
    # Your actual PDF filename
    pdf_filename = "Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf"
    
    print(f"📁 Your PDF file: {pdf_filename}")
    print()
    
    print("🔧 Windows Command Prompt:")
    print(f'''
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" ^
  -H "X-API-Key: your-api-key-here" ^
  -F "pdf=@{pdf_filename}" ^
  -F "format=jntuk"
    ''')
    
    print("🔧 PowerShell:")
    print(f'''
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" `
  -H "X-API-Key: your-api-key-here" `
  -F "pdf=@{pdf_filename}" `
  -F "format=jntuk"
    ''')
    
    print("🔧 Linux/Mac Terminal:")
    print(f'''
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" \\
  -H "X-API-Key: your-api-key-here" \\
  -F "pdf=@{pdf_filename}" \\
  -F "format=jntuk"
    ''')

def show_what_will_happen():
    """Explain exactly what the system will do"""
    print("\n\n🧠 WHAT THE SYSTEM WILL DO")
    print("=" * 60)
    
    print("📖 1. PDF PARSING:")
    print("   ✅ Extract student HTNOs (Hall Ticket Numbers)")
    print("   ✅ Extract subject codes and grades from supply results")
    print("   ✅ Parse 'Results of II B.Tech I Semester Supplementary' format")
    print()
    
    print("🔍 2. FIREBASE LOOKUP:")
    print("   ✅ Search existing records by HTNO")
    print("   ✅ Find regular results for same students")
    print("   ✅ Load current subject grades")
    print()
    
    print("🎯 3. SMART GRADE REPLACEMENT:")
    print("   ✅ Match subjects by subject code")
    print("   ✅ Find regular grades with 'F' (Failed)")
    print("   ✅ Replace F with supply grade (if supply grade is better)")
    print("   ✅ Track attempt count (Regular=1, Supply=2, etc.)")
    print()
    
    print("📊 4. EXAMPLES OF REPLACEMENTS:")
    print("   Regular: CS101=F → Supply: CS101=C → Final: CS101=C (Attempt #2) ✅")
    print("   Regular: MA101=F → Supply: MA101=B → Final: MA101=B (Attempt #2) ✅")
    print("   Regular: PH101=C → Supply: PH101=D → Final: PH101=C (Attempt #2) ❌ (No downgrade)")
    print("   Regular: EN101=B → Supply: EN101=A → Final: EN101=A (Attempt #2) ✅ (Improvement)")

def create_python_test_script():
    """Create a Python script to test the upload"""
    print("\n\n🐍 PYTHON TEST SCRIPT")
    print("=" * 60)
    
    script_content = '''#!/usr/bin/env python3
"""
Test script for uploading your specific supply PDF
"""
import requests
import json
import os

def upload_supply_pdf():
    """Upload your specific supply PDF"""
    
    # Your specific PDF file
    pdf_filename = "Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf"
    
    # Check if file exists
    if not os.path.exists(pdf_filename):
        print(f"❌ File not found: {pdf_filename}")
        print("💡 Make sure the PDF is in the same directory as this script")
        return
    
    # Your deployed server
    url = "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf"
    api_key = "your-api-key-here"  # Replace with your actual API key
    
    print(f"🎯 Uploading: {pdf_filename}")
    print(f"🌐 Server: {url}")
    print("⏳ Processing...")
    
    try:
        with open(pdf_filename, 'rb') as pdf_file:
            files = {'pdf': pdf_file}
            data = {'format': 'jntuk'}
            headers = {'X-API-Key': api_key}
            
            response = requests.post(url, files=files, data=data, headers=headers)
            
            print(f"📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ SUCCESS! Supply PDF processed")
                print("\\n📊 PROCESSING STATISTICS:")
                
                stats = result.get('stats', {})
                print(f"   👥 Students processed: {stats.get('total_processed', 0)}")
                print(f"   🔍 Students found in Firebase: {stats.get('students_found_in_firebase', 0)}")
                print(f"   🔄 Students updated: {stats.get('students_updated', 0)}")
                print(f"   📈 Subjects overwritten: {stats.get('subjects_overwritten', 0)}")
                print(f"   ➕ Subjects added: {stats.get('subjects_added', 0)}")
                print(f"   🔢 Total attempts tracked: {stats.get('total_attempts_tracked', 0)}")
                
                # Show grade improvements (F → better grades)
                improvements = result.get('improvements', {}).get('grade_improvements', [])
                if improvements:
                    print("\\n🎉 GRADE IMPROVEMENTS (F → Better Grades):")
                    for imp in improvements:
                        print(f"   {imp['student_id']} - {imp['subject_code']}: {imp['from_grade']} → {imp['to_grade']} (Attempt #{imp['attempt_number']})")
                else:
                    print("\\n📝 No grade improvements found")
                    print("   (This could mean no students had F grades that were improved in supply)")
                
                return result
                
            elif response.status_code == 401:
                print("❌ AUTHENTICATION ERROR")
                print("🔑 Please update the API key in this script")
                
            else:
                print(f"❌ Error {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Raw response: {response.text}")
                    
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_filename}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    upload_supply_pdf()
'''
    
    print("📝 Save this as 'upload_my_supply.py' and run it:")
    print(script_content)
    
    print("\n▶️ To run:")
    print("   python upload_my_supply.py")

def show_api_key_locations():
    """Show where to find the API key"""
    print("\n\n🔑 WHERE TO FIND YOUR API KEY")
    print("=" * 60)
    
    print("📍 Check these locations for your API key:")
    print("   1. app.py file - look for VALID_API_KEYS")
    print("   2. config.py file - look for API_KEY")
    print("   3. .env file - look for API_KEY")
    print("   4. Google Cloud environment variables")
    print()
    
    print("🔍 Current API key in app.py:")
    print('   VALID_API_KEYS = {"my-very-secret-admin-api-key"}')
    print()
    
    print("✅ Use this API key in your requests:")
    print('   "my-very-secret-admin-api-key"')

if __name__ == "__main__":
    show_correct_curl_command()
    show_what_will_happen()
    create_python_test_script()
    show_api_key_locations()
