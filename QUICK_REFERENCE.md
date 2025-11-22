# Quick Reference Card

## 🚀 Quick Start Commands

### Local Development
```bash
# Setup
cp .env.example .env
# Edit .env and add GOOGLE_API_KEY

# Run
docker-compose up -d

# Access
# Frontend: http://localhost
# Backend: http://localhost:8000
# Docs: http://localhost:8000/docs

# Stop
docker-compose down
```

### GitHub
```bash
# First time
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/healthcareHackathon.git
git branch -M main
git push -u origin main

# Subsequent pushes
git add .
git commit -m "Your message"
git push origin main
```

### Google Cloud Setup
```bash
export PROJECT_ID="health-triage-prod"
export REGION="us-central1"

# Create project
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Store API key
echo -n "your-key" | gcloud secrets create google-api-key --data-file=-

# Create trigger
gcloud builds triggers create github \
  --name=health-triage-deploy \
  --repo-name=healthcareHackathon \
  --repo-owner=YOUR_USERNAME \
  --branch-pattern="^main$" \
  --build-config=cloudbuild-cloudrun.yaml
```

### Deploy to Cloud Run
```bash
# Automatic (push to main)
git push origin main

# Manual
gcloud builds submit --config=cloudbuild-cloudrun.yaml

# Get URLs
gcloud run services describe health-triage-backend --region $REGION --format 'value(status.url)'
gcloud run services describe health-triage-frontend --region $REGION --format 'value(status.url)'
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `Dockerfile.backend` | Backend container image |
| `Dockerfile.frontend` | Frontend container image |
| `docker-compose.yml` | Local development setup |
| `nginx.conf` | Web server configuration |
| `cloudbuild-cloudrun.yaml` | Cloud Build pipeline |
| `.gitignore` | Git exclusions (updated) |
| `.dockerignore` | Docker exclusions |
| `.env.example` | Environment template |
| `DEPLOYMENT_GUIDE.md` | Complete guide |
| `DOCKER_QUICKSTART.md` | Quick start |

---

## 🔧 Configuration

### Backend CORS (app/main.py)
- **Local**: Allows `localhost:3000`, `localhost:80`
- **Production**: Allows `https://*.run.app`, `FRONTEND_URL`

### Frontend (vite.config.ts)
- **Dev**: Proxies `/api` to `http://localhost:8000`
- **Prod**: Uses `VITE_API_URL` environment variable

### Nginx (nginx.conf)
- Proxies `/api/*` to backend
- Serves static files with caching
- SPA routing support

---

## 🌐 Service URLs

### Local
- Frontend: http://localhost
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Cloud Run
- Frontend: https://health-triage-frontend-xxxxx.run.app
- Backend: https://health-triage-backend-xxxxx.run.app
- API Docs: https://health-triage-backend-xxxxx.run.app/docs

---

## 📊 Environment Variables

### Backend (.env)
```
GOOGLE_API_KEY=your_key
ENVIRONMENT=development|production
DEBUG=true|false
FRONTEND_URL=http://localhost:80
```

### Frontend (.env.production)
```
VITE_API_URL=https://backend-url
VITE_ENVIRONMENT=production
VITE_DEBUG=false
```

---

## 🐛 Troubleshooting

### Docker
```bash
docker-compose logs -f                  # View logs
docker-compose ps                       # Check status
docker-compose build --no-cache         # Rebuild
docker-compose down -v                  # Reset
```

### Build
```bash
gcloud builds list --limit=10            # List builds
gcloud builds log BUILD_ID               # View logs
gcloud builds describe BUILD_ID          # Check status
```

### Cloud Run
```bash
gcloud run services list                 # List services
gcloud run services describe SERVICE     # View details
gcloud logging read --limit=50           # View logs
```

---

## ✅ Deployment Checklist

- [ ] `.env` configured with `GOOGLE_API_KEY`
- [ ] Local testing with `docker-compose up`
- [ ] `.gitignore` verified (no `.env`, `node_modules/`, `__pycache__/`)
- [ ] Committed to git: `git commit -m "..."`
- [ ] Pushed to GitHub: `git push origin main`
- [ ] GCP project created
- [ ] APIs enabled (Cloud Build, Cloud Run)
- [ ] API key stored in Secret Manager
- [ ] Cloud Build trigger created
- [ ] Push to main triggers deployment
- [ ] Services deployed to Cloud Run
- [ ] CORS working in production
- [ ] Health checks passing

---

## 📚 Documentation Files

1. **DEPLOYMENT_GUIDE.md** - Complete step-by-step guide
2. **DOCKER_DEPLOYMENT.md** - Detailed Docker & Cloud Run guide
3. **DOCKER_QUICKSTART.md** - Quick start reference
4. **DEPLOYMENT_SUMMARY.md** - Summary of created files
5. **QUICK_REFERENCE.md** - This file

---

## 🔗 Useful Links

- Docker: https://docs.docker.com
- Cloud Run: https://cloud.google.com/run/docs
- Cloud Build: https://cloud.google.com/build/docs
- FastAPI: https://fastapi.tiangolo.com
- Vite: https://vitejs.dev
- React: https://react.dev

---

## 💡 Tips

1. **Always use `.env.example`** as template, never commit `.env`
2. **Test locally first** with `docker-compose` before pushing
3. **Check `.gitignore`** before committing: `git status`
4. **Monitor Cloud Build** logs: `gcloud builds log BUILD_ID`
5. **Use Cloud Logging** for production debugging
6. **Set up alerts** for Cloud Run services
7. **Keep secrets in Secret Manager**, never in code
8. **Use environment variables** for configuration

---

## 🎯 Common Tasks

### Update Backend Code
```bash
# Edit code
# Test locally
docker-compose up -d
# Commit and push
git add .
git commit -m "Update backend"
git push origin main
# Cloud Build automatically deploys
```

### Update Frontend Code
```bash
# Edit code
# Test locally
docker-compose up -d
# Commit and push
git add .
git commit -m "Update frontend"
git push origin main
# Cloud Build automatically deploys
```

### View Production Logs
```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=health-triage-backend" \
  --limit 50 --format json
```

### Rollback Deployment
```bash
gcloud run revisions list --service=health-triage-backend --region=us-central1
gcloud run services update-traffic health-triage-backend \
  --to-revisions=REVISION_ID=100 --region=us-central1
```

---

**Created**: November 22, 2024
**Project**: Healthcare Hackathon - AI Clinical Triage
