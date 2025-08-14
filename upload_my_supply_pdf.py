#!/usr/bin/env python3
"""
🎯 READY-TO-USE: Upload Your Supply PDF
Script configured with your exact PDF filename and API key
"""
import requests
import json
import os

def upload_supply_pdf():
    """Upload your specific supply PDF with smart F → better grade replacement"""
    
    # Your specific PDF file (the one you mentioned)
    pdf_filename = "Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf"
    
    # Your deployed server and API key
    url = "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf"
    api_key = "my-very-secret-admin-api-key"  # Your actual API key from app.py
    
    print("🎯 SUPPLY PDF UPLOAD - SMART F → BETTER GRADE REPLACEMENT")
    print("=" * 70)
    print(f"📁 PDF File: {pdf_filename}")
    print(f"🌐 Server: {url}")
    print(f"🔑 API Key: {api_key[:10]}...")
    print()
    
    # Check if file exists
    if not os.path.exists(pdf_filename):
        print(f"❌ File not found: {pdf_filename}")
        print("💡 Please copy the PDF to this directory first")
        print("📂 Expected location: Same folder as this script")
        return
    
    file_size = os.path.getsize(pdf_filename) / (1024 * 1024)  # MB
    print(f"📊 File size: {file_size:.1f} MB")
    
    print("\n🧠 What this will do:")
    print("   1. Parse supply PDF to extract HTNOs and subject grades")
    print("   2. Find existing regular results in Firebase by HTNO")
    print("   3. For each subject code:")
    print("      • If regular grade = F and supply grade > F → REPLACE ✅")
    print("      • If supply grade > regular grade → REPLACE ✅") 
    print("      • If supply grade ≤ regular grade → KEEP original ❌")
    print("   4. Track attempt counts (Regular=1, Supply=2, etc.)")
    print("   5. Maintain detailed improvement history")
    
    choice = input("\n🚀 Proceed with upload? (y/n): ").lower()
    if choice != 'y':
        print("❌ Upload cancelled")
        return
    
    print("\n⏳ Uploading and processing...")
    
    try:
        with open(pdf_filename, 'rb') as pdf_file:
            files = {'pdf': pdf_file}
            data = {'format': 'jntuk'}
            headers = {'X-API-Key': api_key}
            
            response = requests.post(url, files=files, data=data, headers=headers)
            
            print(f"\n📡 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ SUCCESS! Supply PDF processed with smart merge")
                print("\n📊 PROCESSING STATISTICS:")
                print("=" * 50)
                
                stats = result.get('stats', {})
                print(f"👥 Students processed: {stats.get('total_processed', 0)}")
                print(f"🔍 Students found in Firebase: {stats.get('students_found_in_firebase', 0)}")
                print(f"❌ Students not found: {stats.get('students_not_found', 0)}")
                print(f"🔄 Students updated: {stats.get('students_updated', 0)}")
                print(f"📈 Subjects overwritten: {stats.get('subjects_overwritten', 0)}")
                print(f"➕ Subjects added: {stats.get('subjects_added', 0)}")
                print(f"🔢 Total attempts tracked: {stats.get('total_attempts_tracked', 0)}")
                
                # Show grade improvements (especially F → better grades)
                improvements = result.get('improvements', {}).get('grade_improvements', [])
                if improvements:
                    print(f"\n🎉 GRADE IMPROVEMENTS ({len(improvements)} total):")
                    print("=" * 50)
                    
                    f_improvements = 0
                    other_improvements = 0
                    
                    for imp in improvements:
                        htno = imp['student_id']
                        subject = imp['subject_code'] 
                        from_grade = imp['from_grade']
                        to_grade = imp['to_grade']
                        attempt = imp['attempt_number']
                        
                        if from_grade == 'F':
                            print(f"🎯 {htno} - {subject}: F → {to_grade} (Attempt #{attempt}) [FAILED TO PASSED]")
                            f_improvements += 1
                        else:
                            print(f"📈 {htno} - {subject}: {from_grade} → {to_grade} (Attempt #{attempt}) [GRADE IMPROVED]")
                            other_improvements += 1
                    
                    print(f"\n📊 IMPROVEMENT SUMMARY:")
                    print(f"   🎯 F → Better Grade: {f_improvements}")
                    print(f"   📈 Other Improvements: {other_improvements}")
                    print(f"   🎉 Total Improvements: {len(improvements)}")
                    
                else:
                    print("\n📝 No grade improvements found")
                    print("💡 Possible reasons:")
                    print("   • No students had F grades that improved in supply")
                    print("   • Supply grades weren't better than existing grades")
                    print("   • Students not found in regular results database")
                
                # Show cloud storage info
                if 'firebase' in result and result['firebase'].get('storage_url'):
                    print(f"\n☁️ PDF stored at: {result['firebase']['storage_url']}")
                
                print(f"\n✅ Upload completed successfully!")
                return result
                
            elif response.status_code == 401:
                print("❌ AUTHENTICATION ERROR")
                print("🔑 API key authentication failed")
                print("💡 The API key might have been changed")
                
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ BAD REQUEST: {error_data.get('error', 'Unknown error')}")
                print("💡 Check if the PDF format is correct")
                
            else:
                print(f"❌ Error {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data.get('error', 'Unknown error')}")
                except:
                    print(f"Raw response: {response.text}")
                    
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_filename}")
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR")
        print("🌐 Cannot connect to the server")
        print("💡 Check your internet connection")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def show_curl_alternative():
    """Show the curl command as an alternative"""
    print("\n\n💻 ALTERNATIVE: Use curl command")
    print("=" * 50)
    
    pdf_filename = "Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf"
    
    print("🔧 Windows Command Prompt:")
    print(f'''
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" ^
  -H "X-API-Key: my-very-secret-admin-api-key" ^
  -F "pdf=@{pdf_filename}" ^
  -F "format=jntuk"
    ''')

if __name__ == "__main__":
    upload_supply_pdf()
    show_curl_alternative()
