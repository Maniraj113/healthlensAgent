# Complete Deployment Guide: Docker + GitHub + Cloud Run

## 📋 Overview

This guide walks you through:
1. **Local Development** with Docker Compose
2. **GitHub Setup** for version control
3. **Google Cloud Setup** for CI/CD and deployment
4. **Cloud Run Deployment** for production

---

## Part 1: Local Development with Docker

### Prerequisites
- Docker Desktop installed
- Docker Compose installed
- Git installed
- Google API Key (from https://makersuite.google.com/app/apikey)

### Step 1: Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Google API Key
# GOOGLE_API_KEY=your_actual_key_here
```

### Step 2: Build and Start Services
```bash
# Build Docker images
docker-compose build

# Start services in background
docker-compose up -d

# Or start with visible logs
docker-compose up
```

### Step 3: Verify Services
```bash
# Check running containers
docker-compose ps

# Test backend health
curl http://localhost:8000/api/v1/health

# Test frontend
curl http://localhost/

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Step 4: Access Services
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Step 5: Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

---

## Part 2: GitHub Setup

### Step 1: Verify .gitignore
```bash
# Check what would be committed
git status

# Should NOT include:
# - .env (use .env.example instead)
# - node_modules/ (frontend)
# - __pycache__/ (Python)
# - .venv/ (Virtual environment)
# - *.db (Database files)
# - dist/ (Build artifacts)
```

### Step 2: Initial Commit
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Healthcare Hackathon with Docker and Cloud Build setup"
```

### Step 3: Create GitHub Repository
1. Go to https://github.com/new
2. Create repository: `healthcareHackathon`
3. **Do NOT** initialize with README (we already have one)
4. Click "Create repository"

### Step 4: Push to GitHub
```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/healthcareHackathon.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 5: Verify Push
```bash
# Check remote
git remote -v

# Verify files on GitHub
# Visit: https://github.com/YOUR_USERNAME/healthcareHackathon
```

---

## Part 3: Google Cloud Setup

### Step 1: Create GCP Project
```bash
# Set variables
export PROJECT_ID="health-triage-prod"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID

# Set as default
gcloud config set project $PROJECT_ID

# Enable billing (required for Cloud Run)
# Visit: https://console.cloud.google.com/billing
```

### Step 2: Enable Required APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### Step 3: Store API Key in Secret Manager
```bash
# Store Google API Key
echo -n "your-google-api-key-here" | \
  gcloud secrets create google-api-key --data-file=-

# Verify
gcloud secrets list
```

### Step 4: Grant Cloud Build Access to Secret
```bash
# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

# Grant access
gcloud secrets add-iam-policy-binding google-api-key \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

---

## Part 4: Cloud Build Setup

### Option A: Using Cloud Build (Recommended)

#### Step 1: Connect GitHub Repository
```bash
# Via gcloud
gcloud builds connect \
  --repository-name=healthcareHackathon \
  --repository-owner=YOUR_USERNAME \
  --region=$REGION
```

Or via Cloud Console:
1. Go to Cloud Build → Repositories
2. Click "Connect Repository"
3. Select GitHub
4. Authorize and select your repository

#### Step 2: Create Cloud Build Trigger
```bash
gcloud builds triggers create github \
  --name=health-triage-deploy \
  --repo-name=healthcareHackathon \
  --repo-owner=YOUR_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild-cloudrun.yaml
```

Or via Cloud Console:
1. Go to Cloud Build → Triggers
2. Click "Create Trigger"
3. Configure:
   - **Name**: health-triage-deploy
   - **Repository**: Your GitHub repo
   - **Branch**: main
   - **Build configuration**: Cloud Build configuration file
   - **Location**: cloudbuild-cloudrun.yaml
4. Click "Create"

#### Step 3: Test Trigger
```bash
# Push to main to trigger build
git push origin main

# View build logs
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

### Option B: Using GitHub Actions

#### Step 1: Create Service Account
```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/run.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.admin
```

#### Step 2: Create Service Account Key
```bash
# Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com

# Copy key content
cat key.json
```

#### Step 3: Add GitHub Secrets
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secrets:
   - **GCP_PROJECT_ID**: your-project-id
   - **GCP_SA_KEY**: (paste contents of key.json)
   - **GOOGLE_API_KEY**: your-google-api-key

#### Step 4: Workflow Ready
- Workflow file already created: `.github/workflows/deploy-cloudrun.yml`
- Automatically triggers on push to main

---

## Part 5: Deploy to Cloud Run

### Automatic Deployment (via Cloud Build)

```bash
# Push to main branch
git push origin main

# Cloud Build automatically:
# 1. Builds backend Docker image
# 2. Builds frontend Docker image
# 3. Pushes to Container Registry
# 4. Deploys backend to Cloud Run
# 5. Deploys frontend to Cloud Run
```

### Manual Deployment

#### Build and Push Images
```bash
# Build backend
docker build -f Dockerfile.backend \
  -t gcr.io/$PROJECT_ID/health-triage-backend:latest .

# Push backend
docker push gcr.io/$PROJECT_ID/health-triage-backend:latest

# Build frontend
docker build -f Dockerfile.frontend \
  -t gcr.io/$PROJECT_ID/health-triage-frontend:latest .

# Push frontend
docker push gcr.io/$PROJECT_ID/health-triage-frontend:latest
```

#### Deploy Backend
```bash
gcloud run deploy health-triage-backend \
  --image gcr.io/$PROJECT_ID/health-triage-backend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$(gcloud secrets versions access latest --secret="google-api-key"),ENVIRONMENT=production,DEBUG=false \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 100
```

#### Deploy Frontend
```bash
gcloud run deploy health-triage-frontend \
  --image gcr.io/$PROJECT_ID/health-triage-frontend:latest \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 50
```

### Get Service URLs
```bash
# Backend URL
gcloud run services describe health-triage-backend \
  --region $REGION \
  --format 'value(status.url)'

# Frontend URL
gcloud run services describe health-triage-frontend \
  --region $REGION \
  --format 'value(status.url)'
```

---

## Part 6: Verify Deployment

### Test Backend
```bash
# Get backend URL
BACKEND_URL=$(gcloud run services describe health-triage-backend \
  --region $REGION \
  --format 'value(status.url)')

# Test health endpoint
curl $BACKEND_URL/api/v1/health

# Test API documentation
curl $BACKEND_URL/docs
```

### Test Frontend
```bash
# Get frontend URL
FRONTEND_URL=$(gcloud run services describe health-triage-frontend \
  --region $REGION \
  --format 'value(status.url)')

# Test frontend
curl $FRONTEND_URL
```

### Test CORS
```bash
# Test CORS headers
curl -i -X OPTIONS \
  -H "Origin: $FRONTEND_URL" \
  -H "Access-Control-Request-Method: POST" \
  $BACKEND_URL/api/v1/analyze
```

---

## Part 7: Configure CORS for Production

### Update Backend CORS
The backend CORS is already configured to:
- Allow `https://*.run.app` in production
- Allow `FRONTEND_URL` environment variable

### Update Frontend Nginx
Update `nginx.conf` with actual backend URL:

```nginx
location /api/ {
    proxy_pass https://health-triage-backend-xxxxx.run.app;
    # ... rest of config
}
```

Or use environment variable in docker-compose:
```yaml
environment:
  - BACKEND_URL=https://health-triage-backend-xxxxx.run.app
```

---

## Part 8: Monitoring and Logs

### View Cloud Build Logs
```bash
# List builds
gcloud builds list --limit=10

# View specific build
gcloud builds log <BUILD_ID>

# Stream logs
gcloud builds log <BUILD_ID> --stream
```

### View Cloud Run Logs
```bash
# Backend logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=health-triage-backend" \
  --limit 50 \
  --format json

# Frontend logs
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=health-triage-frontend" \
  --limit 50 \
  --format json
```

### Monitor Services
```bash
# View service details
gcloud run services describe health-triage-backend --region $REGION

# View metrics
gcloud monitoring time-series list \
  --filter 'metric.type="run.googleapis.com/request_count"'
```

---

## Troubleshooting

### Docker Issues
```bash
# Check Docker daemon
docker ps

# Rebuild without cache
docker-compose build --no-cache

# View image details
docker images

# Remove unused images
docker image prune -a
```

### Build Failures
```bash
# View build logs
gcloud builds log <BUILD_ID>

# Check build status
gcloud builds describe <BUILD_ID>

# Retry build
gcloud builds submit --config=cloudbuild-cloudrun.yaml
```

### CORS Issues
1. Verify backend CORS in `app/main.py`
2. Check frontend URL in allowed origins
3. Verify nginx proxy configuration
4. Test with curl: `curl -i http://localhost:8000/`

### Deployment Issues
```bash
# Check service status
gcloud run services describe health-triage-backend --region $REGION

# View recent revisions
gcloud run revisions list --service=health-triage-backend --region=$REGION

# Rollback to previous revision
gcloud run services update-traffic health-triage-backend \
  --to-revisions=REVISION_ID=100 \
  --region=$REGION
```

---

## File Structure

```
healthcareHackathon/
├── Dockerfile.backend              # Backend Docker image
├── Dockerfile.frontend             # Frontend Docker image
├── docker-compose.yml              # Local development
├── nginx.conf                      # Web server config
├── cloudbuild-cloudrun.yaml        # Cloud Build pipeline
├── .dockerignore                   # Docker exclusions
├── .gitignore                      # Git exclusions (updated)
├── .env.example                    # Environment template
├── .github/
│   └── workflows/
│       └── deploy-cloudrun.yml     # GitHub Actions workflow
├── DEPLOYMENT_GUIDE.md             # This file
├── DOCKER_DEPLOYMENT.md            # Detailed guide
├── DOCKER_QUICKSTART.md            # Quick reference
├── DEPLOYMENT_SUMMARY.md           # Summary of changes
├── app/                            # Backend
│   ├── main.py                     # FastAPI with CORS
│   ├── config.py                   # Configuration
│   └── ...
└── frontend/                       # Frontend
    └── sevasetu_-ai-clinical-triage/
        ├── package.json
        ├── vite.config.ts          # Updated config
        ├── .env.production         # Production config
        └── ...
```

---

## Environment Variables Summary

### Local Development (.env)
```
GOOGLE_API_KEY=your_key
ENVIRONMENT=development
DEBUG=true
FRONTEND_URL=http://localhost:80
```

### Cloud Run (via Cloud Build)
```
GOOGLE_API_KEY=<from Secret Manager>
ENVIRONMENT=production
DEBUG=false
FRONTEND_URL=https://health-triage-frontend-xxxxx.run.app
```

---

## Production Checklist

- [ ] `.env` NOT committed to GitHub
- [ ] `GOOGLE_API_KEY` stored in Secret Manager
- [ ] CORS configured for production URLs
- [ ] Health checks working
- [ ] Logs accessible in Cloud Logging
- [ ] Monitoring alerts configured
- [ ] Database strategy planned (Cloud SQL recommended)
- [ ] Security headers verified
- [ ] Rate limiting configured (if needed)
- [ ] Load testing completed

---

## Useful Commands Reference

```bash
# Docker
docker-compose up -d                    # Start services
docker-compose down                     # Stop services
docker-compose logs -f                  # View logs
docker-compose ps                       # List services

# Git
git status                              # Check status
git add .                               # Stage files
git commit -m "message"                 # Commit
git push origin main                    # Push to GitHub

# Google Cloud
gcloud projects list                    # List projects
gcloud services list                    # List enabled APIs
gcloud builds list                      # List builds
gcloud run services list                # List Cloud Run services
gcloud logging read --limit=50          # View logs

# Cloud Run
gcloud run deploy SERVICE --image IMAGE # Deploy service
gcloud run services describe SERVICE    # View service details
gcloud run services delete SERVICE      # Delete service
```

---

## Support & Resources

- **Docker**: https://docs.docker.com
- **Cloud Run**: https://cloud.google.com/run/docs
- **Cloud Build**: https://cloud.google.com/build/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Vite**: https://vitejs.dev
- **React**: https://react.dev

---

## Next Steps

1. ✅ Review Docker files and configuration
2. ✅ Test locally with docker-compose
3. → Commit and push to GitHub
4. → Set up Google Cloud project
5. → Create Cloud Build trigger
6. → Deploy to Cloud Run
7. → Monitor and scale

---

**Last Updated**: November 22, 2024
**Project**: Healthcare Hackathon - AI Clinical Triage
**Deployment**: Docker + GitHub + Cloud Run
