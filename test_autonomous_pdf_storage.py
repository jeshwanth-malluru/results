#!/usr/bin/env python3
"""
Test Autonomous PDF Upload to Firebase Storage
==============================================

This script tests the autonomous PDF upload functionality to ensure
that PDFs are properly stored in Firebase Storage.
"""

import os
import tempfile
import firebase_admin
from firebase_admin import credentials, storage
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_autonomous_pdf_storage():
    """Test the autonomous PDF storage functionality"""
    print("🧪 TESTING AUTONOMOUS PDF STORAGE")
    print("=" * 50)
    
    # Initialize Firebase if not already done
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate('serviceAccount.json')
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'plant-ec218.firebasestorage.app'
            })
        
        bucket = storage.bucket()
        print(f"✅ Firebase initialized with bucket: {bucket.name}")
        
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        return False
    
    # Test PDF files in current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if not pdf_files:
        print("⚠️ No PDF files found in current directory")
        return False
    
    # Test with the first PDF found
    test_pdf = pdf_files[0]
    print(f"📄 Testing with PDF: {test_pdf}")
    
    try:
        # Simulate the upload process from the app
        storage_filename = f"test_autonomous/test_upload_{test_pdf}"
        
        with open(test_pdf, 'rb') as pdf_file:
            print("📤 Uploading PDF to Firebase Storage...")
            
            # Upload the file
            blob = bucket.blob(storage_filename)
            content = pdf_file.read()
            blob.upload_from_string(content, content_type='application/pdf')
            
            # Make it publicly accessible (like in the app)
            blob.make_public()
            
            print(f"✅ PDF uploaded successfully!")
            print(f"📁 Storage path: {storage_filename}")
            print(f"🔗 Public URL: {blob.public_url}")
            
            # Verify the upload by trying to download
            print("🔍 Verifying upload...")
            downloaded_content = blob.download_as_bytes()
            
            if len(downloaded_content) == len(content):
                print("✅ Upload verification successful!")
                print(f"📊 File size: {len(content)} bytes")
            else:
                print("❌ Upload verification failed - size mismatch")
                return False
            
            # Clean up test file
            print("🧹 Cleaning up test file...")
            blob.delete()
            print("✅ Test file deleted")
            
            return True
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

def check_existing_pdfs():
    """Check existing PDFs in Firebase Storage"""
    print("\n📁 CHECKING EXISTING PDFS IN FIREBASE STORAGE")
    print("=" * 50)
    
    try:
        bucket = storage.bucket()
        
        # List all blobs (files) in the bucket
        blobs = list(bucket.list_blobs())
        pdf_blobs = [blob for blob in blobs if blob.name.endswith('.pdf')]
        
        print(f"📊 Total files in storage: {len(blobs)}")
        print(f"📄 PDF files found: {len(pdf_blobs)}")
        
        if pdf_blobs:
            print("\n📄 PDF Files in Storage:")
            for blob in pdf_blobs[:10]:  # Show first 10
                size_mb = blob.size / (1024 * 1024) if blob.size else 0
                print(f"   📄 {blob.name} ({size_mb:.2f} MB)")
            
            if len(pdf_blobs) > 10:
                print(f"   ... and {len(pdf_blobs) - 10} more PDFs")
        else:
            print("⚠️ No PDF files found in Firebase Storage")
        
        return len(pdf_blobs) > 0
        
    except Exception as e:
        print(f"❌ Error checking existing PDFs: {e}")
        return False

def main():
    """Main test function"""
    print("🔥 FIREBASE STORAGE PDF TEST")
    print("=" * 50)
    
    # Check existing PDFs
    has_existing_pdfs = check_existing_pdfs()
    
    # Test new upload
    upload_success = test_autonomous_pdf_storage()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if has_existing_pdfs:
        print("✅ Firebase Storage has existing PDFs")
    else:
        print("⚠️ No existing PDFs found in Firebase Storage")
    
    if upload_success:
        print("✅ PDF upload test successful")
        print("✅ Autonomous PDF storage is WORKING!")
    else:
        print("❌ PDF upload test failed")
        print("❌ There's an issue with autonomous PDF storage")
    
    print("\n💡 RECOMMENDATIONS:")
    if upload_success:
        print("   ✅ Your Firebase Storage is correctly configured")
        print("   ✅ Autonomous PDF uploads should work in your app")
    else:
        print("   🔧 Check Firebase Storage permissions")
        print("   🔧 Verify service account has Storage Admin role")
        print("   🔧 Check if storage bucket exists and is accessible")

if __name__ == "__main__":
    main()
