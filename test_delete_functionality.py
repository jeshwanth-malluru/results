#!/usr/bin/env python3
"""
Test PDF Delete Functionality
Test the delete endpoints for removing PDF data from local storage and Firebase
"""

import requests
import json

def test_delete_functionality():
    """Test the PDF delete functionality"""
    
    # Base URL (adjust if needed)
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing PDF Delete Functionality")
    print("=" * 50)
    
    # First, get list of available data files
    print("📋 Step 1: Getting list of data files...")
    try:
        response = requests.get(f"{base_url}/data-files")
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            
            print(f"✅ Found {len(files)} data files:")
            for i, file in enumerate(files[:5]):  # Show first 5 files
                metadata = file.get('metadata', {})
                print(f"   {i+1}. {file['filename']}")
                print(f"      - Students: {metadata.get('total_students', 0)}")
                print(f"      - Year: {metadata.get('year', 'Unknown')}")
                print(f"      - Exam Type: {metadata.get('exam_type', 'regular')}")
                print(f"      - Size: {file.get('size', 0)} bytes")
            
            if files:
                # Test delete with the first file (uncomment to actually test)
                test_filename = files[0]['filename']
                print(f"\n🎯 Test file selected: {test_filename}")
                print(f"⚠️ To test delete functionality, uncomment the delete test code below")
                
                # Uncomment the lines below to actually test deletion
                # WARNING: This will permanently delete data!
                
                # print(f"🗑️ Step 2: Testing delete for {test_filename}...")
                # confirm = input(f"Are you sure you want to delete {test_filename}? (yes/no): ")
                # 
                # if confirm.lower() == 'yes':
                #     delete_response = requests.delete(f"{base_url}/data-files/{test_filename}")
                #     
                #     if delete_response.status_code == 200:
                #         result = delete_response.json()
                #         print(f"✅ Delete successful!")
                #         print(f"   Local file deleted: {result['details']['local_file_deleted']}")
                #         print(f"   Firebase records deleted: {result['details']['firebase_records_deleted']}")
                #         if result['details']['firebase_errors']:
                #             print(f"   Firebase errors: {len(result['details']['firebase_errors'])}")
                #     else:
                #         print(f"❌ Delete failed: {delete_response.status_code}")
                #         print(f"   Response: {delete_response.text}")
                # else:
                #     print("🛑 Delete cancelled by user")
                
            else:
                print("📁 No data files found to test deletion")
        else:
            print(f"❌ Failed to get data files: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_delete_by_upload_id():
    """Test deletion by upload ID"""
    print("\n🔍 Testing delete by upload ID...")
    
    # Example upload ID (replace with actual ID)
    test_upload_id = "upload_20250814_123456"
    
    base_url = "http://127.0.0.1:5000"
    
    print(f"🎯 Test upload ID: {test_upload_id}")
    print(f"⚠️ To test delete by upload ID, uncomment the code below")
    
    # Uncomment to test
    # try:
    #     response = requests.delete(f"{base_url}/api/delete-upload/{test_upload_id}")
    #     
    #     if response.status_code == 200:
    #         result = response.json()
    #         print(f"✅ Delete by upload ID successful!")
    #         print(f"   Firebase records deleted: {result['details']['firebase_records_deleted']}")
    #         print(f"   Local files deleted: {result['details']['local_files_deleted']}")
    #     else:
    #         print(f"❌ Delete failed: {response.status_code}")
    #         print(f"   Response: {response.text}")
    #         
    # except Exception as e:
    #     print(f"❌ Error: {e}")

def demo_api_endpoints():
    """Demonstrate the available API endpoints"""
    print("\n📡 Available API Endpoints for PDF Data Management:")
    print("=" * 60)
    
    endpoints = [
        {
            "method": "GET",
            "url": "/data-files",
            "description": "List all PDF data files with metadata"
        },
        {
            "method": "GET", 
            "url": "/data-files/<filename>",
            "description": "Get specific PDF data file content"
        },
        {
            "method": "DELETE",
            "url": "/data-files/<filename>",
            "description": "Delete PDF data file (local + Firebase)"
        },
        {
            "method": "DELETE",
            "url": "/api/delete-upload/<upload_id>",
            "description": "Delete all data by upload ID"
        },
        {
            "method": "GET",
            "url": "/pdf-data-management",
            "description": "Web interface for managing PDF data"
        }
    ]
    
    for endpoint in endpoints:
        print(f"🔹 {endpoint['method']} {endpoint['url']}")
        print(f"   📝 {endpoint['description']}")
        print()

def demo_javascript_usage():
    """Show JavaScript examples for frontend integration"""
    print("\n💻 JavaScript Examples for Frontend Integration:")
    print("=" * 50)
    
    js_examples = """
// Delete a PDF data file
async function deletePdfData(filename) {
    if (!confirm(`Delete ${filename}? This will remove local and Firebase data!`)) {
        return;
    }
    
    try {
        const response = await fetch(`/data-files/${filename}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`Deleted successfully! Firebase records: ${result.details.firebase_records_deleted}`);
            window.location.reload(); // Refresh the page
        } else {
            alert('Delete failed: ' + result.error);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

// Delete by upload ID
async function deleteByUploadId(uploadId) {
    try {
        const response = await fetch(`/api/delete-upload/${uploadId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('Deleted:', result.details);
        }
    } catch (error) {
        console.error('Delete error:', error);
    }
}

// Load and display data files
async function loadDataFiles() {
    try {
        const response = await fetch('/data-files');
        const data = await response.json();
        
        data.files.forEach(file => {
            console.log(`File: ${file.filename}, Students: ${file.metadata.total_students}`);
        });
    } catch (error) {
        console.error('Load error:', error);
    }
}
"""
    
    print(js_examples)

if __name__ == "__main__":
    test_delete_functionality()
    test_delete_by_upload_id()
    demo_api_endpoints()
    demo_javascript_usage()
    
    print("\n🎯 Summary:")
    print("1. ✅ Delete endpoints added to app.py")
    print("2. ✅ PDF data management web interface created")
    print("3. ✅ Dashboard navigation updated")
    print("4. ⚠️ Test deletion carefully - it permanently removes data!")
    print("5. 🌐 Access the management interface at: http://localhost:5000/pdf-data-management")
