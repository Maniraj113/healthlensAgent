# Quick Start Guide - 5 Minutes to Running

## Prerequisites
- Python 3.10+
- Google API key for Gemini

## Setup (3 steps)

### 1. Install Dependencies
```bash
cd healthcareHackathon
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
```

### 2. Configure API Key
Create `.env` file:
```bash
cp .env.example .env
```

Edit `.env` and add your key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

Get API key: https://makersuite.google.com/app/apikey

### 3. Run Server
```bash
python run.py
```

Server starts at: http://localhost:8000

## Test It

### Option 1: Interactive Docs
Open browser: http://localhost:8000/docs

Click "POST /api/v1/analyze" → "Try it out" → Use example payload → Execute

### Option 2: Test Script
```bash
python test_api.py
```

### Option 3: Curl
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

## What You Get

```json
{
  "visit_id": "v_abc123",
  "triage_level": "urgent",
  "summary_text": "URGENT: High maternal risk...",
  "risk_scores": {
    "maternal": {"score": 88, "level": "urgent"},
    "anemia": {"score": 15, "level": "low"},
    "sugar": {"score": 10, "level": "low"}
  },
  "action_checklist": [
    "Arrange immediate transport to PHC",
    "Do NOT allow patient to walk or exert",
    "Accompany patient to PHC"
  ],
  "voice_text": "Urgent medical attention required..."
}
```

## Project Structure

```
app/
├── agents/          # 5 ADK agents
├── core/            # Medical rules + NLG
├── models/          # Data schemas
├── orchestration/   # Workflow
├── api/             # FastAPI routes
└── main.py          # Application entry
```

## Key Files

- `app/main.py` - FastAPI app
- `app/orchestration/triage_workflow.py` - Main workflow
- `app/core/medical_rules.py` - Clinical decision rules
- `app/agents/` - All 5 agents
- `run.py` - Server launcher
- `test_api.py` - Test script

## Next Steps

1. ✅ Backend running
2. 📖 Read `ARCHITECTURE.md` for details
3. 📖 Read `API_EXAMPLES.md` for more examples
4. 🔧 Integrate with React frontend
5. 🚀 Deploy to cloud

## Troubleshooting

**Module not found?**
```bash
pip install -r requirements.txt
```

**API key error?**
Check `.env` file has correct `GOOGLE_API_KEY`

**Port in use?**
Change `PORT=8001` in `.env`

**Database error?**
```bash
rm health_triage.db
python run.py
```

## Documentation

- 📘 `README.md` - Overview
- 🏗️ `ARCHITECTURE.md` - System design
- ⚙️ `SETUP.md` - Detailed setup
- 📚 `API_EXAMPLES.md` - API examples
- 🚀 `QUICKSTART.md` - This file

## Support

Check `/docs` endpoint for interactive API documentation.
