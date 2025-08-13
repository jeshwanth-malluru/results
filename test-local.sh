#!/bin/bash

# Local testing script for Google Cloud deployment
# This script tests your app locally using Docker before deploying to Cloud Run

set -e

echo "🧪 Testing Student Result Analysis locally with Docker"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if serviceAccount.json exists
if [ ! -f "serviceAccount.json" ]; then
    echo "❌ serviceAccount.json not found!"
    echo "Please download your Firebase service account key and name it 'serviceAccount.json'"
    exit 1
fi

echo "✅ Found serviceAccount.json"

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t student-result-local .

# Run container
echo "🚀 Starting container on port 8080..."
docker run -d \
    --name student-result-test \
    -p 8080:8080 \
    -e FLASK_ENV=production \
    -e PYTHONPATH=/app \
    student-result-local

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Test the application
echo "🧪 Testing application..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8080/api/firebase-status" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Local test passed! Application is working correctly."
    echo "🌐 Test your app at: http://localhost:8080"
    echo ""
    echo "📋 Test these endpoints:"
    echo "   - http://localhost:8080/ (Home page)"
    echo "   - http://localhost:8080/api/firebase-status (Firebase status)"
    echo "   - http://localhost:8080/student-search (Student search)"
    echo "   - http://localhost:8080/data-files (Data files)"
    echo ""
    echo "🛑 To stop the test container:"
    echo "   docker stop student-result-test"
    echo "   docker rm student-result-test"
    echo ""
    echo "🚀 If everything works, you can now deploy to Google Cloud:"
    echo "   ./deploy.sh (Linux/Mac) or deploy.bat (Windows)"
else
    echo "❌ Local test failed with status: $HTTP_STATUS"
    echo "📋 Check container logs:"
    echo "   docker logs student-result-test"
    
    # Show recent logs
    echo ""
    echo "🔍 Recent container logs:"
    docker logs --tail 20 student-result-test
    
    # Cleanup
    docker stop student-result-test || true
    docker rm student-result-test || true
    exit 1
fi
