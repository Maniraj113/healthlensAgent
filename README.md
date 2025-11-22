# Health Triage Multi-Agent System

Production-ready backend + agentic AI system using Google Agent Development Kit (ADK) for frontline health workers in rural India.

## Architecture

### Multi-Agent System
- **Intake Agent**: Validates and normalizes vitals/symptoms
- **Image Interpretation Agent**: Analyzes medical photos (anemia, edema, malnutrition)
- **Clinical Reasoning Agent**: Computes risk scores using medical rules
- **Action Planner Agent**: Generates multilingual advice and action plans
- **Follow-Up/Sync Agent**: Handles offline-first data synchronization

### Tech Stack
- **Framework**: Google ADK (Agent Development Kit)
- **API**: FastAPI
- **Database**: SQLite with SQLModel
- **AI Model**: Gemini 2.0 Flash
- **Image Processing**: PIL, OpenCV

## Project Structure

```
healthcareHackathon/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── models/                 # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── input_models.py
│   │   ├── output_models.py
│   │   └── db_models.py
│   ├── agents/                 # ADK Agents
│   │   ├── __init__.py
│   │   ├── intake_agent.py
│   │   ├── image_agent.py
│   │   ├── clinical_agent.py
│   │   ├── action_agent.py
│   │   └── sync_agent.py
│   ├── tools/                  # Agent tools
│   │   ├── __init__.py
│   │   ├── validation_tools.py
│   │   ├── image_tools.py
│   │   └── db_tools.py
│   ├── core/                   # Business logic
│   │   ├── __init__.py
│   │   ├── medical_rules.py
│   │   ├── risk_calculator.py
│   │   └── nlg_templates.py
│   ├── orchestration/          # ADK workflow
│   │   ├── __init__.py
│   │   └── triage_workflow.py
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   └── session.py
│   └── api/                    # API routes
│       ├── __init__.py
│       └── routes.py
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

1. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

## Usage

### Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Endpoints:

**POST /api/v1/analyze**
- Accepts patient vitals, symptoms, and images
- Returns risk scores, triage level, and action plan

**POST /api/v1/sync**
- Syncs offline visits to server
- Returns authoritative results

**GET /api/v1/visit/{visit_id}**
- Retrieves stored visit data

## Medical Risk Scoring

### Anemia
- Pallor detected: +40
- Heart rate > 100: +10
- Fatigue symptom: +10
- Pregnant multiplier: 1.2
- Levels: 0-30 (low), 31-60 (moderate), >60 (high)

### Maternal Risk
- BP ≥140/90: +60
- Edema visible: +20
- Headache: +10
- Decreased fetal movement: +30
- Levels: >70 (urgent high risk)

### Sugar Risk
- Glucose ≥200: high
- Glucose 140-199: moderate
- Glucose <140: low

### Nutrition
- Malnutrition flag: moderate/high

## Offline-First Support

The system includes offline fallback logic in the Intake Agent that runs minimal rule-based triage when network is unavailable.

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black app/
```

## License

Apache 2.0
