🎯 SUMMARY: Upload Your Supply PDF for Smart F → Better Grade Replacement

📁 YOUR PDF FILE:
"Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf"

🔑 YOUR API KEY: 
"my-very-secret-admin-api-key"

🌐 YOUR DEPLOYED SERVER:
https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 OPTION 1: Use Python Script (RECOMMENDED)
1. Run: python upload_my_supply_pdf.py
2. The script will:
   ✅ Check if your PDF exists
   ✅ Upload to your deployed server
   ✅ Show detailed results including F → better grade replacements
   ✅ Display statistics and improvement counts

🚀 OPTION 2: Use curl Command

Windows Command Prompt:
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" ^
  -H "X-API-Key: my-very-secret-admin-api-key" ^
  -F "pdf=@Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf" ^
  -F "format=jntuk"

PowerShell:
curl -X POST "https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf" `
  -H "X-API-Key: my-very-secret-admin-api-key" `
  -F "pdf=@Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf" `
  -F "format=jntuk"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 WHAT THE SMART SYSTEM WILL DO:

📖 STEP 1: Parse Supply PDF
   ✅ Extract student HTNOs (Hall Ticket Numbers)
   ✅ Extract subject codes and supply grades
   ✅ Identify this as "II B.Tech I Semester Supplementary"

🔍 STEP 2: Firebase Lookup
   ✅ Search existing regular results by HTNO
   ✅ Load current subject grades for each student
   ✅ Prepare for intelligent comparison

🎯 STEP 3: Smart Grade Replacement Logic
   ✅ Match subjects by exact subject code
   ✅ Apply replacement rules:

   RULE 1: F → Better Grade (Priority)
   Regular: CS201=F, Supply: CS201=C → Final: CS201=C ✅ REPLACED
   Regular: MA201=F, Supply: MA201=B → Final: MA201=B ✅ REPLACED
   
   RULE 2: Grade Improvement  
   Regular: PH201=D, Supply: PH201=B → Final: PH201=B ✅ REPLACED
   Regular: EN201=C, Supply: EN201=A → Final: EN201=A ✅ REPLACED
   
   RULE 3: No Downgrade (Preserve Original)
   Regular: CS202=B, Supply: CS202=C → Final: CS202=B ❌ PRESERVED
   Regular: MA202=A, Supply: MA202=B → Final: MA202=A ❌ PRESERVED

📊 STEP 4: Track Attempts
   ✅ Regular results = Attempt #1
   ✅ Supply results = Attempt #2
   ✅ Maintain detailed attempt history
   ✅ Record improvement timestamps

💾 STEP 5: Firebase Update
   ✅ Update student documents with merged results
   ✅ Save attempt history and improvement tracking
   ✅ Preserve original grades for audit trail

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 EXPECTED RESULTS:
• Students processed: (number of students in your PDF)
• Students found in Firebase: (students with existing regular results)
• Subjects overwritten: (F grades replaced + improvements)
• F → Better Grade replacements: (main focus - failed students who passed)
• Grade improvements: (students who got better grades)
• Total attempts tracked: (all supply attempts recorded)

🎉 SUCCESS INDICATORS:
✅ "F → C (Attempt #2) [FAILED TO PASSED]" - Student passed a failed subject
✅ "D → B (Attempt #2) [GRADE IMPROVED]" - Student improved their grade
✅ Processing statistics showing subjects overwritten
✅ PDF stored in Firebase Storage for future reference

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 READY TO UPLOAD? 
Your system is fully configured and ready to process your supply PDF with intelligent F → better grade replacement!
