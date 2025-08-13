## 🚀 Deploy from Google Cloud Console (No Installation Needed)

### Step 1: Open Cloud Shell
1. Go to your Google Cloud Console: https://console.cloud.google.com
2. Make sure you're in project `spry-pipe-467106-m5`
3. Click the **Cloud Shell** icon (>_) in the top right corner

### Step 2: Upload Your Code
In Cloud Shell, run these commands:

```bash
# Clone your repository or upload files
# If you have a GitHub repo:
git clone https://github.com/mjeshwanth/Result-Analysis.git
cd Result-Analysis/backend

# Or upload files manually using Cloud Shell's upload feature
```

### Step 3: Upload Firebase Service Account
1. In Cloud Shell, click the **three dots menu** → **Upload file**
2. Upload your `serviceAccount.json` file from Firebase

### Step 4: Enable Required APIs
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Step 5: Deploy to Cloud Run
```bash
# Set your project (it should already be set)
gcloud config set project spry-pipe-467106-m5

# Deploy your application
gcloud run deploy student-result-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 10 \
  --set-env-vars "FLASK_ENV=production,PYTHONPATH=/app"
```

### Step 6: Test Your Deployment
After deployment, you'll get a URL like:
```
https://student-result-backend-xxx-uc.a.run.app
```

Test it by visiting:
- `https://your-url.run.app/` (Home page)
- `https://your-url.run.app/api/firebase-status` (Health check)

---

## Alternative: Upload Code as ZIP

### If you don't have GitHub:

1. **Create a ZIP file** of your backend folder
2. **Upload to Cloud Shell**:
   - Click **three dots** → **Upload file**
   - Select your ZIP file
3. **Extract in Cloud Shell**:
   ```bash
   unzip your-backend.zip
   cd backend
   ```
4. **Continue with Step 4 above**

---

## What You Need to Prepare:

### 1. Firebase Service Account Key
- Go to: https://console.firebase.google.com
- Select your project → ⚙️ Settings → Service Accounts
- Click **Generate new private key**
- Save as `serviceAccount.json`

### 2. Your Backend Code
- Either push to GitHub
- Or create a ZIP file of your `backend` folder

### 3. Required Files Checklist
Make sure these files are in your backend folder:
- ✅ `app.py` (your main Flask app)
- ✅ `requirements.txt` (dependencies)
- ✅ `Dockerfile` (container config)
- ✅ `serviceAccount.json` (Firebase key)
- ✅ All your Python files and templates

---

## After Deployment:

### Update Firebase CORS Settings
1. Go to Firebase Console → Authentication → Settings
2. Add your Cloud Run URL to authorized domains

### Test Your Smart Merge System
1. Visit your deployed URL
2. Try uploading a PDF
3. Check Firebase Firestore for data

---

## Cost: FREE (for normal usage)
- Cloud Run free tier: 2M requests/month
- Your app will likely stay in free tier

Ready to deploy? Let me know if you need help with any step!
