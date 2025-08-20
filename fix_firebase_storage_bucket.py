#!/usr/bin/env python3
"""
Fix Firebase Storage Bucket Configuration
==========================================

This script attempts to fix the Firebase Storage bucket issue by:
1. Testing both possible bucket names
2. Creating the bucket if it doesn't exist
3. Updating configuration files consistently
"""

import json
import firebase_admin
from firebase_admin import credentials, storage, firestore
from google.cloud import storage as gcs
from google.api_core import exceptions

def test_bucket_access(bucket_name):
    """Test if a bucket exists and is accessible"""
    try:
        # Try to access the bucket
        bucket = storage.bucket(bucket_name)
        # Try to list files (this will fail if bucket doesn't exist)
        blobs = list(bucket.list_blobs(max_results=1))
        print(f"✅ Bucket '{bucket_name}' exists and is accessible")
        return True, bucket
    except Exception as e:
        print(f"❌ Bucket '{bucket_name}' error: {str(e)}")
        return False, None

def create_storage_bucket(project_id, bucket_name):
    """Create a Firebase Storage bucket"""
    try:
        # Initialize Google Cloud Storage client
        client = gcs.Client(project=project_id)
        
        # Create bucket
        bucket = client.bucket(bucket_name)
        bucket = client.create_bucket(bucket, location='us-central1')
        print(f"✅ Created bucket '{bucket_name}' successfully")
        return True
    except exceptions.Conflict:
        print(f"ℹ️ Bucket '{bucket_name}' already exists")
        return True
    except Exception as e:
        print(f"❌ Failed to create bucket '{bucket_name}': {str(e)}")
        return False

def main():
    print("🔧 FIREBASE STORAGE BUCKET FIX")
    print("=" * 50)
    
    # Initialize Firebase
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate('serviceAccount.json')
            firebase_admin.initialize_app(cred, {
                'storageBucket': 'plant-ec218.appspot.com'  # Default bucket
            })
        
        # Get project ID
        with open('serviceAccount.json', 'r') as f:
            service_account = json.load(f)
            project_id = service_account['project_id']
        
        print(f"📊 Project ID: {project_id}")
        
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        return
    
    # Test both bucket names
    bucket_names = [
        'plant-ec218.appspot.com',
        'plant-ec218.firebasestorage.app'
    ]
    
    working_bucket = None
    
    print("\n1️⃣ Testing existing buckets...")
    for bucket_name in bucket_names:
        success, bucket = test_bucket_access(bucket_name)
        if success:
            working_bucket = bucket_name
            break
    
    if not working_bucket:
        print("\n2️⃣ No working bucket found. Trying to create default bucket...")
        default_bucket = f"{project_id}.appspot.com"
        
        if create_storage_bucket(project_id, default_bucket):
            working_bucket = default_bucket
            print(f"✅ Using newly created bucket: {working_bucket}")
        else:
            print("❌ Failed to create storage bucket")
            return
    else:
        print(f"\n✅ Found working bucket: {working_bucket}")
    
    print("\n3️⃣ Testing bucket upload...")
    try:
        bucket = storage.bucket(working_bucket)
        
        # Test upload with a small test file
        test_content = "Firebase Storage test file"
        blob = bucket.blob('test/connection_test.txt')
        blob.upload_from_string(test_content, content_type='text/plain')
        
        # Test download
        downloaded_content = blob.download_as_text()
        
        if downloaded_content == test_content:
            print("✅ Upload/download test successful")
            
            # Clean up test file
            blob.delete()
            print("🧹 Test file cleaned up")
        else:
            print("❌ Upload/download test failed")
            
    except Exception as e:
        print(f"❌ Storage test failed: {e}")
        return
    
    print("\n4️⃣ Updating configuration files...")
    
    # Files to update with correct bucket name
    config_updates = [
        {
            'file': 'app.py',
            'old_patterns': [
                "'storageBucket': 'plant-ec218.appspot.com'",
                '"storageBucket": "plant-ec218.appspot.com"'
            ],
            'new_pattern': f"'storageBucket': '{working_bucket}'"
        },
        {
            'file': 'comprehensive_firebase_test.py',
            'old_patterns': [
                "'storageBucket': 'plant-ec218.appspot.com'"
            ],
            'new_pattern': f"'storageBucket': '{working_bucket}'"
        },
        {
            'file': 'check_firebase_storage.py',
            'old_patterns': [
                "'storageBucket': 'plant-ec218.appspot.com'"
            ],
            'new_pattern': f"'storageBucket': '{working_bucket}'"
        }
    ]
    
    for config in config_updates:
        try:
            with open(config['file'], 'r') as f:
                content = f.read()
            
            updated = False
            for old_pattern in config['old_patterns']:
                if old_pattern in content:
                    content = content.replace(old_pattern, config['new_pattern'])
                    updated = True
            
            if updated:
                with open(config['file'], 'w') as f:
                    f.write(content)
                print(f"✅ Updated {config['file']}")
            else:
                print(f"ℹ️ No updates needed for {config['file']}")
                
        except FileNotFoundError:
            print(f"⚠️ File not found: {config['file']}")
        except Exception as e:
            print(f"❌ Error updating {config['file']}: {e}")
    
    print(f"\n🎉 FIREBASE STORAGE SETUP COMPLETE!")
    print(f"✅ Working bucket: {working_bucket}")
    print("✅ Configuration files updated")
    print("\n💡 Now test your autonomous PDF upload again!")

if __name__ == "__main__":
    main()
