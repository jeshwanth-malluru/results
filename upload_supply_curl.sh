#!/bin/bash
# 🚀 Ready-to-use curl command for your supply PDF upload
# Copy and paste this in your terminal

echo "🎯 UPLOADING SUPPLY PDF WITH SMART F → BETTER GRADE REPLACEMENT"
echo "================================================================"
echo "📁 PDF: Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf"
echo "🌐 Server: https://student-result-backend-390507264435.us-central1.run.app"
echo "🔑 API Key: my-very-secret-admin-api-key"
echo ""
echo "🧠 This will:"
echo "   ✅ Parse HTNOs and subject codes from supply PDF"
echo "   ✅ Find existing regular results in Firebase"
echo "   ✅ Replace F grades with better supply grades"
echo "   ✅ Track attempt counts and improvement history"
echo ""

# Windows Command Prompt version
echo "🔧 FOR WINDOWS COMMAND PROMPT:"
echo 'curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" ^'
echo '  -H "X-API-Key: my-very-secret-admin-api-key" ^'
echo '  -F "pdf=@Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf" ^'
echo '  -F "format=jntuk"'
echo ""

# PowerShell version  
echo "🔧 FOR POWERSHELL:"
echo 'curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" `'
echo '  -H "X-API-Key: my-very-secret-admin-api-key" `'
echo '  -F "pdf=@Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf" `'
echo '  -F "format=jntuk"'
echo ""

# Linux/Mac version
echo "🔧 FOR LINUX/MAC TERMINAL:"
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" \
  -H "X-API-Key: my-very-secret-admin-api-key" \
  -F "pdf=@Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf" \
  -F "format=jntuk"
