#!/usr/bin/env python3
"""
Comprehensive Firebase Connection Test
Tests Firestore, Storage, and Authentication
"""

import firebase_admin
from firebase_admin import credentials, firestore, storage
import json
import os
from datetime import datetime

def test_firebase_connection():
    """Comprehensive test of Firebase services"""
    print("🔥 FIREBASE CONNECTION TEST")
    print("=" * 60)
    
    results = {
        'service_account': False,
        'firebase_init': False,
        'firestore': False,
        'storage': False,
        'storage_bucket_exists': False,
        'data_exists': False,
        'pdfs_stored': False,
        'errors': []
    }
    
    # 1. Check service account file
    print("1️⃣ Checking Service Account...")
    try:
        if os.path.exists('serviceAccount.json'):
            with open('serviceAccount.json', 'r') as f:
                service_data = json.load(f)
            print(f"   ✅ Service account file found")
            print(f"   📧 Client email: {service_data.get('client_email', 'N/A')}")
            print(f"   🆔 Project ID: {service_data.get('project_id', 'N/A')}")
            results['service_account'] = True
        else:
            print("   ❌ Service account file not found")
            results['errors'].append("serviceAccount.json not found")
    except Exception as e:
        print(f"   ❌ Error reading service account: {e}")
        results['errors'].append(f"Service account error: {e}")
    
    # 2. Test Firebase initialization
    print("\n2️⃣ Testing Firebase Initialization...")
    try:
        # Clear any existing apps
        try:
            firebase_admin.delete_app(firebase_admin.get_app())
        except:
            pass
        
        if results['service_account']:
            cred = credentials.Certificate('serviceAccount.json')
            app = firebase_admin.initialize_app(cred, {
                'storageBucket': 'plant-ec218.firebasestorage.app'
            })
            print("   ✅ Firebase initialized successfully")
            results['firebase_init'] = True
        else:
            print("   ⏭️ Skipping - no service account")
    except Exception as e:
        print(f"   ❌ Firebase initialization failed: {e}")
        results['errors'].append(f"Firebase init error: {e}")
    
    # 3. Test Firestore
    print("\n3️⃣ Testing Firestore...")
    if results['firebase_init']:
        try:
            db = firestore.client()
            
            # Test write
            test_doc = db.collection('_connection_test').document('test')
            test_doc.set({
                'test': True,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'message': 'Connection test successful'
            })
            
            # Test read
            doc = test_doc.get()
            if doc.exists:
                print("   ✅ Firestore read/write successful")
                results['firestore'] = True
                
                # Clean up test document
                test_doc.delete()
                print("   🧹 Test document cleaned up")
            else:
                print("   ❌ Firestore read failed")
                results['errors'].append("Firestore read failed")
                
        except Exception as e:
            print(f"   ❌ Firestore test failed: {e}")
            results['errors'].append(f"Firestore error: {e}")
    else:
        print("   ⏭️ Skipping - Firebase not initialized")
    
    # 4. Test Storage
    print("\n4️⃣ Testing Firebase Storage...")
    if results['firebase_init']:
        try:
            bucket = storage.bucket()
            print(f"   📁 Storage bucket: {bucket.name}")
            
            # Test bucket access
            try:
                blobs = list(bucket.list_blobs(max_results=1))
                print("   ✅ Storage bucket accessible")
                results['storage'] = True
                results['storage_bucket_exists'] = True
                
                # Count total files
                all_blobs = list(bucket.list_blobs())
                pdf_count = sum(1 for blob in all_blobs if blob.name.lower().endswith('.pdf'))
                
                print(f"   📊 Total files in storage: {len(all_blobs)}")
                print(f"   📄 PDF files in storage: {pdf_count}")
                
                if pdf_count > 0:
                    results['pdfs_stored'] = True
                    print("   ✅ PDFs are stored in Firebase Storage")
                    
                    # Show sample PDFs
                    pdf_blobs = [blob for blob in all_blobs if blob.name.lower().endswith('.pdf')][:3]
                    for blob in pdf_blobs:
                        size_mb = blob.size / (1024 * 1024) if blob.size else 0
                        print(f"      📄 {blob.name} ({size_mb:.1f} MB)")
                else:
                    print("   ⚠️ No PDFs stored in Firebase Storage")
                    
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print(f"   ❌ Storage bucket does not exist: {bucket.name}")
                    results['errors'].append(f"Storage bucket {bucket.name} does not exist")
                else:
                    print(f"   ❌ Storage access failed: {e}")
                    results['errors'].append(f"Storage error: {e}")
                    
        except Exception as e:
            print(f"   ❌ Storage initialization failed: {e}")
            results['errors'].append(f"Storage init error: {e}")
    else:
        print("   ⏭️ Skipping - Firebase not initialized")
    
    # 5. Check existing data
    print("\n5️⃣ Checking Existing Data...")
    if results['firestore']:
        try:
            db = firestore.client()
            
            # Check student_results collection
            student_docs = list(db.collection('student_results').limit(5).stream())
            print(f"   📊 Student records found: {len(student_docs)}")
            
            if len(student_docs) > 0:
                results['data_exists'] = True
                print("   ✅ Student data exists in Firestore")
                
                # Sample data
                for doc in student_docs[:3]:
                    doc_data = doc.to_dict()
                    student_id = doc_data.get('student_id', 'N/A')
                    name = doc_data.get('student_name', doc_data.get('name', 'N/A'))
                    print(f"      🎓 {student_id} - {name}")
            else:
                print("   ⚠️ No student data found in Firestore")
                
        except Exception as e:
            print(f"   ❌ Data check failed: {e}")
            results['errors'].append(f"Data check error: {e}")
    else:
        print("   ⏭️ Skipping - Firestore not available")
    
    # 6. Summary
    print("\n" + "=" * 60)
    print("📊 FIREBASE CONNECTION SUMMARY")
    print("=" * 60)
    
    if results['service_account'] and results['firebase_init'] and results['firestore']:
        print("✅ Firebase is CONNECTED and working!")
        print("   🔥 Firestore: Connected")
        if results['storage_bucket_exists']:
            print("   📁 Storage: Connected")
            if results['pdfs_stored']:
                print("   📄 PDFs: Stored in Firebase Storage")
            else:
                print("   📄 PDFs: NOT stored in Firebase Storage")
        else:
            print("   📁 Storage: Bucket does not exist")
        
        if results['data_exists']:
            print("   📊 Data: Student records exist")
        else:
            print("   📊 Data: No student records found")
            
    elif results['service_account'] and results['firebase_init']:
        print("🟡 Firebase is PARTIALLY connected")
        print("   🔥 Firebase initialized but services have issues")
        if not results['firestore']:
            print("   ❌ Firestore: Not working")
        if not results['storage']:
            print("   ❌ Storage: Not working")
            
    else:
        print("❌ Firebase is NOT connected")
        if not results['service_account']:
            print("   ❌ Service account file missing or invalid")
        if not results['firebase_init']:
            print("   ❌ Firebase initialization failed")
    
    if results['errors']:
        print(f"\n🚨 Errors encountered ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"   ❌ {error}")
    
    # 7. Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if not results['service_account']:
        print("   1. Ensure serviceAccount.json file exists and is valid")
        print("   2. Download correct service account key from Firebase Console")
    elif not results['storage_bucket_exists']:
        print("   1. Create Firebase Storage bucket 'plant-ec218.appspot.com'")
        print("   2. Or update bucket name in Firebase configuration")
    elif not results['pdfs_stored']:
        print("   1. PDFs are stored locally but not in Firebase Storage")
        print("   2. Consider uploading PDFs to Firebase Storage for backup")
    elif not results['data_exists']:
        print("   1. No student data found - upload some PDF files to populate database")
        print("   2. Use the upload functionality to process PDF results")
    else:
        print("   ✅ Firebase is working perfectly!")
        print("   💡 You can upload PDFs and access student data")
    
    return results

if __name__ == "__main__":
    test_firebase_connection()
