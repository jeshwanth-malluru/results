@echo off
REM Local testing script for Google Cloud deployment (Windows)
REM This script tests your app locally using Docker before deploying to Cloud Run

echo.
echo 🧪 Testing Student Result Analysis locally with Docker
echo ==================================================
echo.

REM Check if Docker is running
docker info >nul 2>nul
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if serviceAccount.json exists
if not exist "serviceAccount.json" (
    echo ❌ serviceAccount.json not found!
    echo Please download your Firebase service account key and name it 'serviceAccount.json'
    pause
    exit /b 1
)

echo ✅ Found serviceAccount.json

REM Build Docker image
echo 🐳 Building Docker image...
docker build -t student-result-local .

if errorlevel 1 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

REM Stop any existing container
docker stop student-result-test >nul 2>nul
docker rm student-result-test >nul 2>nul

REM Run container
echo 🚀 Starting container on port 8080...
docker run -d ^
    --name student-result-test ^
    -p 8080:8080 ^
    -e FLASK_ENV=production ^
    -e PYTHONPATH=/app ^
    student-result-local

if errorlevel 1 (
    echo ❌ Failed to start container
    pause
    exit /b 1
)

REM Wait for container to start
echo ⏳ Waiting for container to start...
timeout /t 10 /nobreak >nul

REM Test the application
echo 🧪 Testing application...
curl -s -o nul -w "%%{http_code}" "http://localhost:8080/api/firebase-status" > temp_status.txt
set /p HTTP_STATUS=<temp_status.txt
del temp_status.txt

if "%HTTP_STATUS%"=="200" (
    echo ✅ Local test passed! Application is working correctly.
    echo 🌐 Test your app at: http://localhost:8080
    echo.
    echo 📋 Test these endpoints:
    echo    - http://localhost:8080/ ^(Home page^)
    echo    - http://localhost:8080/api/firebase-status ^(Firebase status^)
    echo    - http://localhost:8080/student-search ^(Student search^)
    echo    - http://localhost:8080/data-files ^(Data files^)
    echo.
    echo 🛑 To stop the test container:
    echo    docker stop student-result-test
    echo    docker rm student-result-test
    echo.
    echo 🚀 If everything works, you can now deploy to Google Cloud:
    echo    deploy.bat
    echo.
) else (
    echo ❌ Local test failed with status: %HTTP_STATUS%
    echo 📋 Check container logs:
    echo    docker logs student-result-test
    
    REM Show recent logs
    echo.
    echo 🔍 Recent container logs:
    docker logs --tail 20 student-result-test
    
    REM Cleanup
    docker stop student-result-test >nul 2>nul
    docker rm student-result-test >nul 2>nul
    pause
    exit /b 1
)

pause
