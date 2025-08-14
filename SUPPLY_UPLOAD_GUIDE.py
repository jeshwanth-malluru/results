#!/usr/bin/env python3
"""
Complete Guide: How to Upload Supply PDFs
Shows all the different ways to upload and process supply PDFs with smart merge
"""

def show_api_endpoints():
    """Show the available API endpoints for supply processing"""
    print("🌐 SUPPLY PDF UPLOAD API ENDPOINTS")
    print("=" * 60)
    
    print("\n📡 1. MAIN SUPPLY UPLOAD ENDPOINT")
    print("   URL: /upload-supply-pdf")
    print("   Method: POST")
    print("   Content-Type: multipart/form-data")
    print("   Authentication: X-API-Key header required")
    
    print("\n📋 Required Parameters:")
    print("   - pdf: [File] Supply PDF file")
    print("   - format: [String] 'jntuk' or 'autonomous'")
    
    print("\n📊 Optional Parameters:")
    print("   - None (auto-detects everything from PDF)")

def show_curl_examples():
    """Show curl command examples"""
    print("\n\n💻 CURL COMMAND EXAMPLES")
    print("=" * 60)
    
    print("\n🔧 1. Upload JNTUK Supply PDF:")
    print("""
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" \\
  -H "X-API-Key: your-api-key-here" \\
  -F "pdf=@BTECH_2-1_SUPPLY_FEB_2025.pdf" \\
  -F "format=jntuk"
    """)
    
    print("\n🔧 2. Upload Autonomous Supply PDF:")
    print("""
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" \\
  -H "X-API-Key: your-api-key-here" \\
  -F "pdf=@Autonomous_Supply_Results.pdf" \\
  -F "format=autonomous"
    """)
    
    print("\n🔧 3. Local Testing:")
    print("""
curl -X POST "http://localhost:5000/upload-supply-pdf" \\
  -H "X-API-Key: your-api-key-here" \\
  -F "pdf=@supply_results.pdf" \\
  -F "format=jntuk"
    """)

def show_javascript_examples():
    """Show JavaScript/Frontend examples"""
    print("\n\n🌐 JAVASCRIPT/FRONTEND EXAMPLES")
    print("=" * 60)
    
    print("\n📝 1. HTML Form:")
    print("""
<form id="supplyUploadForm" enctype="multipart/form-data">
    <div>
        <label for="pdfFile">Supply PDF File:</label>
        <input type="file" id="pdfFile" name="pdf" accept=".pdf" required>
    </div>
    
    <div>
        <label for="format">Format:</label>
        <select id="format" name="format" required>
            <option value="jntuk">JNTUK</option>
            <option value="autonomous">Autonomous</option>
        </select>
    </div>
    
    <button type="submit">Upload Supply PDF</button>
    <div id="uploadStatus"></div>
    <div id="results"></div>
</form>
    """)
    
    print("\n🔥 2. JavaScript Upload Function:")
    print("""
async function uploadSupplyPDF() {
    const form = document.getElementById('supplyUploadForm');
    const formData = new FormData(form);
    const statusDiv = document.getElementById('uploadStatus');
    const resultsDiv = document.getElementById('results');
    
    try {
        statusDiv.innerHTML = '⏳ Uploading and processing supply PDF...';
        
        const response = await fetch('/upload-supply-pdf', {
            method: 'POST',
            headers: {
                'X-API-Key': 'your-api-key-here'
            },
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            statusDiv.innerHTML = '✅ Supply PDF processed successfully!';
            
            // Show detailed results
            const stats = result.stats;
            const improvements = result.improvements;
            
            resultsDiv.innerHTML = `
                <h3>📊 Processing Results</h3>
                <p><strong>Students Processed:</strong> ${stats.total_processed}</p>
                <p><strong>Students Updated:</strong> ${stats.students_updated}</p>
                <p><strong>Subjects Overwritten:</strong> ${stats.subjects_overwritten}</p>
                <p><strong>Subjects Added:</strong> ${stats.subjects_added}</p>
                <p><strong>Total Attempts Tracked:</strong> ${stats.total_attempts_tracked}</p>
                
                <h4>🎉 Grade Improvements:</h4>
                <ul>
                    ${improvements.grade_improvements.map(imp => 
                        `<li>${imp.student_id} - ${imp.subject_code}: ${imp.from_grade} → ${imp.to_grade} (Attempt #${imp.attempt_number})</li>`
                    ).join('')}
                </ul>
            `;
        } else {
            statusDiv.innerHTML = `❌ Error: ${result.error || 'Upload failed'}`;
        }
    } catch (error) {
        statusDiv.innerHTML = `❌ Network error: ${error.message}`;
    }
}

// Attach event listener
document.getElementById('supplyUploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    uploadSupplyPDF();
});
    """)

def show_python_examples():
    """Show Python script examples"""
    print("\n\n🐍 PYTHON SCRIPT EXAMPLES")
    print("=" * 60)
    
    print("\n📝 1. Simple Upload Script:")
    print("""
import requests
import json

def upload_supply_pdf(pdf_path, format_type, api_key):
    url = "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf"
    
    with open(pdf_path, 'rb') as pdf_file:
        files = {'pdf': pdf_file}
        data = {'format': format_type}
        headers = {'X-API-Key': api_key}
        
        print(f"📤 Uploading {pdf_path}...")
        response = requests.post(url, files=files, data=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            print(f"📊 Students processed: {result['stats']['total_processed']}")
            print(f"🔄 Students updated: {result['stats']['students_updated']}")
            print(f"📈 Subjects overwritten: {result['stats']['subjects_overwritten']}")
            return result
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None

# Usage
if __name__ == "__main__":
    result = upload_supply_pdf(
        pdf_path="supply_results.pdf",
        format_type="jntuk",
        api_key="your-api-key-here"
    )
    """)
    
    print("\n📝 2. Advanced Upload with Progress:")
    print("""
import requests
import json
import time

class SupplyPDFUploader:
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url or "https://student-result-backend-390507264435.us-central1.run.app"
    
    def upload_supply_pdf(self, pdf_path, format_type):
        print(f"🎯 Starting supply PDF upload: {pdf_path}")
        print(f"📋 Format: {format_type}")
        
        url = f"{self.base_url}/upload-supply-pdf"
        
        with open(pdf_path, 'rb') as pdf_file:
            files = {'pdf': pdf_file}
            data = {'format': format_type}
            headers = {'X-API-Key': self.api_key}
            
            start_time = time.time()
            response = requests.post(url, files=files, data=data, headers=headers)
            upload_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                self._show_success_results(result, upload_time)
                return result
            else:
                self._show_error(response)
                return None
    
    def _show_success_results(self, result, upload_time):
        print(f"\\n✅ SUPPLY PDF PROCESSED SUCCESSFULLY!")
        print(f"⏱️ Upload time: {upload_time:.2f} seconds")
        print(f"⚡ Processing time: {result.get('result', {}).get('processing_time', 0):.2f} seconds")
        
        stats = result.get('stats', {})
        print(f"\\n📊 PROCESSING STATISTICS:")
        print(f"   👥 Students processed: {stats.get('total_processed', 0)}")
        print(f"   ✅ Students found in Firebase: {stats.get('students_found_in_firebase', 0)}")
        print(f"   ❌ Students not found: {stats.get('students_not_found', 0)}")
        print(f"   🔄 Students updated: {stats.get('students_updated', 0)}")
        print(f"   📈 Subjects overwritten: {stats.get('subjects_overwritten', 0)}")
        print(f"   ➕ Subjects added: {stats.get('subjects_added', 0)}")
        print(f"   🔢 Total attempts tracked: {stats.get('total_attempts_tracked', 0)}")
        
        improvements = result.get('improvements', {}).get('grade_improvements', [])
        if improvements:
            print(f"\\n🎉 GRADE IMPROVEMENTS:")
            for imp in improvements:
                print(f"   {imp['student_id']} - {imp['subject_code']}: {imp['from_grade']} → {imp['to_grade']} (Attempt #{imp['attempt_number']})")
    
    def _show_error(self, response):
        print(f"❌ UPLOAD FAILED!")
        print(f"Status Code: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error: {error_data.get('error', 'Unknown error')}")
        except:
            print(f"Raw Error: {response.text}")
    
    def get_improvement_report(self, days=30, format_filter=None):
        url = f"{self.base_url}/api/supply-improvement-report"
        params = {'days': days}
        if format_filter:
            params['format'] = format_filter
        
        headers = {'X-API-Key': self.api_key}
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Failed to get improvement report: {response.status_code}")
            return None

# Usage
uploader = SupplyPDFUploader("your-api-key-here")

# Upload supply PDF
result = uploader.upload_supply_pdf("supply_results.pdf", "jntuk")

# Get improvement report
report = uploader.get_improvement_report(days=60, format_filter="jntuk")
if report:
    print(f"\\n📈 IMPROVEMENT REPORT:")
    print(json.dumps(report, indent=2))
    """)

def show_local_testing():
    """Show how to test locally"""
    print("\n\n🔧 LOCAL TESTING")
    print("=" * 60)
    
    print("\n📝 1. Start Local Server:")
    print("""
# In your backend directory
cd "c:\\Users\\jeshw_3agky5x\\Desktop\\student-result-project\\Result-Analysis\\backend"

# Run the Flask app
python app.py

# Server will start at http://localhost:5000
    """)
    
    print("\n📝 2. Test with Postman:")
    print("""
POST http://localhost:5000/upload-supply-pdf

Headers:
- X-API-Key: your-api-key
- Content-Type: multipart/form-data

Body (form-data):
- pdf: [Choose File] supply_results.pdf
- format: jntuk
    """)
    
    print("\n📝 3. Test with Python locally:")
    print("""
from batch_pdf_processor import process_supply_pdf_with_smart_merge

# Direct function call (bypass API)
result = process_supply_pdf_with_smart_merge(
    pdf_path="supply_results.pdf",
    format_type="jntuk",
    original_filename="supply_results.pdf"
)

print("Result:", result)
    """)

def show_response_examples():
    """Show example API responses"""
    print("\n\n📡 API RESPONSE EXAMPLES")
    print("=" * 60)
    
    print("\n✅ 1. Successful Upload Response:")
    print("""
{
  "message": "Successfully processed supply results with smart merge.",
  "result": {
    "status": "success",
    "stats": {
      "total_processed": 150,
      "students_found_in_firebase": 140,
      "students_not_found": 10,
      "students_updated": 125,
      "subjects_overwritten": 89,
      "subjects_added": 15,
      "total_attempts_tracked": 320
    },
    "processing_time": 4.23,
    "improvement_report": {
      "total_improvements": 89,
      "students_with_improvements": 85
    }
  },
  "stats": {
    "total_processed": 150,
    "students_updated": 125,
    "subjects_overwritten": 89
  },
  "improvements": {
    "grade_improvements": [
      {
        "student_id": "20R01A0501",
        "subject_code": "CS301",
        "from_grade": "F",
        "to_grade": "C",
        "attempt_number": 2
      },
      {
        "student_id": "20R01A0502",
        "subject_code": "MA301",
        "from_grade": "D",
        "to_grade": "B",
        "attempt_number": 3
      }
    ]
  },
  "firebase": {
    "enabled": true,
    "processing_time": 4.23,
    "storage_url": "https://storage.googleapis.com/plant-ec218.firebasestorage.app/supply_jntuk_20250813_153000_supply_results.pdf"
  }
}
    """)
    
    print("\n❌ 2. Error Response Examples:")
    print("""
# Missing PDF file
{
  "error": "Missing required fields (pdf, format).",
  "status": 400
}

# Invalid format
{
  "error": "Invalid format type. Must be 'jntuk' or 'autonomous'.",
  "status": 400
}

# No students found in PDF
{
  "error": "No valid student results found in supply PDF",
  "status": 400
}

# Authentication error
{
  "error": "Unauthorized - Invalid API key",
  "status": 401
}
    """)

def show_what_happens_during_upload():
    """Show the step-by-step process"""
    print("\n\n🔄 WHAT HAPPENS DURING SUPPLY UPLOAD")
    print("=" * 60)
    
    print("""
📥 STEP 1: PDF Upload
   ✅ File received and validated
   ✅ Format type checked (jntuk/autonomous)
   ✅ File saved to temporary location

📖 STEP 2: PDF Parsing
   ✅ Extract student register numbers
   ✅ Extract subject codes and grades
   ✅ Parse supply exam results
   ✅ Detect semester and year information

🔍 STEP 3: Firebase Lookup
   ✅ Search existing records by register number
   ✅ Find matching student documents
   ✅ Load current academic records

🔄 STEP 4: Smart Merge Processing
   ✅ Compare supply grades with regular grades
   ✅ Apply overwrite rules:
      • Failed to Passed → OVERWRITE
      • Grade improvement → OVERWRITE  
      • Grade downgrade → PRESERVE original
   ✅ Track attempt counts
   ✅ Maintain attempt history

💾 STEP 5: Firebase Update
   ✅ Update student documents
   ✅ Save merged academic records
   ✅ Record processing statistics

📤 STEP 6: File Storage
   ✅ Upload PDF to Firebase Storage
   ✅ Generate permanent download URL

📊 STEP 7: Response Generation
   ✅ Compile processing statistics
   ✅ List grade improvements
   ✅ Return detailed results
    """)

def show_troubleshooting():
    """Show common issues and solutions"""
    print("\n\n🔧 TROUBLESHOOTING")
    print("=" * 60)
    
    print("\n❌ Problem: 'Missing required fields' error")
    print("✅ Solution: Ensure both 'pdf' file and 'format' are provided")
    
    print("\n❌ Problem: 'No valid student results found'")
    print("✅ Solution: Check PDF format - ensure it's a valid JNTUK/Autonomous result PDF")
    
    print("\n❌ Problem: 'Students not found in Firebase'")
    print("✅ Solution: Upload regular results first before supply results")
    
    print("\n❌ Problem: 'Authentication failed'")
    print("✅ Solution: Check X-API-Key header is correct")
    
    print("\n❌ Problem: Large file upload timeout")
    print("✅ Solution: Ensure PDF is under 10MB, good internet connection")
    
    print("\n❌ Problem: No grade improvements shown")
    print("✅ Solution: This is normal if supply grades aren't better than regular grades")

if __name__ == "__main__":
    show_api_endpoints()
    show_curl_examples()
    show_javascript_examples()
    show_python_examples()
    show_local_testing()
    show_response_examples()
    show_what_happens_during_upload()
    show_troubleshooting()
