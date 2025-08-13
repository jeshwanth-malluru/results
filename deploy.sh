#!/bin/bash

# Google Cloud Deployment Script for Student Result Analysis System
# This script deploys your Flask app to Google Cloud Run

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Student Result Analysis - Google Cloud Deployment${NC}"
echo "================================================================"

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo -e "${RED}❌ Google Cloud CLI not found. Please install it first.${NC}" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker not found. Please install it first.${NC}" >&2; exit 1; }

# Get project configuration
echo -e "${YELLOW}📋 Project Configuration${NC}"
read -p "Enter your Google Cloud Project ID: " PROJECT_ID
read -p "Enter deployment region (default: us-central1): " REGION
REGION=${REGION:-us-central1}
read -p "Enter service name (default: student-result-backend): " SERVICE_NAME
SERVICE_NAME=${SERVICE_NAME:-student-result-backend}

# Validate project ID
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Project ID cannot be empty${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configuration:${NC}"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service Name: $SERVICE_NAME"
echo ""

# Set project
echo -e "${YELLOW}🔧 Setting up Google Cloud configuration...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔌 Enabling required Google Cloud APIs...${NC}"
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Check if serviceAccount.json exists
if [ ! -f "serviceAccount.json" ]; then
    echo -e "${RED}❌ serviceAccount.json not found!${NC}"
    echo -e "${YELLOW}Please ensure your Firebase service account key is named 'serviceAccount.json'${NC}"
    echo -e "${YELLOW}Download it from: Firebase Console → Project Settings → Service Accounts${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found serviceAccount.json${NC}"

# Build and deploy options
echo -e "${YELLOW}🏗️ Choose deployment method:${NC}"
echo "1) Deploy from source (recommended)"
echo "2) Build Docker image and deploy"
read -p "Enter choice (1 or 2): " DEPLOY_METHOD

if [ "$DEPLOY_METHOD" = "1" ]; then
    # Deploy from source
    echo -e "${YELLOW}🚀 Deploying from source...${NC}"
    gcloud run deploy $SERVICE_NAME \
        --source . \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 3600 \
        --max-instances 10 \
        --set-env-vars "FLASK_ENV=production,PYTHONPATH=/app" \
        --quiet

elif [ "$DEPLOY_METHOD" = "2" ]; then
    # Build and deploy Docker image
    echo -e "${YELLOW}🐳 Building Docker image...${NC}"
    IMAGE_URL="gcr.io/$PROJECT_ID/$SERVICE_NAME"
    
    # Configure Docker for GCR
    gcloud auth configure-docker
    
    # Build image
    docker build -t $IMAGE_URL .
    
    # Push image
    echo -e "${YELLOW}📤 Pushing Docker image...${NC}"
    docker push $IMAGE_URL
    
    # Deploy to Cloud Run
    echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
    gcloud run deploy $SERVICE_NAME \
        --image $IMAGE_URL \
        --platform managed \
        --region $REGION \
        --allow-unauthenticated \
        --memory 2Gi \
        --cpu 2 \
        --timeout 3600 \
        --max-instances 10 \
        --set-env-vars "FLASK_ENV=production,PYTHONPATH=/app" \
        --quiet

else
    echo -e "${RED}❌ Invalid choice${NC}"
    exit 1
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "================================================================"
echo -e "${GREEN}✅ Service URL: $SERVICE_URL${NC}"
echo ""

# Test the deployment
echo -e "${YELLOW}🧪 Testing deployment...${NC}"
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/api/firebase-status" || echo "000")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${YELLOW}⚠️ Health check returned status: $HTTP_STATUS${NC}"
    echo -e "${YELLOW}Check logs: gcloud logs tail --source-type=gce_instance${NC}"
fi

# Show useful commands
echo ""
echo -e "${BLUE}📋 Useful Commands:${NC}"
echo "View logs:"
echo "  gcloud logs tail 'resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME' --region $REGION"
echo ""
echo "Update service:"
echo "  gcloud run deploy $SERVICE_NAME --source . --region $REGION"
echo ""
echo "Delete service:"
echo "  gcloud run services delete $SERVICE_NAME --region $REGION"
echo ""
echo "Set up custom domain:"
echo "  gcloud run domain-mappings create --service $SERVICE_NAME --domain your-domain.com --region $REGION"
echo ""

# Firebase configuration reminder
echo -e "${YELLOW}🔥 Firebase Configuration Reminder:${NC}"
echo "1. Update CORS settings in Firebase to allow: $SERVICE_URL"
echo "2. Update Firestore security rules if needed"
echo "3. Verify Firebase Storage bucket permissions"
echo ""

echo -e "${GREEN}🚀 Your Student Result Analysis system is now live at:${NC}"
echo -e "${GREEN}   $SERVICE_URL${NC}"
echo ""
echo -e "${BLUE}Happy analyzing! 📊${NC}"
