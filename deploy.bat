@echo off
REM Google Cloud Deployment Script for Windows
REM Student Result Analysis System

echo.
echo ==========================================
echo 🚀 Student Result Analysis - Google Cloud Deployment
echo ==========================================
echo.

REM Check if required tools are installed
where gcloud >nul 2>nul
if errorlevel 1 (
    echo ❌ Google Cloud CLI not found. Please install it first.
    echo Download from: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

where docker >nul 2>nul
if errorlevel 1 (
    echo ❌ Docker not found. Please install it first.
    echo Download from: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

REM Get project configuration
set /p PROJECT_ID="Enter your Google Cloud Project ID: "
set /p REGION="Enter deployment region (default: us-central1): "
if "%REGION%"=="" set REGION=us-central1
set /p SERVICE_NAME="Enter service name (default: student-result-backend): "
if "%SERVICE_NAME%"=="" set SERVICE_NAME=student-result-backend

if "%PROJECT_ID%"=="" (
    echo ❌ Project ID cannot be empty
    pause
    exit /b 1
)

echo.
echo ✅ Configuration:
echo    Project ID: %PROJECT_ID%
echo    Region: %REGION%
echo    Service Name: %SERVICE_NAME%
echo.

REM Set project
echo 🔧 Setting up Google Cloud configuration...
gcloud config set project %PROJECT_ID%

REM Enable required APIs
echo 🔌 Enabling required Google Cloud APIs...
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

REM Check if serviceAccount.json exists
if not exist "serviceAccount.json" (
    echo ❌ serviceAccount.json not found!
    echo Please ensure your Firebase service account key is named 'serviceAccount.json'
    echo Download it from: Firebase Console → Project Settings → Service Accounts
    pause
    exit /b 1
)

echo ✅ Found serviceAccount.json
echo.

REM Deploy from source (recommended for Windows)
echo 🚀 Deploying from source...
gcloud run deploy %SERVICE_NAME% ^
    --source . ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --memory 2Gi ^
    --cpu 2 ^
    --timeout 3600 ^
    --max-instances 10 ^
    --set-env-vars "FLASK_ENV=production,PYTHONPATH=/app" ^
    --quiet

if errorlevel 1 (
    echo ❌ Deployment failed
    pause
    exit /b 1
)

REM Get service URL
for /f "tokens=*" %%i in ('gcloud run services describe %SERVICE_NAME% --region %REGION% --format="value(status.url)"') do set SERVICE_URL=%%i

echo.
echo ==========================================
echo 🎉 Deployment completed successfully!
echo ==========================================
echo ✅ Service URL: %SERVICE_URL%
echo.

REM Test the deployment
echo 🧪 Testing deployment...
curl -s -o nul -w "%%{http_code}" "%SERVICE_URL%/api/firebase-status" > temp_status.txt
set /p HTTP_STATUS=<temp_status.txt
del temp_status.txt

if "%HTTP_STATUS%"=="200" (
    echo ✅ Health check passed!
) else (
    echo ⚠️ Health check returned status: %HTTP_STATUS%
    echo Check logs with: gcloud logs tail "resource.type=cloud_run_revision"
)

echo.
echo ==========================================
echo 📋 Useful Commands:
echo ==========================================
echo View logs:
echo   gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=%SERVICE_NAME%" --region %REGION%
echo.
echo Update service:
echo   gcloud run deploy %SERVICE_NAME% --source . --region %REGION%
echo.
echo Delete service:
echo   gcloud run services delete %SERVICE_NAME% --region %REGION%
echo.

echo ==========================================
echo 🔥 Firebase Configuration Reminder:
echo ==========================================
echo 1. Update CORS settings in Firebase to allow: %SERVICE_URL%
echo 2. Update Firestore security rules if needed
echo 3. Verify Firebase Storage bucket permissions
echo.

echo ==========================================
echo 🚀 Your Student Result Analysis system is now live at:
echo    %SERVICE_URL%
echo ==========================================
echo.
echo Happy analyzing! 📊
echo.
pause
