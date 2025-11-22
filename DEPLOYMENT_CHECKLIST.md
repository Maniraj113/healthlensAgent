# Deployment Checklist

## Pre-Deployment

### ✅ Code Quality
- [ ] All agents tested individually
- [ ] Integration tests passing
- [ ] Error handling verified
- [ ] Logging configured
- [ ] Code formatted (black)
- [ ] Type hints complete

### ✅ Configuration
- [ ] Environment variables set
- [ ] API keys secured (not in code)
- [ ] Database URL configured
- [ ] CORS origins restricted
- [ ] Debug mode disabled
- [ ] Proper logging level set

### ✅ Security
- [ ] API authentication implemented
- [ ] Rate limiting configured
- [ ] Input validation tested
- [ ] SQL injection prevention verified
- [ ] XSS protection enabled
- [ ] HTTPS/TLS configured
- [ ] Secrets in secure vault

### ✅ Database
- [ ] Production database setup (PostgreSQL)
- [ ] Migrations tested
- [ ] Indexes created
- [ ] Backup strategy defined
- [ ] Connection pooling configured

### ✅ Performance
- [ ] Load testing completed
- [ ] Response times acceptable (<1s)
- [ ] Memory usage optimized
- [ ] Database queries optimized
- [ ] Caching strategy implemented

## Deployment Steps

### Option 1: Docker Deployment

#### 1. Create Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Build Image
```bash
docker build -t health-triage:latest .
```

#### 3. Test Locally
```bash
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key \
  health-triage:latest
```

#### 4. Push to Registry
```bash
docker tag health-triage:latest gcr.io/PROJECT_ID/health-triage:latest
docker push gcr.io/PROJECT_ID/health-triage:latest
```

### Option 2: Google Cloud Run

#### 1. Install Google Cloud SDK
```bash
gcloud init
```

#### 2. Deploy
```bash
gcloud run deploy health-triage \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=your_key \
  --set-env-vars DATABASE_URL=postgresql://... \
  --memory 1Gi \
  --cpu 2 \
  --max-instances 10
```

#### 3. Verify
```bash
gcloud run services describe health-triage
```

### Option 3: AWS ECS/Fargate

#### 1. Create ECR Repository
```bash
aws ecr create-repository --repository-name health-triage
```

#### 2. Build and Push
```bash
aws ecr get-login-password | docker login --username AWS --password-stdin ECR_URL
docker build -t health-triage .
docker tag health-triage:latest ECR_URL/health-triage:latest
docker push ECR_URL/health-triage:latest
```

#### 3. Create Task Definition
```json
{
  "family": "health-triage",
  "containerDefinitions": [{
    "name": "health-triage",
    "image": "ECR_URL/health-triage:latest",
    "memory": 1024,
    "cpu": 512,
    "portMappings": [{
      "containerPort": 8000,
      "protocol": "tcp"
    }],
    "environment": [
      {"name": "GOOGLE_API_KEY", "value": "your_key"}
    ]
  }]
}
```

#### 4. Create Service
```bash
aws ecs create-service \
  --cluster health-cluster \
  --service-name health-triage \
  --task-definition health-triage \
  --desired-count 2 \
  --launch-type FARGATE
```

### Option 4: Traditional Server (Ubuntu)

#### 1. Setup Server
```bash
sudo apt update
sudo apt install python3.10 python3-pip nginx
```

#### 2. Install Application
```bash
cd /opt
git clone YOUR_REPO
cd healthcareHackathon
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. Create Systemd Service
```ini
# /etc/systemd/system/health-triage.service
[Unit]
Description=Health Triage API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/healthcareHackathon
Environment="PATH=/opt/healthcareHackathon/.venv/bin"
EnvironmentFile=/opt/healthcareHackathon/.env
ExecStart=/opt/healthcareHackathon/.venv/bin/gunicorn \
  app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
```

#### 4. Configure Nginx
```nginx
# /etc/nginx/sites-available/health-triage
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### 5. Start Services
```bash
sudo systemctl enable health-triage
sudo systemctl start health-triage
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## Post-Deployment

### ✅ Verification
- [ ] Health endpoint responding
- [ ] API documentation accessible
- [ ] Sample request succeeds
- [ ] Database connection working
- [ ] Logs being generated
- [ ] Metrics being collected

### ✅ Monitoring Setup
- [ ] Uptime monitoring configured
- [ ] Error tracking enabled (Sentry)
- [ ] Performance monitoring active
- [ ] Log aggregation setup
- [ ] Alerts configured
- [ ] Dashboard created

### ✅ Documentation
- [ ] API documentation published
- [ ] Deployment guide updated
- [ ] Runbook created
- [ ] Contact information shared
- [ ] SLA defined

### ✅ Backup & Recovery
- [ ] Database backups automated
- [ ] Backup restoration tested
- [ ] Disaster recovery plan documented
- [ ] Rollback procedure tested

## Environment Variables (Production)

```bash
# Required
GOOGLE_API_KEY=your_production_key
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Application
APP_NAME=health_triage_system
ENVIRONMENT=production
DEBUG=False

# Server
HOST=0.0.0.0
PORT=8000

# Security
SECRET_KEY=your_secret_key
ALLOWED_ORIGINS=https://your-frontend.com

# Database
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
```

## Performance Tuning

### Database
```python
# Connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

### Gunicorn Workers
```bash
# Calculate workers: (2 x CPU cores) + 1
gunicorn app.main:app \
  --workers 9 \
  --worker-class uvicorn.workers.UvicornWorker \
  --worker-connections 1000 \
  --timeout 30 \
  --keep-alive 5
```

### Caching
```python
# Add Redis caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="health-triage")
```

## Monitoring Endpoints

### Health Check
```bash
curl https://your-domain.com/api/v1/health
```

### Metrics (if Prometheus enabled)
```bash
curl https://your-domain.com/metrics
```

## Rollback Procedure

### Docker/Cloud Run
```bash
# Rollback to previous version
gcloud run services update-traffic health-triage \
  --to-revisions=PREVIOUS_REVISION=100
```

### Traditional Server
```bash
# Stop service
sudo systemctl stop health-triage

# Restore previous version
cd /opt/healthcareHackathon
git checkout PREVIOUS_COMMIT

# Restart
sudo systemctl start health-triage
```

## Troubleshooting

### High Memory Usage
- Check for memory leaks
- Reduce worker count
- Enable connection pooling
- Add caching layer

### Slow Response Times
- Check database query performance
- Add database indexes
- Enable caching
- Optimize image processing

### Database Connection Errors
- Check connection pool settings
- Verify database credentials
- Check network connectivity
- Review firewall rules

### API Errors
- Check logs: `docker logs CONTAINER_ID`
- Verify environment variables
- Test database connection
- Check API key validity

## Support Contacts

- **Technical Lead**: [email]
- **DevOps**: [email]
- **On-Call**: [phone]
- **Escalation**: [email]

## Useful Commands

### View Logs
```bash
# Docker
docker logs -f CONTAINER_ID

# Cloud Run
gcloud run logs read health-triage --limit 100

# Systemd
sudo journalctl -u health-triage -f
```

### Database Backup
```bash
# PostgreSQL
pg_dump -h HOST -U USER DATABASE > backup.sql

# Restore
psql -h HOST -U USER DATABASE < backup.sql
```

### Check Resource Usage
```bash
# Docker
docker stats CONTAINER_ID

# Server
htop
df -h
free -m
```

## Success Criteria

- [ ] API responding with <500ms latency
- [ ] 99.9% uptime
- [ ] Zero critical errors
- [ ] Database backups running
- [ ] Monitoring alerts working
- [ ] Documentation complete
- [ ] Team trained

---

**Deployment Complete! 🚀**
