# Upload 2-1 Supply PDF - Fixed Commands
# The file path has spaces, so we need to handle it properly

# ==============================================================================
# METHOD 1: PowerShell (Recommended)
# ==============================================================================
# Copy and paste this command in PowerShell:

$headers = @{
    'X-API-Key' = 'my-very-secret-admin-api-key'
}

$filePath = 'c:\Users\jeshw_3agky5x\Downloads\Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf'

# Using Invoke-RestMethod (PowerShell native)
$form = @{
    pdf = Get-Item $filePath
    format = 'jntuk'
}

try {
    $response = Invoke-RestMethod -Uri 'https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf' -Method Post -Headers $headers -Form $form
    Write-Host "✅ SUCCESS!" -ForegroundColor Green
    Write-Host "📊 Results:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# ==============================================================================
# METHOD 2: curl with proper escaping
# ==============================================================================
# Use this curl command (copy entire line):
curl.exe -X POST -H "X-API-Key: my-very-secret-admin-api-key" -F "pdf=@\"c:\Users\jeshw_3agky5x\Downloads\Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf\"" -F "format=jntuk" https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf

# ==============================================================================
# METHOD 3: Alternative curl with short path
# ==============================================================================
# First, copy the file to a simpler path:
# copy "c:\Users\jeshw_3agky5x\Downloads\Results of II B.Tech I Semester (R23R20R19R16) Supplementary Examinations, May-2025.pdf" "c:\temp\supply_21.pdf"
# 
# Then use:
# curl.exe -X POST -H "X-API-Key: my-very-secret-admin-api-key" -F "pdf=@c:\temp\supply_21.pdf" -F "format=jntuk" https://student-result-backend-390507264435.us-central1.run.app/upload-supply-pdf
