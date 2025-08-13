#!/usr/bin/env python3
"""
Demo script to test the student search duplicate removal functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

def test_student_search_duplicates():
    """Test the student search API with duplicate removal"""
    print("🧪 Testing Student Search Duplicate Removal")
    print("=" * 50)
    
    # Test student ID (using a real ID from the database)
    test_student_id = "17B81A0106"
    
    print(f"🔍 Searching for student: {test_student_id}")
    print()
    
    # Test 1: Detailed view (show all records)
    print("📊 TEST 1: Detailed View (Show All Records)")
    try:
        response = requests.get(f"{BASE_URL}/api/students/search", params={
            'student_id': test_student_id,
            'deduplicate': 'false',
            'limit': 50
        })
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"   ✅ Found {len(results)} records")
            for i, record in enumerate(results, 1):
                print(f"   Record {i}:")
                print(f"      - Student ID: {record.get('student_id')}")
                print(f"      - Semester: {record.get('semester')}")
                print(f"      - Exam Type: {record.get('examType', record.get('exam_type'))}")
                print(f"      - SGPA: {record.get('sgpa')}")
                print(f"      - Subjects: {len(record.get('subjectGrades', []))}")
                print(f"      - Upload Date: {record.get('upload_date')}")
                print()
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("-" * 50)
    
    # Test 2: Consolidated view (remove duplicates)
    print("📊 TEST 2: Consolidated View (Remove Duplicates)")
    try:
        response = requests.get(f"{BASE_URL}/api/students/search", params={
            'student_id': test_student_id,
            'deduplicate': 'true',
            'limit': 50
        })
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"   ✅ Found {len(results)} consolidated record(s)")
            for i, record in enumerate(results, 1):
                print(f"   Consolidated Record {i}:")
                print(f"      - Student ID: {record.get('student_id')}")
                print(f"      - Semester: {record.get('semester')}")
                print(f"      - Is Consolidated: {record.get('consolidatedRecord', False)}")
                print(f"      - Record Count: {record.get('recordCount', 1)}")
                print(f"      - All Semesters: {record.get('allSemesters', [])}")
                print(f"      - All Exam Types: {record.get('allExamTypes', [])}")
                print(f"      - Consolidated SGPA: {record.get('consolidatedSGPA')}")
                print(f"      - Total Subjects: {record.get('totalSubjects')}")
                print(f"      - Total Credits: {record.get('totalCredits')}")
                print(f"      - Duplicates Removed: {record.get('duplicatesRemoved', 0)}")
                print(f"      - Last Updated: {record.get('lastUpdated')}")
                
                # Show semester data
                semester_data = record.get('semesterData', [])
                if semester_data:
                    print(f"      - Semester Breakdown:")
                    for sem in semester_data:
                        print(f"        * {sem.get('semester')} ({sem.get('exam_type')}): SGPA {sem.get('sgpa')}")
                
                print()
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    print("=" * 50)
    print("🎯 How to Use:")
    print("1. 📱 Web Interface: http://127.0.0.1:5000/student-search")
    print("2. 🔍 Enter a student ID in the search box")
    print("3. 📋 Choose 'Consolidated' to remove duplicates")
    print("4. 📋 Choose 'Detailed' to see all individual records")
    print("5. 🔍 Search automatically as you type (8+ characters)")
    print()
    print("🚀 Benefits of Consolidated View:")
    print("   ✅ No duplicate records")
    print("   ✅ Combined subject data from all semesters")
    print("   ✅ Average SGPA calculation")
    print("   ✅ Complete academic history")
    print("   ✅ Clean, organized display")

def test_general_search():
    """Test general search functionality"""
    print()
    print("🔍 Testing General Search Features")
    print("=" * 50)
    
    # Test search by semester
    print("📊 Testing search by semester...")
    try:
        response = requests.get(f"{BASE_URL}/api/students/search", params={
            'semester': 'Semester 1',
            'deduplicate': 'true',
            'limit': 5
        })
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"   ✅ Found {len(results)} students in Semester 1")
        else:
            print(f"   ⚠️ No students found or API error")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test search by exam type
    print("📊 Testing search by exam type...")
    try:
        response = requests.get(f"{BASE_URL}/api/students/search", params={
            'exam_type': 'regular',
            'deduplicate': 'true',
            'limit': 5
        })
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"   ✅ Found {len(results)} students with regular exams")
        else:
            print(f"   ⚠️ No students found or API error")
            
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    print("🎓 Student Search Duplicate Removal Demo")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/api/firebase-status", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            test_student_search_duplicates()
            test_general_search()
        else:
            print("❌ Server responded with error")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the Flask app first:")
        print("   python app.py")
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
