#!/usr/bin/env python3
"""
Direct test of supply upload API
"""

import requests
import json

def test_supply_upload():
    """Test supply upload via API"""
    
    print("🧪 TESTING SUPPLY UPLOAD API")
    print("=" * 50)
    
    # Create a dummy test file (you can replace this with a real PDF path)
    test_file_path = "test_supply.txt"  # We'll create a dummy file
    
    # Create a dummy file for testing
    with open(test_file_path, 'w') as f:
        f.write("Test supply file content")
    
    # Test the API endpoint
    url = "http://127.0.0.1:5000/api/upload-result"
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'format': 'jntuk',
                'exam_type': 'supply'
            }
            
            print(f"📤 Sending request to {url}")
            print(f"📋 Data: {data}")
            
            response = requests.post(url, files=files, data=data)
            
            print(f"📨 Response status: {response.status_code}")
            print(f"📄 Response content: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload started successfully!")
                print(f"🆔 Upload ID: {result.get('upload_id')}")
                
                # Check progress
                upload_id = result.get('upload_id')
                if upload_id:
                    import time
                    time.sleep(2)  # Wait a bit
                    
                    progress_url = f"http://127.0.0.1:5000/api/upload-progress/{upload_id}"
                    progress_response = requests.get(progress_url)
                    
                    if progress_response.status_code == 200:
                        progress_data = progress_response.json()
                        print(f"📊 Progress data: {json.dumps(progress_data, indent=2)}")
                    else:
                        print(f"❌ Could not get progress: {progress_response.text}")
            else:
                print(f"❌ Upload failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing upload: {e}")
    
    finally:
        # Clean up test file
        import os
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    test_supply_upload()
