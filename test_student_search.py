#!/usr/bin/env python3
"""
Test script for student search API endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000"
SAMPLE_STUDENT_IDS = [
    "17B81A0106",  # From actual Firebase data
    "17B81A0126", 
    "17B81A0130",
    "17B81A0136",
    "24B81A0101",  # Test newer format
    "INVALID_ID"   # Test invalid ID
]

def test_student_search_api():
    """Test the Firebase-based student search API"""
    print("🧪 Testing Student Search API")
    print("=" * 50)
    
    for student_id in SAMPLE_STUDENT_IDS:
        print(f"\n🔍 Testing student ID: {student_id}")
        
        try:
            # Test basic search
            url = f"{BASE_URL}/api/students/{student_id}/results"
            response = requests.get(url, timeout=10)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"✅ Found {count} results for {student_id}")
                
                if count > 0:
                    # Show first result details
                    first_result = data['results'][0]
                    print(f"   📝 Student Name: {first_result.get('student_name', 'N/A')}")
                    print(f"   📅 Semester: {first_result.get('semester', 'N/A')}")
                    print(f"   🎓 Year: {first_result.get('year', 'N/A')}")
                    print(f"   📈 SGPA: {first_result.get('sgpa', first_result.get('grades', {}).get('sgpa', 'N/A'))}")
                else:
                    print(f"   ℹ️ No results found for {student_id}")
                    
            elif response.status_code == 503:
                print("❌ Firebase not available")
                break
            else:
                data = response.json()
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Response text: {response.text[:200]}")
    
    print(f"\n{'=' * 50}")
    print("🏁 Student Search API Test Complete")

def test_search_with_filters():
    """Test search with filters"""
    print("\n🔧 Testing Search with Filters")
    print("=" * 50)
    
    student_id = "24B81A0101"  # Use a known student ID
    
    filters = [
        {"semester": "Semester 1"},
        {"year": "1 Year"},
        {"exam_type": "regular"},
        {"semester": "Semester 1", "year": "1 Year"},
    ]
    
    for filter_set in filters:
        print(f"\n🔍 Testing with filters: {filter_set}")
        
        try:
            url = f"{BASE_URL}/api/students/{student_id}/results"
            response = requests.get(url, params=filter_set, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                print(f"✅ Found {count} results with filters")
            else:
                data = response.json()
                print(f"❌ Error: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

def test_frontend_pages():
    """Test if frontend pages load correctly"""
    print("\n🌐 Testing Frontend Pages")
    print("=" * 50)
    
    pages = [
        ("/admin", "Admin Login"),
        ("/student-search", "Student Search"),
        ("/admin/dashboard", "Admin Dashboard"),
        ("/upload", "Upload Page")
    ]
    
    for url, name in pages:
        try:
            response = requests.get(f"{BASE_URL}{url}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: OK")
            else:
                print(f"❌ {name}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")

if __name__ == "__main__":
    print("🚀 Starting API Tests")
    print("🌐 Base URL:", BASE_URL)
    
    # Test API endpoints
    test_student_search_api()
    
    # Test with filters
    test_search_with_filters()
    
    # Test frontend pages
    test_frontend_pages()
    
    print("\n🎯 All tests completed!")
