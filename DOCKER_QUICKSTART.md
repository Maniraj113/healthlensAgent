# Docker Quick Start Guide

## Local Development (Docker Compose)

### 1. Prepare Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your GOOGLE_API_KEY
# GOOGLE_API_KEY=your_actual_key_here
```

### 2. Build and Start Services
```bash
# Build images
docker-compose build

# Start services in background
docker-compose up -d

# Or start with logs visible
docker-compose up
```

### 3. Access Services
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### 4. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. Stop Services
```bash
docker-compose down

# Remove volumes (clears database)
docker-compose down -v
```

---

## GitHub Setup

### 1. Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: Healthcare Hackathon with Docker"
```

### 2. Create GitHub Repository
1. Go to https://github.com/new
2. Create repository: `healthcareHackathon`
3. Do NOT initialize with README (we have one)

### 3. Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/healthcareHackathon.git
git branch -M main
git push -u origin main
```

### 4. Verify .gitignore
```bash
# Check what would be committed
git status

# Should NOT show:
# - .env
# - node_modules/
# - __pycache__/
# - .venv/
# - *.db
```

---

## Cloud Run Deployment

### 1. Set Up Google Cloud Project
```bash
# Set project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID

# Set as default
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com
```

### 2. Create Cloud Build Trigger
```bash
# Connect GitHub repository
gcloud builds connect --repository-name=healthcareHackathon \
  --repository-owner=YOUR_USERNAME \
  --region=$REGION

# Create trigger
gcloud builds triggers create github \
  --name=health-triage-deploy \
  --repo-name=healthcareHackathon \
  --repo-owner=YOUR_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild-cloudrun.yaml
```

### 3. Set Up Secrets
```bash
# Store Google API Key
echo -n "your-google-api-key" | gcloud secrets create google-api-key --data-file=-

# Grant Cloud Build access
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding google-api-key \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### 4. Deploy
```bash
# Push to GitHub - Cloud Build will automatically deploy
git push origin main

# Or manually trigger build
gcloud builds submit --config=cloudbuild-cloudrun.yaml
```

### 5. Get Service URLs
```bash
# Backend
gcloud run services describe health-triage-backend \
  --region $REGION \
  --format 'value(status.url)'

# Frontend
gcloud run services describe health-triage-frontend \
  --region $REGION \
  --format 'value(status.url)'
```

---

## Troubleshooting

### Docker Issues
```bash
# Check if Docker is running
docker ps

# View image details
docker images

# Remove unused images
docker image prune

# Rebuild without cache
docker-compose build --no-cache
```

### Build Failures
```bash
# View Cloud Build logs
gcloud builds log <BUILD_ID>

# List recent builds
gcloud builds list --limit=10

# Check build status
gcloud builds describe <BUILD_ID>
```

### CORS/Connection Issues
1. Ensure backend is running: `curl http://localhost:8000/api/v1/health`
2. Check frontend logs: `docker-compose logs frontend`
3. Verify nginx.conf proxy settings
4. Check CORS headers: `curl -i http://localhost:8000/`

### Database Issues
```bash
# Reset database (local)
docker-compose down -v
docker-compose up -d

# For Cloud Run, use Cloud SQL instead of SQLite
```

---

## File Structure

```
healthcareHackathon/
├── Dockerfile.backend          # Backend Docker image
├── Dockerfile.frontend         # Frontend Docker image
├── docker-compose.yml          # Local development setup
├── nginx.conf                  # Frontend web server config
├── cloudbuild-cloudrun.yaml    # Cloud Build pipeline
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git exclusions
├── .env.example                # Environment template
├── app/                        # Backend source
│   ├── main.py                # FastAPI app with CORS
│   ├── config.py              # Configuration
│   └── ...
└── frontend/                   # Frontend source
    └── sevasetu_-ai-clinical-triage/
        ├── package.json
        ├── vite.config.ts
        └── ...
```

---

## Environment Variables

### Local Development (.env)
```
GOOGLE_API_KEY=your_key
ENVIRONMENT=development
DEBUG=true
```

### Cloud Run (via Cloud Build)
```
GOOGLE_API_KEY=your_key
ENVIRONMENT=production
DEBUG=false
FRONTEND_URL=https://health-triage-frontend-xxxxx.run.app
```

---

## Next Steps

1. ✅ Create Docker files
2. ✅ Set up docker-compose
3. ✅ Configure CORS
4. ✅ Create .gitignore
5. → Push to GitHub
6. → Set up Cloud Build
7. → Deploy to Cloud Run
8. → Monitor and scale

---

## Useful Commands

```bash
# Docker Compose
docker-compose up -d              # Start services
docker-compose down               # Stop services
docker-compose logs -f            # View logs
docker-compose ps                 # List services

# Docker
docker build -t image:tag .       # Build image
docker run -p 8000:8000 image     # Run container
docker exec -it container bash    # Access container

# Google Cloud
gcloud run services list          # List services
gcloud run services delete name   # Delete service
gcloud logging read --limit=50    # View logs
```

---

## Support

For issues, check:
- DOCKER_DEPLOYMENT.md (detailed guide)
- Docker documentation: https://docs.docker.com
- Cloud Run documentation: https://cloud.google.com/run/docs
