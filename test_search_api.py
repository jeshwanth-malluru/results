#!/usr/bin/env python3
"""
Test Updated Search API
Test if the updated search API now returns supply grades correctly
"""

import requests
import json

def test_search_api():
    """Test the search API with a student who should have supply grades"""
    
    # Test with the local server (adjust URL if needed)
    base_url = "http://127.0.0.1:5000"  # Change to your server URL
    
    # Test parameters - search for a student with known supply improvements
    test_params = {
        'student_id': '24485A0501',  # Replace with actual student ID
        'deduplicate': 'true'
    }
    
    print("🧪 Testing Search API for Supply Grade Display")
    print("=" * 60)
    
    try:
        # Make API request
        response = requests.get(f"{base_url}/api/students/search", params=test_params)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            
            print(f"✅ API Response: {response.status_code}")
            print(f"📊 Results found: {len(results)}")
            
            if results:
                for i, result in enumerate(results):
                    print(f"\n📄 Result #{i+1}:")
                    print(f"   Student ID: {result.get('student_id', 'Unknown')}")
                    print(f"   Student Name: {result.get('student_name', 'Unknown')}")
                    print(f"   Semester: {result.get('semester', 'Unknown')}")
                    print(f"   Exam Type: {result.get('examType', 'Unknown')}")
                    print(f"   Perfect Merge Applied: {result.get('perfectMergeApplied', False)}")
                    print(f"   Has Supply Attempts: {result.get('hasSupplyAttempts', False)}")
                    
                    # Check subjects
                    subjects = result.get('subjects', [])
                    subject_grades = result.get('subjectGrades', [])
                    
                    print(f"   📚 Subjects: {len(subjects)} (subjects field)")
                    print(f"   📚 Subject Grades: {len(subject_grades)} (subjectGrades field)")
                    
                    # Look for key subjects like ADS
                    key_subjects = ['R232112', 'R2321052', 'R2321054']
                    
                    for subject in (subjects or subject_grades):
                        subject_code = (subject.get('subject_code', '') or 
                                      subject.get('code', '') or 
                                      subject.get('subjectCode', ''))
                        
                        if any(code in subject_code for code in key_subjects):
                            grade = subject.get('grade', 'Unknown')
                            result_status = subject.get('result', 'Unknown')
                            exam_type = subject.get('exam_type', 'Unknown')
                            attempts = subject.get('attempts', 1)
                            original_grade = subject.get('original_grade', None)
                            
                            print(f"   🎯 {subject_code}: {grade} ({result_status}) [{exam_type}] - Attempts: {attempts}")
                            if original_grade:
                                print(f"      🔄 Original: {original_grade} → Current: {grade}")
                            
                            # Check if this shows improvement
                            if original_grade and original_grade == 'F' and grade != 'F':
                                print(f"      ✅ SUPPLY IMPROVEMENT DETECTED: F → {grade}")
                            elif grade == 'F':
                                print(f"      ❌ Still showing F grade")
                
            else:
                print("❌ No results found for the test student ID")
        
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the Flask app is running.")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_direct_api_call():
    """Test a direct API call to check the response structure"""
    print("\n🔧 Direct API Structure Test")
    print("=" * 40)
    
    # You can also test with curl command
    curl_command = """
curl -X GET "http://127.0.0.1:5000/api/students/search?student_id=24485A0501&deduplicate=true"
"""
    
    print("📋 Equivalent curl command:")
    print(curl_command.strip())
    
    print("\n💡 Expected Behavior:")
    print("   1. Should return 1 consolidated record")
    print("   2. Should show 'subjects' and 'subjectGrades' fields")
    print("   3. Supply improved subjects should show current grade (A, B, C, D, E)")
    print("   4. Should have 'original_grade' field showing the old F grade")
    print("   5. 'exam_type' should be 'SUPPLY' for improved subjects")

if __name__ == "__main__":
    test_search_api()
    test_direct_api_call()
