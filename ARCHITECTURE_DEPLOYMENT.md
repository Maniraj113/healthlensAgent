# Architecture & Deployment Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRODUCTION (Cloud Run)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │  Frontend Service    │         │  Backend Service     │    │
│  │  (Cloud Run)         │         │  (Cloud Run)         │    │
│  │                      │         │                      │    │
│  │  - Nginx             │         │  - FastAPI           │    │
│  │  - React App         │◄────────┤  - Multi-Agent AI    │    │
│  │  - Static Files      │ HTTPS   │  - Medical Rules     │    │
│  │  - Port: 80/443      │         │  - Port: 8000        │    │
│  └──────────────────────┘         └──────────────────────┘    │
│         │                                    │                 │
│         │ https://frontend-xxxxx.run.app     │                 │
│         │ https://backend-xxxxx.run.app      │                 │
│         │                                    │                 │
└─────────────────────────────────────────────────────────────────┘
                          ▲
                          │
                          │ Deploy
                          │
┌─────────────────────────────────────────────────────────────────┐
│                    Cloud Build Pipeline                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Trigger: Push to main branch                               │
│  2. Build: Backend Docker image                                │
│  3. Build: Frontend Docker image                               │
│  4. Push: Images to Container Registry                         │
│  5. Deploy: Backend to Cloud Run                               │
│  6. Deploy: Frontend to Cloud Run                              │
│  7. Test: Health checks                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          ▲
                          │
                          │ Push
                          │
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Repository                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  - Source Code                                                 │
│  - Docker Files                                                │
│  - Cloud Build Config                                          │
│  - GitHub Actions Workflow                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          ▲
                          │
                          │ Commit & Push
                          │
┌─────────────────────────────────────────────────────────────────┐
│                  Local Development                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐         ┌──────────────────────┐    │
│  │  Frontend Container  │         │  Backend Container   │    │
│  │  (Docker)            │         │  (Docker)            │    │
│  │                      │         │                      │    │
│  │  - Nginx             │         │  - FastAPI           │    │
│  │  - React Dev Server  │◄────────┤  - Python            │    │
│  │  - Port: 80          │ HTTP    │  - Port: 8000        │    │
│  └──────────────────────┘         └──────────────────────┘    │
│         │                                    │                 │
│         │ http://localhost                   │                 │
│         │ http://localhost:8000              │                 │
│         │                                    │                 │
│  Docker Compose Network                     │                 │
│  (health-triage-network)                    │                 │
│                                              │                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deployment Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT PIPELINE                          │
└─────────────────────────────────────────────────────────────────┘

Developer Workflow:
  1. Edit code locally
  2. Test with docker-compose
  3. Commit changes
  4. Push to GitHub (main branch)
         │
         ▼
  5. Cloud Build triggered automatically
         │
         ├─► Build Backend Image
         │   - Dockerfile.backend
         │   - Python 3.11-slim
         │   - Install dependencies
         │   - Tag: gcr.io/PROJECT/health-triage-backend:SHA
         │
         ├─► Build Frontend Image
         │   - Dockerfile.frontend
         │   - Node 20-alpine (build)
         │   - Nginx-alpine (serve)
         │   - Tag: gcr.io/PROJECT/health-triage-frontend:SHA
         │
         ├─► Push to Container Registry
         │   - gcr.io/PROJECT/health-triage-backend:SHA
         │   - gcr.io/PROJECT/health-triage-frontend:SHA
         │
         ├─► Deploy Backend to Cloud Run
         │   - Service: health-triage-backend
         │   - Memory: 2Gi
         │   - CPU: 2
         │   - Max instances: 100
         │
         ├─► Deploy Frontend to Cloud Run
         │   - Service: health-triage-frontend
         │   - Memory: 512Mi
         │   - CPU: 1
         │   - Max instances: 50
         │
         └─► Test Deployment
             - Health check backend
             - Health check frontend
             - Verify CORS

  6. Services live at:
     - https://health-triage-backend-xxxxx.run.app
     - https://health-triage-frontend-xxxxx.run.app
```

---

## Local Development Setup

```
┌─────────────────────────────────────────────────────────────────┐
│              DOCKER COMPOSE LOCAL DEVELOPMENT                   │
└─────────────────────────────────────────────────────────────────┘

docker-compose.yml defines:

┌──────────────────────────────────────────────────────────────┐
│ Service: backend                                             │
├──────────────────────────────────────────────────────────────┤
│ Build: ./Dockerfile.backend                                  │
│ Port: 8000:8000                                              │
│ Environment:                                                 │
│   - GOOGLE_API_KEY=<from .env>                              │
│   - ENVIRONMENT=development                                  │
│   - DEBUG=true                                               │
│ Volumes:                                                     │
│   - ./app:/app/app (live reload)                            │
│   - ./health_triage.db:/app/health_triage.db               │
│ Health Check: curl http://localhost:8000/api/v1/health     │
│ Network: health-triage-network                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Service: frontend                                            │
├──────────────────────────────────────────────────────────────┤
│ Build: ./Dockerfile.frontend                                 │
│ Port: 80:80                                                  │
│ Environment:                                                 │
│   - REACT_APP_API_URL=http://localhost:8000                │
│ Depends On: backend                                          │
│ Health Check: wget http://localhost:80/health              │
│ Network: health-triage-network                              │
└──────────────────────────────────────────────────────────────┘

Access:
  Frontend: http://localhost
  Backend:  http://localhost:8000
  API Docs: http://localhost:8000/docs
```

---

## CORS Configuration

```
┌─────────────────────────────────────────────────────────────────┐
│                  CORS CONFIGURATION FLOW                        │
└─────────────────────────────────────────────────────────────────┘

LOCAL DEVELOPMENT:
┌──────────────────────────────────────────────────────────────┐
│ Frontend (http://localhost)                                  │
│   ├─ Makes request to /api/v1/analyze                       │
│   └─ Nginx proxies to http://backend:8000                   │
│                                                              │
│ Backend (http://localhost:8000)                             │
│   ├─ CORS configured for:                                   │
│   │  - http://localhost:3000                                │
│   │  - http://localhost:80                                  │
│   │  - http://127.0.0.1:3000                                │
│   │  - http://127.0.0.1:80                                  │
│   └─ Allow all origins in development mode                  │
│                                                              │
│ Nginx (http://localhost)                                    │
│   ├─ Serves static files                                    │
│   ├─ Proxies /api/* to backend                              │
│   └─ Adds CORS headers for local development                │
└──────────────────────────────────────────────────────────────┘

CLOUD RUN PRODUCTION:
┌──────────────────────────────────────────────────────────────┐
│ Frontend (https://frontend-xxxxx.run.app)                   │
│   ├─ Makes request to /api/v1/analyze                       │
│   └─ Nginx proxies to backend service URL                   │
│                                                              │
│ Backend (https://backend-xxxxx.run.app)                     │
│   ├─ CORS configured for:                                   │
│   │  - https://*.run.app (wildcard)                         │
│   │  - FRONTEND_URL env var                                 │
│   └─ Specific origins in production mode                    │
│                                                              │
│ Nginx (https://frontend-xxxxx.run.app)                      │
│   ├─ Serves static files                                    │
│   ├─ Proxies /api/* to backend service                      │
│   └─ Adds CORS headers for production                       │
└──────────────────────────────────────────────────────────────┘
```

---

## File Organization

```
healthcareHackathon/
│
├── Docker Configuration
│   ├── Dockerfile.backend          (Backend image)
│   ├── Dockerfile.frontend         (Frontend image)
│   ├── docker-compose.yml          (Local orchestration)
│   ├── nginx.conf                  (Web server config)
│   └── .dockerignore               (Build exclusions)
│
├── Cloud Deployment
│   ├── cloudbuild-cloudrun.yaml    (Cloud Build pipeline)
│   ├── cloudbuild.yaml             (Alternative K8s config)
│   └── .github/
│       └── workflows/
│           └── deploy-cloudrun.yml (GitHub Actions)
│
├── Configuration
│   ├── .env.example                (Environment template)
│   ├── .gitignore                  (Git exclusions)
│   └── frontend/
│       └── .env.production         (Frontend prod config)
│
├── Source Code
│   ├── app/
│   │   ├── main.py                 (FastAPI with CORS)
│   │   ├── config.py               (Configuration)
│   │   └── ...
│   └── frontend/
│       └── sevasetu_-ai-clinical-triage/
│           ├── vite.config.ts      (Build config)
│           ├── package.json        (Dependencies)
│           └── ...
│
└── Documentation
    ├── DEPLOYMENT_GUIDE.md         (Complete guide)
    ├── DOCKER_DEPLOYMENT.md        (Detailed guide)
    ├── DOCKER_QUICKSTART.md        (Quick start)
    ├── DEPLOYMENT_SUMMARY.md       (Summary)
    ├── QUICK_REFERENCE.md          (Reference card)
    ├── ARCHITECTURE_DEPLOYMENT.md  (This file)
    └── FILES_CREATED.txt           (File list)
```

---

## Environment Variables Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              ENVIRONMENT VARIABLES FLOW                         │
└─────────────────────────────────────────────────────────────────┘

LOCAL DEVELOPMENT:
  .env (local file)
    ├─ GOOGLE_API_KEY
    ├─ ENVIRONMENT=development
    ├─ DEBUG=true
    └─ FRONTEND_URL=http://localhost:80
         │
         ▼
  docker-compose.yml
    ├─ Backend container
    │   └─ Reads from .env
    └─ Frontend container
        └─ Reads from .env

CLOUD RUN PRODUCTION:
  Cloud Build Trigger
    ├─ Reads cloudbuild-cloudrun.yaml
    └─ Sets environment variables
         │
         ├─ GOOGLE_API_KEY (from Secret Manager)
         ├─ ENVIRONMENT=production
         ├─ DEBUG=false
         └─ FRONTEND_URL=https://frontend-xxxxx.run.app
              │
              ▼
         Cloud Run Service
         ├─ Backend service
         │   └─ Uses env vars
         └─ Frontend service
             └─ Uses env vars

GitHub Actions (Alternative):
  .github/workflows/deploy-cloudrun.yml
    ├─ Reads from GitHub Secrets
    │   ├─ GCP_PROJECT_ID
    │   ├─ GCP_SA_KEY
    │   └─ GOOGLE_API_KEY
    └─ Deploys to Cloud Run
        └─ Sets environment variables
```

---

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  SECURITY ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────┘

Secrets Management:
  ┌──────────────────────────────────────────────────────────┐
  │ Google Cloud Secret Manager                              │
  ├──────────────────────────────────────────────────────────┤
  │ Secret: google-api-key                                   │
  │   ├─ Stored securely                                     │
  │   ├─ Accessed only by Cloud Build                        │
  │   ├─ Never in code or .env                               │
  │   └─ Rotated regularly                                   │
  └──────────────────────────────────────────────────────────┘

Code Security:
  ┌──────────────────────────────────────────────────────────┐
  │ .gitignore                                               │
  ├──────────────────────────────────────────────────────────┤
  │ Excludes:                                                │
  │   ├─ .env (local secrets)                                │
  │   ├─ node_modules/ (dependencies)                        │
  │   ├─ __pycache__/ (Python cache)                         │
  │   ├─ .venv/ (Virtual environment)                        │
  │   └─ *.db (Database files)                               │
  └──────────────────────────────────────────────────────────┘

Network Security:
  ┌──────────────────────────────────────────────────────────┐
  │ CORS Configuration                                       │
  ├──────────────────────────────────────────────────────────┤
  │ Local:                                                   │
  │   ├─ Allow localhost origins                             │
  │   └─ Proxy through nginx                                 │
  │                                                          │
  │ Production:                                              │
  │   ├─ Allow https://*.run.app                             │
  │   ├─ Allow specific FRONTEND_URL                         │
  │   └─ HTTPS enforced                                      │
  └──────────────────────────────────────────────────────────┘

Container Security:
  ┌──────────────────────────────────────────────────────────┐
  │ Docker Images                                            │
  ├──────────────────────────────────────────────────────────┤
  │ Backend:                                                 │
  │   ├─ Multi-stage build (smaller image)                   │
  │   ├─ Python 3.11-slim base                               │
  │   └─ No unnecessary dependencies                         │
  │                                                          │
  │ Frontend:                                                │
  │   ├─ Multi-stage build                                   │
  │   ├─ Node 20-alpine for build                            │
  │   ├─ Nginx-alpine for serving                            │
  │   └─ No build tools in final image                       │
  └──────────────────────────────────────────────────────────┘
```

---

## Monitoring & Logging

```
┌─────────────────────────────────────────────────────────────────┐
│              MONITORING & LOGGING ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────┘

Local Development:
  docker-compose logs -f
    ├─ Backend logs
    │   └─ FastAPI output
    └─ Frontend logs
        └─ Nginx output

Cloud Build:
  Cloud Build Logs
    ├─ Build steps
    ├─ Docker build output
    ├─ Push to registry
    └─ Deployment status

Cloud Run:
  Cloud Logging
    ├─ Backend service logs
    │   ├─ Request logs
    │   ├─ Error logs
    │   └─ Performance metrics
    └─ Frontend service logs
        ├─ Access logs
        ├─ Error logs
        └─ Performance metrics

Health Checks:
  Backend:
    └─ GET /api/v1/health
        └─ Monitored by Cloud Run

  Frontend:
    └─ GET /health
        └─ Monitored by Cloud Run
```

---

## Scaling & Performance

```
┌─────────────────────────────────────────────────────────────────┐
│            SCALING & PERFORMANCE CONFIGURATION                  │
└─────────────────────────────────────────────────────────────────┘

Backend Service:
  ┌──────────────────────────────────────────────────────────┐
  │ Cloud Run Configuration                                  │
  ├──────────────────────────────────────────────────────────┤
  │ Memory: 2Gi                                              │
  │ CPU: 2                                                   │
  │ Max Instances: 100                                       │
  │ Timeout: 3600 seconds (1 hour)                           │
  │ Concurrency: Default (80)                                │
  │                                                          │
  │ Scaling:                                                 │
  │   ├─ Automatic based on traffic                          │
  │   ├─ Min instances: 0 (cold start)                       │
  │   └─ Max instances: 100                                  │
  └──────────────────────────────────────────────────────────┘

Frontend Service:
  ┌──────────────────────────────────────────────────────────┐
  │ Cloud Run Configuration                                  │
  ├──────────────────────────────────────────────────────────┤
  │ Memory: 512Mi                                            │
  │ CPU: 1                                                   │
  │ Max Instances: 50                                        │
  │ Timeout: 300 seconds (5 minutes)                         │
  │ Concurrency: Default (80)                                │
  │                                                          │
  │ Scaling:                                                 │
  │   ├─ Automatic based on traffic                          │
  │   ├─ Min instances: 0 (cold start)                       │
  │   └─ Max instances: 50                                   │
  └──────────────────────────────────────────────────────────┘

Performance Optimization:
  ┌──────────────────────────────────────────────────────────┐
  │ Frontend (Nginx)                                         │
  ├──────────────────────────────────────────────────────────┤
  │ ├─ Gzip compression enabled                              │
  │ ├─ Static asset caching (1 year)                         │
  │ ├─ HTTP/2 support                                        │
  │ └─ Security headers                                      │
  └──────────────────────────────────────────────────────────┘
```

---

## Disaster Recovery

```
┌─────────────────────────────────────────────────────────────────┐
│            DISASTER RECOVERY & BACKUP STRATEGY                  │
└─────────────────────────────────────────────────────────────────┘

Code Backup:
  GitHub Repository
    ├─ Version control
    ├─ Commit history
    └─ Branch management

Database Backup:
  Local Development:
    └─ health_triage.db (SQLite)

  Production:
    ├─ Recommended: Cloud SQL
    ├─ Automated backups
    └─ Point-in-time recovery

Container Images:
  Container Registry (gcr.io)
    ├─ All built images stored
    ├─ Tagged by commit SHA
    ├─ Latest tag available
    └─ Can rollback to previous version

Rollback Strategy:
  Cloud Run:
    ├─ View previous revisions
    ├─ Route traffic to previous version
    └─ Automatic rollback on health check failure
```

---

## Deployment Checklist

```
┌─────────────────────────────────────────────────────────────────┐
│              DEPLOYMENT READINESS CHECKLIST                     │
└─────────────────────────────────────────────────────────────────┘

Pre-Deployment:
  ☐ Docker files created and tested
  ☐ docker-compose.yml working locally
  ☐ .gitignore updated
  ☐ .env.example created
  ☐ CORS configured
  ☐ Health checks working
  ☐ All tests passing

GitHub:
  ☐ Repository created
  ☐ Code committed
  ☐ Pushed to main branch
  ☐ .env NOT committed
  ☐ node_modules/ NOT committed
  ☐ __pycache__/ NOT committed

Google Cloud:
  ☐ Project created
  ☐ APIs enabled
  ☐ API key stored in Secret Manager
  ☐ Cloud Build trigger created
  ☐ GitHub connected

Deployment:
  ☐ Cloud Build triggered
  ☐ Backend image built
  ☐ Frontend image built
  ☐ Images pushed to registry
  ☐ Backend deployed to Cloud Run
  ☐ Frontend deployed to Cloud Run

Post-Deployment:
  ☐ Backend health check passing
  ☐ Frontend accessible
  ☐ CORS working
  ☐ API endpoints responding
  ☐ Logs accessible
  ☐ Monitoring configured
```

---

**Created**: November 22, 2024
**Project**: Healthcare Hackathon - AI Clinical Triage
**Architecture**: Docker + GitHub + Cloud Build + Cloud Run
