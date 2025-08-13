# Google Cloud Deployment for Student Result Analysis System

## Prerequisites

### 1. Google Cloud Platform Account
- Create a GCP account (separate from Firebase)
- Create a new GCP project or use existing one
- Enable billing for the project

### 2. Required APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 3. Install Google Cloud CLI
Download from: https://cloud.google.com/sdk/docs/install

## Deployment Options

### Option 1: Cloud Run (Recommended - Serverless)
- ✅ Auto-scaling
- ✅ Pay per use
- ✅ Easy deployment
- ✅ HTTPS by default

### Option 2: App Engine
- ✅ Managed platform
- ✅ Auto-scaling
- ✅ Integrated with GCP services

### Option 3: Compute Engine
- ✅ Full control
- ✅ Custom configurations
- ✅ More expensive

## Recommended: Cloud Run Deployment

### Step 1: Authentication
```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Configure Docker for Artifact Registry
gcloud auth configure-docker
```

### Step 2: Deploy to Cloud Run
```bash
# Deploy directly from source
gcloud run deploy student-result-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10

# Or build and deploy with Docker
docker build -t gcr.io/YOUR_PROJECT_ID/student-result-backend .
docker push gcr.io/YOUR_PROJECT_ID/student-result-backend

gcloud run deploy student-result-backend \
  --image gcr.io/YOUR_PROJECT_ID/student-result-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Step 3: Environment Variables
```bash
# Set Firebase service account (upload your serviceAccount.json to Cloud Run)
gcloud run services update student-result-backend \
  --set-env-vars GOOGLE_APPLICATION_CREDENTIALS=/app/serviceAccount.json

# Set other environment variables
gcloud run services update student-result-backend \
  --set-env-vars FLASK_ENV=production,PORT=8080
```

## Firebase Integration Notes

### Important: Different Accounts
- **Firebase Project**: Your existing Firebase project
- **GCP Project**: New or existing GCP project for hosting
- **Service Account**: Firebase service account works in GCP

### Service Account Setup
1. In Firebase Console → Project Settings → Service Accounts
2. Generate new private key (serviceAccount.json)
3. Upload this file to your Cloud Run container
4. Set GOOGLE_APPLICATION_CREDENTIALS environment variable

### Firestore Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read/write from your Cloud Run service
    match /{document=**} {
      allow read, write: if request.auth != null || 
                           request.headers.origin == "YOUR_CLOUD_RUN_URL";
    }
  }
}
```

## Cost Estimation (Cloud Run)

### Free Tier Limits
- 2 million requests/month
- 400,000 GB-seconds compute time
- 200,000 vCPU-seconds compute time

### Paid Usage (after free tier)
- $0.40 per million requests
- $0.0000025 per GB-second
- $0.00001 per vCPU-second

### Estimated Monthly Cost
- Small usage (1000 requests/day): **$0-5**
- Medium usage (10,000 requests/day): **$5-20**
- Heavy usage (100,000 requests/day): **$20-100**

## Monitoring & Logging

### Cloud Logging
```bash
# View logs
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=student-result-backend"
```

### Cloud Monitoring
- Set up alerts for errors
- Monitor response times
- Track resource usage

## Security Best Practices

### 1. IAM Roles
```bash
# Create service account for Cloud Run
gcloud iam service-accounts create student-result-sa

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:student-result-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/firestore.user"
```

### 2. VPC Connector (Optional)
For connecting to private resources:
```bash
gcloud compute networks vpc-access connectors create student-result-connector \
  --region=us-central1 \
  --subnet=default \
  --subnet-project=YOUR_PROJECT_ID
```

### 3. Cloud Armor (Optional)
For DDoS protection and WAF:
```bash
gcloud compute security-policies create student-result-policy
gcloud compute security-policies rules create 1000 \
  --security-policy student-result-policy \
  --expression "origin.region_code == 'IN'" \
  --action allow
```

## Custom Domain Setup

### 1. Domain Mapping
```bash
gcloud run domain-mappings create \
  --service student-result-backend \
  --domain your-domain.com \
  --region us-central1
```

### 2. SSL Certificate
Cloud Run automatically provisions SSL certificates for custom domains.

## Backup Strategy

### 1. Code Backup
- GitHub repository (already done)
- Cloud Source Repositories mirror

### 2. Firebase Backup
```bash
# Export Firestore data
gcloud firestore export gs://your-backup-bucket/firestore-backup
```

### 3. Application Backup
- Cloud Run automatically handles container backups
- Keep Docker images in Artifact Registry

## Troubleshooting

### Common Issues
1. **Firebase connection fails**: Check service account permissions
2. **Memory errors**: Increase Cloud Run memory allocation
3. **Timeout errors**: Increase Cloud Run timeout
4. **CORS errors**: Configure CORS for your domain

### Debug Commands
```bash
# Check service status
gcloud run services describe student-result-backend --region us-central1

# View recent logs
gcloud logs read "resource.type=cloud_run_revision" --limit 50

# Test service
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  https://student-result-backend-xxx-uc.a.run.app/api/firebase-status
```

## Next Steps After Deployment

1. **Test all endpoints** with production URLs
2. **Set up monitoring** and alerts
3. **Configure custom domain** if needed
4. **Set up CI/CD pipeline** for automatic deployments
5. **Performance testing** with realistic load
6. **Security audit** of the deployed service

## Support

- Google Cloud Console: https://console.cloud.google.com
- Cloud Run Documentation: https://cloud.google.com/run/docs
- Firebase Console: https://console.firebase.google.com
