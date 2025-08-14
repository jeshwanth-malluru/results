#!/usr/bin/env python3
"""
📖 COMPLETE GUIDE: How to Upload Supply PDFs
🚀 Your system is deployed at: https://student-result-backend-390507264435.us-central1.run.app
"""

def show_quickstart_guide():
    """The fastest way to get started"""
    print("⚡ QUICKSTART: Upload Supply PDF in 3 Steps")
    print("=" * 60)
    print("🎯 Your deployed server: https://student-result-backend-390507264435.us-central1.run.app")
    print()
    
    print("📋 STEP 1: Prepare your files")
    print("   ✅ Have your supply PDF ready")
    print("   ✅ Ensure it's JNTUK or Autonomous format")
    print("   ✅ Make sure students already have regular results uploaded")
    print()
    
    print("🔑 STEP 2: Get your API key")
    print("   ✅ Check your app.py or config files")
    print("   ✅ Or generate a new one if needed")
    print()
    
    print("📤 STEP 3: Upload using any method below...")

def show_curl_examples():
    """Show curl examples for different scenarios"""
    print("\n\n💻 METHOD 1: Using curl (Terminal/Command Prompt)")
    print("=" * 60)
    
    print("🏫 Upload JNTUK Supply PDF:")
    print("""
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" \\
  -H "X-API-Key: your-api-key-here" \\
  -F "pdf=@BTECH_2-1_SUPPLY_FEB_2025.pdf" \\
  -F "format=jntuk"
    """)
    
    print("🏛️ Upload Autonomous Supply PDF:")
    print("""
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" \\
  -H "X-API-Key: your-api-key-here" \\
  -F "pdf=@Autonomous_Supply_Results.pdf" \\
  -F "format=autonomous"
    """)
    
    print("📱 For Windows Command Prompt, use ^ instead of \\:")
    print("""
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" ^
  -H "X-API-Key: your-api-key-here" ^
  -F "pdf=@BTECH_2-1_SUPPLY_FEB_2025.pdf" ^
  -F "format=jntuk"
    """)

def show_python_script():
    """Show complete Python upload script"""
    print("\n\n🐍 METHOD 2: Using Python Script")
    print("=" * 60)
    
    print("📝 Create this script and run it:")
    print("""
# save this as upload_supply.py
import requests
import json
import os

def upload_supply_pdf(pdf_path, format_type, api_key):
    \"\"\"Upload supply PDF to your deployed system\"\"\"
    
    # Your deployed server URL
    url = "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf"
    
    print(f"🎯 Uploading: {pdf_path}")
    print(f"📋 Format: {format_type}")
    print(f"🌐 Server: {url}")
    print("⏳ Processing...")
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            files = {'pdf': pdf_file}
            data = {'format': format_type}
            headers = {'X-API-Key': api_key}
            
            response = requests.post(url, files=files, data=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ SUCCESS! Supply PDF processed")
                print(f"📊 Students processed: {result.get('stats', {}).get('total_processed', 0)}")
                print(f"🔄 Students updated: {result.get('stats', {}).get('students_updated', 0)}")
                print(f"📈 Subjects overwritten: {result.get('stats', {}).get('subjects_overwritten', 0)}")
                print(f"➕ Subjects added: {result.get('stats', {}).get('subjects_added', 0)}")
                
                # Show grade improvements
                improvements = result.get('improvements', {}).get('grade_improvements', [])
                if improvements:
                    print("\\n🎉 Grade Improvements:")
                    for imp in improvements:
                        print(f"   {imp['student_id']} - {imp['subject_code']}: {imp['from_grade']} → {imp['to_grade']}")
                
                return result
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
    except FileNotFoundError:
        print(f"❌ File not found: {pdf_path}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

# ===== USAGE EXAMPLES =====

# Example 1: Upload JNTUK supply PDF
result = upload_supply_pdf(
    pdf_path="BTECH_2-1_SUPPLY_FEB_2025.pdf",
    format_type="jntuk",
    api_key="your-api-key-here"
)

# Example 2: Upload Autonomous supply PDF  
result = upload_supply_pdf(
    pdf_path="Autonomous_Supply_Results.pdf",
    format_type="autonomous", 
    api_key="your-api-key-here"
)

# Example 3: Batch upload multiple supply PDFs
supply_pdfs = [
    {"path": "BTECH_2-1_SUPPLY_FEB_2025.pdf", "format": "jntuk"},
    {"path": "BTECH_3-1_SUPPLY_FEB_2025.pdf", "format": "jntuk"},
    {"path": "Autonomous_Supply_Results.pdf", "format": "autonomous"}
]

for pdf_info in supply_pdfs:
    if os.path.exists(pdf_info["path"]):
        print(f"\\n🔄 Processing {pdf_info['path']}...")
        upload_supply_pdf(pdf_info["path"], pdf_info["format"], "your-api-key-here")
    else:
        print(f"⚠️ File not found: {pdf_info['path']}")
    """)
    
    print("\n▶️ Run the script:")
    print("   python upload_supply.py")

def show_frontend_integration():
    """Show how to integrate with frontend"""
    print("\n\n🌐 METHOD 3: Frontend Integration (HTML + JavaScript)")
    print("=" * 60)
    
    print("📄 Create this HTML page:")
    print("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Supply PDF Upload</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, button { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        button { background-color: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .status { padding: 15px; margin: 15px 0; border-radius: 4px; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .results { background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin-top: 15px; }
    </style>
</head>
<body>
    <h1>📚 Supply PDF Upload</h1>
    <p>Upload supply exam PDFs to automatically merge with existing regular results</p>
    
    <form id="uploadForm">
        <div class="form-group">
            <label for="pdfFile">Select Supply PDF:</label>
            <input type="file" id="pdfFile" accept=".pdf" required>
        </div>
        
        <div class="form-group">
            <label for="format">PDF Format:</label>
            <select id="format" required>
                <option value="">Choose format...</option>
                <option value="jntuk">JNTUK</option>
                <option value="autonomous">Autonomous</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="apiKey">API Key:</label>
            <input type="password" id="apiKey" placeholder="Enter your API key" required>
        </div>
        
        <button type="submit">🚀 Upload Supply PDF</button>
    </form>
    
    <div id="status"></div>
    <div id="results"></div>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const pdfFile = document.getElementById('pdfFile').files[0];
            const format = document.getElementById('format').value;
            const apiKey = document.getElementById('apiKey').value;
            
            if (!pdfFile || !format || !apiKey) {
                showStatus('❌ Please fill all fields', 'error');
                return;
            }
            
            formData.append('pdf', pdfFile);
            formData.append('format', format);
            
            showStatus('⏳ Uploading and processing supply PDF...', 'info');
            
            try {
                const response = await fetch('https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf', {
                    method: 'POST',
                    headers: {
                        'X-API-Key': apiKey
                    },
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    showStatus('✅ Supply PDF processed successfully!', 'success');
                    showResults(result);
                } else {
                    showStatus(`❌ Error: ${result.error || 'Upload failed'}`, 'error');
                }
            } catch (error) {
                showStatus(`❌ Network error: ${error.message}`, 'error');
            }
        });
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.innerHTML = message;
            statusDiv.className = `status ${type}`;
        }
        
        function showResults(result) {
            const resultsDiv = document.getElementById('results');
            const stats = result.stats || {};
            const improvements = result.improvements?.grade_improvements || [];
            
            let html = `
                <div class="results">
                    <h3>📊 Processing Results</h3>
                    <p><strong>Students Processed:</strong> ${stats.total_processed || 0}</p>
                    <p><strong>Students Updated:</strong> ${stats.students_updated || 0}</p>
                    <p><strong>Subjects Overwritten:</strong> ${stats.subjects_overwritten || 0}</p>
                    <p><strong>Subjects Added:</strong> ${stats.subjects_added || 0}</p>
                    <p><strong>Total Attempts Tracked:</strong> ${stats.total_attempts_tracked || 0}</p>
            `;
            
            if (improvements.length > 0) {
                html += `
                    <h4>🎉 Grade Improvements:</h4>
                    <ul>
                `;
                improvements.forEach(imp => {
                    html += `<li>${imp.student_id} - ${imp.subject_code}: ${imp.from_grade} → ${imp.to_grade} (Attempt #${imp.attempt_number})</li>`;
                });
                html += `</ul>`;
            }
            
            html += `</div>`;
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>
    """)

def show_postman_testing():
    """Show how to test with Postman"""
    print("\n\n📮 METHOD 4: Testing with Postman")
    print("=" * 60)
    
    print("📋 Postman Setup:")
    print("1. Create a new POST request")
    print("2. URL: https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf")
    print("3. Headers:")
    print("   - X-API-Key: your-api-key-here")
    print("4. Body: form-data")
    print("   - pdf: [File] Choose your supply PDF")
    print("   - format: jntuk (or autonomous)")
    print("5. Send the request")
    print()
    print("✅ Expected Response: JSON with processing statistics")

def show_what_happens():
    """Explain what happens during upload"""
    print("\n\n🔍 WHAT HAPPENS WHEN YOU UPLOAD")
    print("=" * 60)
    
    print("📤 1. PDF Upload & Validation")
    print("   - File is received and validated")
    print("   - Format (jntuk/autonomous) is checked")
    print("   - PDF is saved temporarily")
    print()
    
    print("📖 2. PDF Parsing")
    print("   - Student register numbers are extracted")
    print("   - Subject codes and grades are parsed")
    print("   - Supply exam results are identified")
    print()
    
    print("🔍 3. Firebase Lookup")
    print("   - Search for existing students by register number")
    print("   - Load their current academic records")
    print("   - Prepare for intelligent merging")
    print()
    
    print("🧠 4. Smart Merge Logic")
    print("   - Compare supply grades with regular grades")
    print("   - Apply overwrite rules:")
    print("     • Failed → Passed = OVERWRITE ✅")
    print("     • Grade improvement = OVERWRITE ✅")  
    print("     • Grade downgrade = PRESERVE original ❌")
    print("   - Track attempt counts")
    print("   - Maintain detailed history")
    print()
    
    print("💾 5. Firebase Update")
    print("   - Update student documents with merged results")
    print("   - Save attempt history and improvement tracking")
    print("   - Record processing statistics")
    print()
    
    print("📊 6. Response Generation")
    print("   - Compile detailed processing statistics")
    print("   - List all grade improvements")
    print("   - Return comprehensive results")

def show_troubleshooting():
    """Show common issues and solutions"""
    print("\n\n🔧 TROUBLESHOOTING COMMON ISSUES")
    print("=" * 60)
    
    print("❌ Problem: 'Missing required fields' error")
    print("✅ Solution: Ensure both 'pdf' file and 'format' are provided")
    print()
    
    print("❌ Problem: 'Unauthorized - Invalid API key'")
    print("✅ Solution: Check your X-API-Key header is correct")
    print()
    
    print("❌ Problem: 'No valid student results found'")
    print("✅ Solution: Verify the PDF format is correct (JNTUK/Autonomous)")
    print()
    
    print("❌ Problem: 'Students not found in Firebase'")
    print("✅ Solution: Upload regular results first before supply results")
    print()
    
    print("❌ Problem: 'No grade improvements shown'")
    print("✅ Solution: This is normal if supply grades aren't better than regular grades")
    print()
    
    print("❌ Problem: Large file timeout")
    print("✅ Solution: Ensure PDF is under 10MB and you have good internet")

if __name__ == "__main__":
    show_quickstart_guide()
    show_curl_examples()
    show_python_script()
    show_frontend_integration()
    show_postman_testing()
    show_what_happens()
    show_troubleshooting()
