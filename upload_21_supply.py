#!/usr/bin/env python3
"""
Upload 2-1 Supply PDF to Student Result System
This script uploads your 2-1 supply PDF and intelligently merges it with existing regular results.
"""

import requests
import os
from pathlib import Path

# Configuration
API_URL = "https://student-result-backend-390507264435.us-central1.run.app"
API_KEY = "my-very-secret-admin-api-key"
PDF_PATH = r"c:\Users\jeshw_3agky5x\Downloads\Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf"

def upload_supply_pdf():
    """Upload the 2-1 supply PDF with intelligent merging"""
    
    print("🚀 Starting 2-1 Supply PDF Upload...")
    print(f"📄 PDF File: {PDF_PATH}")
    print(f"🌐 API Endpoint: {API_URL}/upload-supply-pdf")
    
    # Check if file exists
    if not os.path.exists(PDF_PATH):
        print("❌ ERROR: PDF file not found!")
        print(f"Expected location: {PDF_PATH}")
        print("Please check the file path and try again.")
        return False
    
    file_size = os.path.getsize(PDF_PATH) / (1024 * 1024)  # MB
    print(f"📊 File size: {file_size:.2f} MB")
    
    try:
        # Prepare the upload
        headers = {
            'X-API-Key': API_KEY
        }
        
        # Upload parameters
        data = {
            'format': 'jntuk'  # Assuming JNTUK format based on filename
        }
        
        print("\n🔄 Uploading and processing...")
        print("This will:")
        print("  ✓ Parse the supply PDF")
        print("  ✓ Find existing 2-1 regular results in Firebase")
        print("  ✓ Compare grades by subject code")
        print("  ✓ Replace F grades with better supply grades")
        print("  ✓ Track attempt counts for each subject")
        print("  ✓ Generate improvement report")
        
        # Open and upload the file
        with open(PDF_PATH, 'rb') as pdf_file:
            files = {'pdf': pdf_file}
            
            response = requests.post(
                f"{API_URL}/upload-supply-pdf",
                headers=headers,
                data=data,
                files=files,
                timeout=300  # 5 minute timeout for large files
            )
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Supply PDF processed successfully!")
            
            # Display statistics
            stats = result.get('stats', {})
            print(f"\n📊 Processing Statistics:")
            print(f"  📚 Total students processed: {stats.get('total_processed', 0)}")
            print(f"  🔄 Students updated: {stats.get('students_updated', 0)}")
            print(f"  ⬆️  Grades improved: {stats.get('grades_improved', 0)}")
            print(f"  📈 F→Better replacements: {stats.get('f_grade_improvements', 0)}")
            print(f"  🆕 New subjects added: {stats.get('new_subjects_added', 0)}")
            print(f"  ⏱️  Processing time: {stats.get('processing_time', 0):.2f}s")
            
            # Display improvements
            improvements = result.get('improvements', {})
            if improvements:
                print(f"\n🎯 Grade Improvements Summary:")
                for improvement_type, count in improvements.items():
                    if count > 0:
                        print(f"  {improvement_type}: {count}")
            
            # Firebase info
            firebase_info = result.get('firebase', {})
            if firebase_info.get('storage_url'):
                print(f"\n☁️  PDF stored in cloud: {firebase_info['storage_url']}")
            
            print(f"\n🎉 All done! Your 2-1 supply results have been intelligently merged.")
            print(f"Students who passed subjects in supply exams now have updated grades!")
            
            return True
            
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            try:
                error_info = response.json()
                print(f"Error: {error_info.get('error', 'Unknown error')}")
            except:
                print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Upload timed out. The file might be too large or the server is busy.")
        print("Try again in a few minutes.")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Please check your internet connection.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("📋 2-1 Supply PDF Upload Script")
    print("=" * 60)
    
    success = upload_supply_pdf()
    
    if success:
        print("\n" + "=" * 60)
        print("🎊 Upload completed successfully!")
        print("Your supply results are now merged with regular results.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("💥 Upload failed!")
        print("Please check the error messages above.")
        print("=" * 60)
