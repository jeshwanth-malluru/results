#!/usr/bin/env python3
"""
Check Firebase Storage to see if PDFs are stored there
"""

import firebase_admin
from firebase_admin import credentials, storage
import os

def check_firebase_storage():
    """Check if PDFs are stored in Firebase Storage"""
    print("🔍 Checking Firebase Storage for PDFs")
    print("=" * 50)
    
    try:
        # Initialize Firebase if not already done
        try:
            app = firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate('serviceAccount.json')
            app = firebase_admin.initialize_app(cred, {
                'storageBucket': 'plant-ec218.firebasestorage.app'
            })
        
        bucket = storage.bucket(app=app)
        
        # List all files in the bucket
        blobs = list(bucket.list_blobs())
        
        print(f"📁 Total files in Firebase Storage: {len(blobs)}")
        
        if len(blobs) == 0:
            print("❌ No files found in Firebase Storage")
            print("💡 PDFs are NOT stored in Firebase Storage")
            return
        
        pdf_files = []
        other_files = []
        
        for blob in blobs:
            if blob.name.lower().endswith('.pdf'):
                pdf_files.append(blob)
            else:
                other_files.append(blob)
        
        print(f"\n📄 PDF files: {len(pdf_files)}")
        print(f"📄 Other files: {len(other_files)}")
        
        if pdf_files:
            print("\n📋 PDF Files in Storage:")
            for i, pdf in enumerate(pdf_files[:10]):  # Show first 10
                size_mb = pdf.size / (1024 * 1024) if pdf.size else 0
                print(f"   📄 {pdf.name} ({size_mb:.1f} MB)")
                if i == 9 and len(pdf_files) > 10:
                    print(f"   ... and {len(pdf_files) - 10} more PDFs")
        else:
            print("❌ No PDF files found in Firebase Storage")
            print("💡 PDFs are NOT stored in Firebase Storage")
        
        if other_files:
            print(f"\n📁 Other files ({len(other_files)}):")
            for i, file in enumerate(other_files[:5]):  # Show first 5
                print(f"   📄 {file.name}")
                if i == 4 and len(other_files) > 5:
                    print(f"   ... and {len(other_files) - 5} more files")
        
        # Check if PDFs directory exists
        pdf_folder_exists = any(blob.name.startswith('pdfs/') for blob in blobs)
        print(f"\n📁 PDFs folder exists: {'✅ Yes' if pdf_folder_exists else '❌ No'}")
        
        return {
            'total_files': len(blobs),
            'pdf_files': len(pdf_files),
            'other_files': len(other_files),
            'pdf_folder_exists': pdf_folder_exists,
            'pdfs_stored': len(pdf_files) > 0
        }
        
    except FileNotFoundError:
        print("❌ serviceAccount.json not found")
        print("💡 Make sure Firebase credentials are configured")
        return None
    except Exception as e:
        print(f"❌ Error accessing Firebase Storage: {e}")
        return None

def check_local_pdfs():
    """Check for local PDF files in the workspace"""
    print("\n🔍 Checking Local PDF Files")
    print("=" * 50)
    
    pdf_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                size = os.path.getsize(full_path)
                size_mb = size / (1024 * 1024)
                pdf_files.append({
                    'path': full_path,
                    'name': file,
                    'size_mb': size_mb
                })
    
    print(f"📄 Local PDF files found: {len(pdf_files)}")
    
    if pdf_files:
        print("\n📋 Local PDF Files:")
        for pdf in pdf_files:
            print(f"   📄 {pdf['name']} ({pdf['size_mb']:.1f} MB)")
            print(f"      📁 {pdf['path']}")
    else:
        print("❌ No local PDF files found")
    
    return pdf_files

if __name__ == "__main__":
    storage_result = check_firebase_storage()
    local_pdfs = check_local_pdfs()
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if storage_result:
        if storage_result['pdfs_stored']:
            print("✅ PDFs ARE stored in Firebase Storage")
            print(f"   📄 Found {storage_result['pdf_files']} PDF files in Firebase")
        else:
            print("❌ PDFs are NOT stored in Firebase Storage")
            print("   💡 Firebase Storage is connected but contains no PDFs")
    else:
        print("❌ Cannot access Firebase Storage")
        print("   💡 Check Firebase configuration and credentials")
    
    if local_pdfs:
        print(f"📁 Found {len(local_pdfs)} local PDF files")
        print("   💡 Local PDFs exist but may not be uploaded to Firebase")
    else:
        print("📁 No local PDF files found")
    
    print("\n🔍 RECOMMENDATION:")
    if storage_result and not storage_result['pdfs_stored'] and local_pdfs:
        print("   ⚠️ Local PDFs found but not in Firebase Storage")
        print("   💡 Consider uploading PDFs to Firebase Storage for backup/access")
    elif not storage_result and local_pdfs:
        print("   ⚠️ Local PDFs found but Firebase Storage not accessible")
        print("   💡 Fix Firebase configuration to enable PDF storage")
    elif storage_result and storage_result['pdfs_stored']:
        print("   ✅ PDFs are properly stored in Firebase Storage")
    else:
        print("   ⚠️ No PDFs found locally or in Firebase Storage")
        print("   💡 Upload PDF files to process student results")
