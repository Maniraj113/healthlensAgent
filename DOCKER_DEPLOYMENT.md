# Docker & Cloud Run Deployment Guide

## Overview

This guide covers:
1. Local Docker development with docker-compose
2. Pushing to GitHub
3. Setting up Cloud Build pipeline
4. Deploying to Cloud Run

---

## Part 1: Local Development with Docker

### Prerequisites
- Docker Desktop installed
- Docker Compose installed
- `.env` file configured with `GOOGLE_API_KEY`

### Build and Run Locally

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Access Services
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Environment Variables for Local Development
Create a `.env` file:
```
GOOGLE_API_KEY=your_api_key_here
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./health_triage.db
```

---

## Part 2: Push to GitHub

### Initial Setup
```bash
# Initialize git (if not already done)
git init

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/healthcareHackathon.git

# Create .gitignore (already created)
# Verify important files are ignored
git status

# Add all files
git add .

# Commit
git commit -m "Initial commit: Docker setup and Cloud Build configuration"

# Push to main branch
git branch -M main
git push -u origin main
```

### Important: Verify .gitignore
Ensure these are NOT committed:
- `.env` (use `.env.example` instead)
- `node_modules/` (frontend)
- `__pycache__/` (Python)
- `.venv/` (Virtual environment)
- `*.db` (Database files)
- `.git/` (Git metadata)

---

## Part 3: Google Cloud Setup

### 1. Create GCP Project
```bash
# Set your project ID
export PROJECT_ID="your-project-id"

# Create project
gcloud projects create $PROJECT_ID

# Set as default
gcloud config set project $PROJECT_ID
```

### 2. Enable Required APIs
```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com \
  artifactregistry.googleapis.com
```

### 3. Create Cloud Build Trigger

**Via Cloud Console:**
1. Go to Cloud Build → Triggers
2. Click "Create Trigger"
3. Configure:
   - **Name**: health-triage-deploy
   - **Repository**: Select your GitHub repo
   - **Branch**: main
   - **Build configuration**: Cloud Build configuration file
   - **Location**: cloudbuild-cloudrun.yaml
4. Click "Create"

**Or via gcloud:**
```bash
gcloud builds triggers create github \
  --name=health-triage-deploy \
  --repo-name=healthcareHackathon \
  --repo-owner=YOUR_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild-cloudrun.yaml
```

### 4. Set Build Secrets (Google API Key)

```bash
# Create secret in Secret Manager
echo -n "your-google-api-key" | gcloud secrets create google-api-key --data-file=-

# Grant Cloud Build access
gcloud secrets add-iam-policy-binding google-api-key \
  --member=serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### 5. Update Cloud Build Configuration

Add to `cloudbuild-cloudrun.yaml` steps (after push steps):

```yaml
  # Fetch secret
  - name: 'gcr.io/cloud-builders/gcloud'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        gcloud secrets versions access latest --secret="google-api-key" > /workspace/api-key.txt
```

---

## Part 4: Deploy to Cloud Run

### Automatic Deployment (via Cloud Build)

Push to main branch:
```bash
git push origin main
```

Cloud Build will automatically:
1. Build backend Docker image
2. Build frontend Docker image
3. Push to Container Registry
4. Deploy backend to Cloud Run
5. Deploy frontend to Cloud Run

### Manual Deployment

```bash
# Build and push backend
docker build -f Dockerfile.backend -t gcr.io/$PROJECT_ID/health-triage-backend:latest .
docker push gcr.io/$PROJECT_ID/health-triage-backend:latest

# Deploy backend
gcloud run deploy health-triage-backend \
  --image gcr.io/$PROJECT_ID/health-triage-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key,ENVIRONMENT=production,DEBUG=false \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600

# Build and push frontend
docker build -f Dockerfile.frontend -t gcr.io/$PROJECT_ID/health-triage-frontend:latest .
docker push gcr.io/$PROJECT_ID/health-triage-frontend:latest

# Deploy frontend
gcloud run deploy health-triage-frontend \
  --image gcr.io/$PROJECT_ID/health-triage-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1
```

### Get Service URLs

```bash
# Backend URL
gcloud run services describe health-triage-backend \
  --region us-central1 \
  --format 'value(status.url)'

# Frontend URL
gcloud run services describe health-triage-frontend \
  --region us-central1 \
  --format 'value(status.url)'
```

---

## Part 5: CORS Configuration

### Local Development
- Backend automatically allows `localhost:3000`, `localhost:80`
- Frontend nginx proxies `/api/` to backend

### Cloud Run Production
- Backend CORS configured for `https://*.run.app`
- Frontend nginx proxies to backend service URL
- Update nginx.conf with actual backend URL:

```nginx
proxy_pass https://health-triage-backend-xxxxx.run.app;
```

---

## Part 6: Environment Variables

### Backend (.env)
```
GOOGLE_API_KEY=your_key
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=sqlite:///./health_triage.db
HOST=0.0.0.0
PORT=8000
FRONTEND_URL=https://health-triage-frontend-xxxxx.run.app
```

### Cloud Run Deployment
Set via `--set-env-vars`:
```bash
--set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY,ENVIRONMENT=production,DEBUG=false
```

---

## Troubleshooting

### Build Failures
```bash
# Check build logs
gcloud builds log <BUILD_ID>

# View recent builds
gcloud builds list --limit=10
```

### CORS Issues
1. Check backend CORS configuration in `app/main.py`
2. Verify frontend URL is in allowed origins
3. Check nginx.conf proxy settings

### Container Issues
```bash
# View Cloud Run logs
gcloud run services describe health-triage-backend --region us-central1

# Stream logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=health-triage-backend" --limit 50 --format json
```

### Database Issues
- Cloud Run instances are ephemeral
- Use Cloud SQL for persistent database
- Or use Cloud Storage for database backups

---

## Production Checklist

- [ ] `.env` file NOT committed to GitHub
- [ ] `GOOGLE_API_KEY` set in Cloud Build secrets
- [ ] CORS origins configured for production URLs
- [ ] Database migration strategy planned
- [ ] Logging configured for Cloud Logging
- [ ] Health checks working
- [ ] Load testing completed
- [ ] Security headers verified
- [ ] Rate limiting configured (if needed)
- [ ] Monitoring and alerts set up

---

## Useful Commands

```bash
# View all Cloud Run services
gcloud run services list

# Update service environment variables
gcloud run services update health-triage-backend \
  --update-env-vars KEY=VALUE \
  --region us-central1

# Delete service
gcloud run services delete health-triage-backend --region us-central1

# View service metrics
gcloud monitoring time-series list \
  --filter 'metric.type="run.googleapis.com/request_count"'
```

---

## Next Steps

1. Commit and push code to GitHub
2. Create Cloud Build trigger
3. Set up secrets in Secret Manager
4. Deploy to Cloud Run
5. Monitor logs and metrics
6. Set up continuous monitoring and alerts
