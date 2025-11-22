# Architecture Documentation - Health Triage Multi-Agent System

## System Overview

This is a production-ready backend system using **Google Agent Development Kit (ADK)** to support frontline health workers in rural India for early health risk detection without lab infrastructure.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         React Frontend                          │
│                    (Mobile/Web Interface)                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/JSON
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Backend                          │
│                     (app/main.py + routes)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ADK Orchestration Layer                       │
│                  (TriageWorkflow - Sequential)                  │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Intake     │→ │    Image     │→ │  Clinical    │         │
│  │    Agent     │  │    Agent     │  │    Agent     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│         │                                     │                 │
│         ▼                                     ▼                 │
│  ┌──────────────┐                    ┌──────────────┐         │
│  │   Action     │                    │     Sync     │         │
│  │    Agent     │                    │    Agent     │         │
│  └──────────────┘                    └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                       │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  Medical Rules   │  │ Risk Calculator  │  │ NLG Templates│ │
│  │     Engine       │  │                  │  │  (i18n)      │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer (SQLite)                        │
│                    (Visit Records Storage)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Multi-Agent System Design

### Agent 1: Intake Agent
**File:** `app/agents/intake_agent.py`

**Purpose:**
- Validates input payload (vitals, symptoms, metadata)
- Normalizes symptoms into standardized flags
- Checks mandatory fields
- Computes derived flags (has_images, has_maternal_risk_factors, etc.)
- Runs offline triage if network unavailable

**Tools:**
- `validate_and_normalize_input()`: Validates vitals and normalizes data
- `run_offline_triage()`: Minimal rule-based triage for offline mode

**Input:** Raw `InputPayload` from frontend
**Output:** `NormalizedContext` with validation status and flags

---

### Agent 2: Image Interpretation Agent
**File:** `app/agents/image_agent.py`

**Purpose:**
- Analyzes medical images (conjunctiva, swelling, child arm, skin)
- Detects clinical signs: pallor, edema, malnutrition, infection, dehydration
- Returns binary flags with confidence scores

**Tools:**
- `process_medical_images()`: Analyzes all available images

**Image Analysis Functions:**
- `analyze_conjunctiva_image()`: Detects pallor (anemia)
- `analyze_swelling_image()`: Detects edema (maternal risk)
- `analyze_child_arm_image()`: Detects malnutrition (MUAC)
- `analyze_skin_image()`: Detects infection and dehydration

**Input:** Camera inputs from `NormalizedContext`
**Output:** `ImageEvidence` with detection flags and confidence

**Note:** Current implementation uses stub/heuristic logic. In production, replace with:
- Fine-tuned Gemini Vision models
- Custom CNN models trained on medical images
- Integration with medical image analysis APIs

---

### Agent 3: Clinical Reasoning Agent
**File:** `app/agents/clinical_agent.py`

**Purpose:**
- Applies evidence-based medical decision rules
- Computes risk scores for 5 domains:
  - Anemia
  - Maternal health
  - Diabetes/sugar
  - Malnutrition
  - Infection
- Determines overall triage level
- Generates reasoning trace (explainability)

**Tools:**
- `calculate_risk_scores()`: Runs complete medical rule engine

**Medical Rules Engine:**
Located in `app/core/medical_rules.py`

**Anemia Rules:**
- Pallor detected: +40 points
- Heart rate > 100: +10 points
- Fatigue: +10 points
- Dizziness: +5 points
- Breathlessness: +10 points
- Pregnant multiplier: ×1.2
- Levels: 0-30 (low), 31-60 (moderate), >60 (high)

**Maternal Risk Rules:**
- BP ≥140/90: +60 points
- Edema visible: +20 points
- Headache: +10 points
- Decreased fetal movement: +30 points
- Abdominal pain: +15 points
- Levels: 0-40 (low), 41-70 (moderate), >70 (urgent)

**Sugar Risk Rules:**
- Glucose ≥200: high (score 80)
- Glucose 140-199: moderate (score 50)
- Glucose <140: low (score 10)

**Triage Priority:**
maternal > anemia > infection > sugar > nutrition

**Input:** `NormalizedContext` + `ImageEvidence`
**Output:** `ReasoningResult` with risk scores, triage level, reasoning trace

---

### Agent 4: Action Planner / Communicator Agent
**File:** `app/agents/action_agent.py`

**Purpose:**
- Converts clinical reasoning into patient-facing advice
- Generates plain-language summaries
- Creates actionable checklists
- Produces emergency warning signs
- Localizes all text to patient's language

**Tools:**
- `generate_patient_communication()`: Creates complete action plan

**Supported Languages:**
- English
- Hindi (हिंदी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Bengali (বাংলা)

**NLG Templates:**
Located in `app/core/nlg_templates.py`

**Output Components:**
- `summary_text`: Clinical summary in plain language
- `action_checklist`: Specific steps for health worker
- `emergency_signs`: Warning signs to watch for
- `voice_text`: Simplified text for TTS

**Input:** `ReasoningResult` + language preference
**Output:** `ActionPlan` with multilingual advice

---

### Agent 5: Follow-Up / Sync Agent
**File:** `app/agents/sync_agent.py`

**Purpose:**
- Persists complete visit record to database
- Marks visits as synced
- Supports offline-to-online synchronization
- Maintains audit trail

**Tools:**
- `save_visit_to_database()`: Stores complete visit record
- `mark_visit_synced()`: Updates sync status

**Database Schema:**
```sql
CREATE TABLE visits (
    id INTEGER PRIMARY KEY,
    visit_id TEXT UNIQUE,
    patient_id TEXT,
    worker_id TEXT,
    timestamp DATETIME,
    input_payload JSON,
    risk_scores JSON,
    image_evidence JSON,
    reasoning_trace JSON,
    triage_level TEXT,
    primary_concern TEXT,
    summary_text TEXT,
    action_checklist JSON,
    voice_text TEXT,
    language TEXT,
    offline_processed BOOLEAN,
    synced BOOLEAN
);
```

**Input:** Complete visit data from all agents
**Output:** Sync status

---

## Workflow Orchestration

**File:** `app/orchestration/triage_workflow.py`

### Sequential Workflow Steps:

1. **Intake** → Validates input, creates normalized context
2. **Image Analysis** → Extracts evidence from photos (if present)
3. **Clinical Reasoning** → Computes risk scores using medical rules
4. **Action Planning** → Generates multilingual advice
5. **Sync** → Stores results in database

### Conditional Logic:

- If `offline_mode=True`: Skip to offline triage (simple rules)
- If `has_images=False`: Skip image analysis, use empty evidence
- If validation fails: Return error response immediately

### Error Handling:

- Validation errors: Return structured error with field details
- Agent failures: Log error, return safe fallback response
- Database errors: Continue workflow, mark as unsynced

---

## Data Models

### Input Models (`app/models/input_models.py`)

**InputPayload:**
- `vitals`: VitalsInput (BP, glucose, temp, HR, SpO2)
- `symptoms`: List[str]
- `camera_inputs`: CameraInputs (base64 images)
- `age`, `sex`, `pregnant`, `gestational_weeks`
- `worker_id`, `patient_id`, `language`
- `offline_mode`: bool

**NormalizedContext:**
- Original payload
- Validation status and errors
- Derived flags (has_images, has_maternal_risk_factors, etc.)
- Normalized vitals
- Symptom flags dictionary

### Output Models (`app/models/output_models.py`)

**FinalResult:**
- `visit_id`: Unique identifier
- `risk_scores`: RiskScores (all domains)
- `triage_level`: TriageLevel (low/moderate/high/urgent)
- `summary_text`: Plain language summary
- `action_checklist`: List of action items
- `emergency_signs`: Warning signs
- `voice_text`: TTS text
- `reasons`: List[ReasoningFact] (explainability)
- `image_evidence`: ImageEvidence (optional)
- `timestamp`: ISO datetime
- `offline_processed`: bool

---

## API Endpoints

### POST /api/v1/analyze
**Purpose:** Main triage endpoint
**Input:** InputPayload
**Output:** FinalResult
**Process:** Runs complete multi-agent workflow

### POST /api/v1/sync
**Purpose:** Sync offline visits
**Input:** List[InputPayload]
**Output:** Sync results summary

### GET /api/v1/visit/{visit_id}
**Purpose:** Retrieve stored visit
**Output:** Complete visit record

### GET /api/v1/visits/unsynced
**Purpose:** Get unsynced visits
**Query Params:** worker_id (optional)
**Output:** List of unsynced visits

### GET /api/v1/health
**Purpose:** Health check
**Output:** Service status

---

## Technology Stack

### Core Framework
- **Google ADK**: Multi-agent orchestration
- **FastAPI**: REST API framework
- **Pydantic**: Data validation
- **SQLModel**: ORM with SQLAlchemy

### AI/ML
- **Gemini 2.0 Flash**: LLM for agent reasoning
- **PIL + OpenCV**: Image processing (stub)
- **NumPy**: Numerical operations

### Database
- **SQLite**: Development database
- **PostgreSQL**: Recommended for production

### Deployment
- **Uvicorn**: ASGI server
- **Docker**: Containerization (future)
- **Google Cloud Run**: Recommended deployment target

---

## Security Considerations

### Current Implementation:
- API key stored in environment variables
- CORS enabled for all origins (development)
- No authentication/authorization

### Production Requirements:
1. **Authentication:** JWT tokens, OAuth2
2. **Authorization:** Role-based access control (RBAC)
3. **Data Encryption:** TLS/SSL, encrypted database fields
4. **API Rate Limiting:** Prevent abuse
5. **Input Validation:** Strict schema validation (already implemented)
6. **Audit Logging:** Track all access and modifications
7. **CORS:** Restrict to specific frontend domains
8. **Secrets Management:** Use Google Secret Manager, AWS Secrets Manager

---

## Scalability & Performance

### Current Capacity:
- Single-threaded async processing
- SQLite (suitable for <100 concurrent users)
- In-memory session state

### Production Scaling:

**Horizontal Scaling:**
- Deploy multiple FastAPI instances behind load balancer
- Use Redis for session state
- PostgreSQL with connection pooling

**Vertical Scaling:**
- Increase worker processes (Gunicorn)
- Optimize database queries with indexes
- Cache frequent queries (Redis)

**Database Optimization:**
- Add indexes on `patient_id`, `worker_id`, `timestamp`
- Partition large tables by date
- Archive old visits

**Caching Strategy:**
- Cache NLG templates
- Cache medical rule configurations
- Use CDN for static assets

---

## Monitoring & Observability

### Recommended Tools:
- **Logging:** Structured JSON logs (Python logging)
- **Metrics:** Prometheus + Grafana
- **Tracing:** OpenTelemetry
- **Error Tracking:** Sentry
- **Uptime Monitoring:** UptimeRobot, Pingdom

### Key Metrics to Track:
- Request latency (p50, p95, p99)
- Error rate by endpoint
- Triage level distribution
- Agent execution time
- Database query performance
- Offline vs online processing ratio

---

## Testing Strategy

### Unit Tests:
- Medical rules engine
- Risk calculator
- Validation tools
- Image analysis functions

### Integration Tests:
- Agent workflows
- API endpoints
- Database operations

### End-to-End Tests:
- Complete triage workflow
- Offline mode
- Sync operations

### Test Command:
```bash
pytest tests/ -v --cov=app
```

---

## Deployment Guide

### Local Development:
```bash
python run.py
```

### Docker Deployment:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Google Cloud Run:
```bash
gcloud run deploy health-triage \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Future Enhancements

### Phase 2:
- [ ] Real vision models for image analysis
- [ ] Voice input support (speech-to-text)
- [ ] Voice output (text-to-speech)
- [ ] Offline mobile app with local ML models
- [ ] Real-time vital signs integration (Bluetooth devices)

### Phase 3:
- [ ] Predictive analytics (risk trends over time)
- [ ] Population health dashboard
- [ ] Integration with national health systems
- [ ] Telemedicine video consultation
- [ ] Automated follow-up reminders

### Phase 4:
- [ ] Federated learning for privacy-preserving model training
- [ ] Advanced explainable AI (SHAP, LIME)
- [ ] Clinical decision support system (CDSS)
- [ ] Integration with electronic health records (EHR)

---

## References

### Medical Guidelines:
- WHO Integrated Management of Childhood Illness (IMCI)
- Indian National Rural Health Mission (NRHM) protocols
- WHO Antenatal Care Guidelines
- Indian Diabetes Guidelines

### Technical Documentation:
- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

---

## License

Apache 2.0

## Contributors

Built for healthcare hackathon - supporting frontline health workers in rural India.
