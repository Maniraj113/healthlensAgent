# Setup Guide - Health Triage Multi-Agent System

Complete setup instructions for the backend + multi-agent system.

## Prerequisites

- Python 3.10 or higher
- pip package manager
- Google API key for Gemini

## Installation Steps

### 1. Clone or Navigate to Project

```bash
cd c:/Users/cmani/OneDrive/Desktop/Learning/healthcareHackathon
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Google ADK (Agent Development Kit)
- FastAPI + Uvicorn
- Pydantic + SQLModel
- Image processing libraries (PIL, OpenCV)
- All other dependencies

### 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Google API key:

```env
GOOGLE_API_KEY=your_actual_gemini_api_key_here
GOOGLE_PROJECT_ID=your_project_id  # Optional

APP_NAME=health_triage_system
ENVIRONMENT=development
DEBUG=True

DATABASE_URL=sqlite:///./health_triage.db

HOST=0.0.0.0
PORT=8000
```

### 6. Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## Running the Application

### Option 1: Using the run script (Recommended)

```bash
python run.py
```

### Option 2: Using uvicorn directly

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Using the main module

```bash
python -m app.main
```

## Verify Installation

Once the server is running, visit:

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/v1/health

## Testing the API

### Using the test script:

```bash
python test_api.py
```

### Using curl:

**Health Check:**
```bash
curl http://localhost:8000/api/v1/health
```

**Analyze Patient (Simple):**
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vitals": {
      "bp_systolic": 150,
      "bp_diastolic": 95,
      "random_glucose": 110,
      "heart_rate": 88,
      "spo2": 97
    },
    "symptoms": ["headache", "swelling"],
    "age": 28,
    "sex": "female",
    "pregnant": true,
    "gestational_weeks": 32,
    "worker_id": "CHW001",
    "patient_id": "PAT001",
    "language": "english"
  }'
```

### Using Python requests:

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "vitals": {
            "bp_systolic": 150,
            "bp_diastolic": 95,
            "random_glucose": 110,
            "heart_rate": 88,
            "spo2": 97
        },
        "symptoms": ["headache", "swelling"],
        "age": 28,
        "sex": "female",
        "pregnant": True,
        "gestational_weeks": 32,
        "worker_id": "CHW001",
        "patient_id": "PAT001",
        "language": "english"
    }
)

print(response.json())
```

## Project Structure

```
healthcareHackathon/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── models/                 # Pydantic schemas
│   │   ├── input_models.py     # Input data models
│   │   ├── output_models.py    # Output data models
│   │   └── db_models.py        # Database models
│   ├── agents/                 # ADK Agents
│   │   ├── intake_agent.py     # Validates input
│   │   ├── image_agent.py      # Analyzes images
│   │   ├── clinical_agent.py   # Computes risks
│   │   ├── action_agent.py     # Generates advice
│   │   └── sync_agent.py       # Handles sync
│   ├── tools/                  # Agent tools
│   │   ├── validation_tools.py
│   │   ├── image_tools.py
│   │   └── db_tools.py
│   ├── core/                   # Business logic
│   │   ├── medical_rules.py    # Clinical rules
│   │   ├── risk_calculator.py  # Risk computation
│   │   └── nlg_templates.py    # Multilingual text
│   ├── orchestration/          # ADK workflow
│   │   └── triage_workflow.py  # Main workflow
│   ├── database/               # Database layer
│   │   └── session.py
│   └── api/                    # API routes
│       └── routes.py
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
├── test_api.py
└── README.md
```

## Troubleshooting

### Issue: Module not found errors

**Solution:** Make sure you're in the virtual environment and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Database errors

**Solution:** Delete the database file and restart:
```bash
rm health_triage.db
python run.py
```

### Issue: Google API key errors

**Solution:** Verify your API key is correct in `.env`:
```bash
cat .env | grep GOOGLE_API_KEY
```

### Issue: Port already in use

**Solution:** Change the port in `.env` or kill the process using port 8000:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## Development

### Format code:
```bash
black app/
```

### Run tests:
```bash
pytest
```

### Check logs:
The application logs to stdout. For production, configure proper logging.

## Production Deployment

For production deployment:

1. Set `ENVIRONMENT=production` in `.env`
2. Set `DEBUG=False`
3. Use a production database (PostgreSQL recommended)
4. Configure proper CORS origins in `app/main.py`
5. Use a production ASGI server (Gunicorn + Uvicorn workers)
6. Set up proper logging and monitoring
7. Use environment variables for secrets (not `.env` file)

Example production command:
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Next Steps

1. ✅ Backend is ready
2. 🔄 Integrate with React frontend
3. 🔄 Deploy to cloud (Google Cloud Run, AWS, etc.)
4. 🔄 Add authentication/authorization
5. 🔄 Implement actual vision models for image analysis
6. 🔄 Add monitoring and analytics

## Support

For issues or questions:
- Check the API documentation at `/docs`
- Review the code comments
- Check logs for error messages
